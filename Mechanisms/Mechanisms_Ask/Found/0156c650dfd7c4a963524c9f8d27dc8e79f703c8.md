---
name: epic-to-feature-specs
description: Break a large epic doc into implementation-ready feature specs (team contracts) and optionally further into sub-specs (one shippable PR per sub-spec, sized for an AI coding harness like hoangsa). Use whenever the user says "break down epic", "split epic", "decompose epic", "write feature specs", "write sub-specs", "epic → spec", "epic to stories", "make this epic AI-codeable", "spec out this epic", Vietnamese equivalents ("chia epic", "viết spec", "tách epic thành spec"), or complains that stories are too small and epics are too big for AI coding agents. Also trigger when the user uploads an epic doc and asks how to hand it to engineering, or when discussing FE/BE handoff contracts, team-split implementation planning, SMART decomposition, sub-spec authoring, Notion task tracking, or Plan Split recommendations for hoangsa. Adapts to different user personas — non-tech PMs delegating to engineering teams get guided FE/BE splits with handoff contracts, while technical users get flexible splitting options (by service, domain, layer, or custom). Optionally integrates UI designs from Figma or Pencil to ensure FE specs match design system components and screen flows. Optionally writes sub-specs into Notion via the Notion MCP. Produce a small number (default 3, up to 5) of feature specs per epic, each with a TypeScript handoff contract and acceptance criteria, then optionally decompose each feat spec into 3–5 sub-specs (cap `.A` through `.E`) — the output is designed to be fed directly to AI coding agents so teams can ship in parallel.
---

# Epic → Feature Specs

## What this skill does

Transforms an epic document (a phase-sized goal with many user stories) into a two-layer decomposition:

1. **3–5 feature specs** — team-level contracts. One feat spec per team-ownership boundary (FE, BE, mobile, service). Each feat spec freezes the cross-team handoff contract and groups stories that share an implementation boundary.
2. **Optionally — 3–5 sub-specs per feat spec** (cap `.A` through `.E`) — shippable-PR-level units sized for an AI coding harness like [hoangsa](https://github.com/unknown-studio-dev/hoangsa). Each sub-spec ships one cohesive surface as one PR, written as a Notion page so the team can track it on a board. Sub-specs that exceed the AI's working-context sweet spot (~250k tokens) get a **Plan Split** annotation that hoangsa uses to plan two sequential cook sessions.

The core problem this solves: epics are too big (agent loses the thread, scope creeps, technical decisions drift), feat specs are still too big to hand to a single AI session (the 35-story feat spec doesn't fit one bounded agent run), and stories are too small (agent implements in isolation, misses shared code paths, re-litigates decisions). The sub-spec layer is the missing rung — bundles stories that ship together, freezes the technical contracts at the right level, and preserves just enough context for a bounded agent session.

**Where this skill stops:** the sub-spec layer. Everything below that — `DESIGN-SPEC.md`, `TEST-SPEC.md`, `plan.json`, task context packs — belongs to hoangsa's `/hoangsa:menu` and `/hoangsa:prepare` commands. This skill produces what hoangsa ingests via `EXTERNAL-TASK.md`; it does not duplicate hoangsa's work.

## Core principles

**1. Each spec must be SMART-independent.** Specific, Measurable, Achievable, Relevant, Time-bound — and crucially, **measurable without its siblings existing**. If Spec B needs Spec A done before B can be tested, the cut is wrong. Use mocked contracts so every spec is independently verifiable.

**2. The handoff contract is load-bearing.** When teams are split (e.g. FE/BE), the contract is what lets them work in parallel. It must be typed (TypeScript or equivalent), frozen before either side codes, and canonical in one place that AI agents can read.

**3. Decisions already made stay made.** Feature specs carry a "Decisions Already Made" section so agents don't re-argue provider choices, state libraries, or data layer picks. This is the single biggest reason agents drift mid-implementation.

**4. Max 5 specs per epic.** 3 is default. 5 is the ceiling. More fragmentation than 5 is a signal the epic itself should be split.

**5. Adapt to the user, not the other way around.** Different users need different splitting strategies. A non-tech PM delegating to an FE/BE team needs clear ownership boundaries and handoff contracts. A technical lead breaking down their own work needs flexible cuts by service, domain, or value slice. The skill detects which persona is at play and adjusts accordingly.

**6. FE specs must be grounded in designs when available.** If UI designs exist (Figma, Pencil, or other tools), the FE spec must reference them — mapping screens to components, citing design tokens, and linking acceptance criteria to specific design states. This prevents the "technically correct but doesn't match the design" failure mode.

**7. Sub-specs use stub-first as the default cutting principle.** When decomposing a feat spec into sub-specs, the first sub-spec is the structural skeleton — provider chain, navigation root, base services — shipping stubs for everything siblings will fill in. Each later sub-spec replaces stubs from earlier sub-specs without touching the integration site. Every sub-spec's Out of Scope section MUST name its sibling sub-specs by ID (`7.1.C`, `7.2`, etc.) — anonymous deferrals fail SMART independence.

**8. The skill stops at the sub-spec layer; hoangsa owns everything below.** Do not generate `DESIGN-SPEC.md`, `TEST-SPEC.md`, `plan.json`, or task context packs — those are hoangsa's outputs. Do not emit token-budget numbers into Plan Split sections — hoangsa runs `hoangsa-cli budget estimate` for that. The skill's job is to produce the right-shaped input that hoangsa's `/hoangsa:menu` can ingest cleanly via `EXTERNAL-TASK.md`.

## Workflow

Follow these steps in order. Use the AskUserQuestion tool to gather inputs — do not assume.

### Step 1: Understand the user (persona detection)

Before asking about team structure or technical details, determine who you're working with. This shapes everything downstream — the questions you ask, the cutting strategy, and the level of technical detail in the specs.

Ask the user (use AskUserQuestion):

1. **Your role in this epic** — present options:
   - **PM / non-technical owner** — "I write the epic, another team implements it. I need specs that clearly divide work across my FE/BE (or other) teams with handoff contracts."
   - **Technical lead / architect** — "I understand the codebase. I want help decomposing this epic into implementation-ready specs for myself or my team. I'll decide how to split."
   - **Solo developer / full-stack** — "I'm implementing this myself. I want specs to break the work into manageable AI-codeable chunks."

Store the persona. It determines:

| Persona | Default team split | Contract depth | Design integration | Technical detail level |
|---|---|---|---|---|
| PM / non-technical | FE + BE (guided) | Full handoff contracts with prose companion | High — map designs to specs | Business-facing acceptance criteria |
| Technical lead | User-defined (flexible) | Typed interfaces only (skip prose companion unless requested) | Medium — reference designs, user extracts details | Implementation-level acceptance criteria |
| Solo developer | Single team (no split) | Internal seams only | Light — link to designs | Full technical detail, code-level notes |

### Step 2: Gather context

Now ask the remaining context questions, **adapted to the persona**:

**For all personas:**

1. **Epic source** — path to the epic file, or Notion URL. Read it in full before proceeding.
2. **Max spec count** — 3 (default, tightest) / 4 / 5 (ceiling).
3. **Spec storage location** — where to write the `.md` files (e.g. `product_docs/specs/{epic}/`, `.hoangsa/sessions/{branch}/`, `docs/specs/`).
4. **Existing tech doc** — ask if there's an architecture/technical document the specs should cite rather than duplicate. Read it if provided.

**For PM / non-technical persona — add:**

5. **Team structure** — present options:
   - FE + BE (presentation vs. everything-else — **recommended default**)
   - FE + BE + Mobile (three-way)
   - Other (free text — describe your teams)

   Explain: "FE team gets one spec per epic covering all presentation work. BE team gets the remaining specs split by service or pipeline stage. A typed handoff contract connects them."

6. **Contract storage location** — where TypeScript contract files live (e.g. `contracts/` at repo root).
7. **Language for the contract** — default TypeScript. Offer alternatives only if the user's stack clearly isn't TS.

**For Technical lead persona — add:**

5. **How do you want to split?** — present options:
   - By team boundary (FE/BE, FE/BE/Mobile, etc.) — same as PM flow
   - By service or domain (e.g. "auth service", "payment pipeline", "notification system")
   - By implementation layer (UI / domain logic / data layer)
   - By value slice (happy path first, then resilience, then polish)
   - Custom — describe your preferred split

   If they pick "by team boundary", follow the PM flow for team structure questions. Otherwise, ask them to describe the boundaries they want.

6. **Contract format** — TypeScript interfaces (default), Go types, Python protocols, JSON Schema, or "just markdown descriptions".

**For Solo developer persona — add:**

5. **Preferred split approach** — present options:
   - By value slice (ship incrementally — **recommended**)
   - By layer (UI / domain / data)
   - By feature area (group related stories)
   - Let the skill decide based on the epic

6. **Do you want typed contracts between specs?** — Yes (helps AI agents stay bounded) / No (lightweight, just markdown boundaries).

Do not improvise these inputs. A wrong assumption here corrupts every spec downstream.

### Step 2.5: Gather UI design references

After gathering context, check for available UI designs. This step is critical for any epic that has user-facing features.

**Auto-detect design tools:** Before asking the user, check which design MCPs are available:
- Look for Figma MCP tools (e.g. `mcp__figma__*` or `mcp__e8eed802-*` / `mcp__plugin_design_figma__*`)
- Look for Pencil MCP tools (e.g. `mcp__pencil__*`)

**If design MCP(s) are detected**, ask:

> "I can see you have {Figma/Pencil} connected. Do you have UI designs for this epic I should reference? If so, please share the file URL or key, and I'll pull component details, screen flows, and design tokens directly into the FE spec."

**If no design MCP is detected**, ask:

> "Do you have UI designs for this epic (Figma, Pencil, screenshots, or any other format)? Providing designs helps ensure the FE spec matches your intended UI — I can map screens to components and reference specific design states in acceptance criteria."

Present options:
- **Yes — Figma** (provide file URL or key)
- **Yes — Pencil** (provide document ID)
- **Yes — other format** (screenshots, PDF, or URL)
- **No designs yet** (skip — specs will note "UI design TBD" where relevant)

**When designs are provided, extract the following:**

If a **Figma MCP** is available and the user provides a Figma URL/key:
1. Use `get_file` or `get_file_nodes` to retrieve the page/frame structure
2. Use `get_file_components` to list reusable components used in the designs
3. Use `get_file_styles` to extract design tokens (colors, typography, spacing)
4. Use `get_image` to capture screenshots of key screens for reference
5. Use `get_screenshot` (Dev Mode MCP) if available for higher-fidelity captures

If a **Pencil MCP** is available:
1. Use `open_document` and `get_editor_state` to understand the document structure
2. Use `get_screenshot` to capture key screens
3. Use `get_variables` to extract design tokens
4. Use `search_all_unique_properties` to identify component patterns
5. Use `get_guidelines` to pull design system rules

If **screenshots or other static assets** are provided:
1. Read the image files to understand the UI
2. Identify screens, components, states, and flows from the visuals
3. Note any ambiguities that need designer clarification

Store the extracted design context for use in Step 4 (drafting specs).

### Step 3: Read and analyze the epic

Read the epic file. Identify:

- The **goal** (the one-sentence outcome)
- The **user stories** (enumerate them with their IDs)
- **Dependencies** on other epics or external systems
- **Technical notes** (stack decisions, architectural constraints)
- **Out-of-scope** items (these must NOT bleed into any spec)

Then mentally group the stories by **implementation cohesion** — which stories touch the same files, the same service, the same state machine? Groupings become candidate specs.

**If UI designs were provided in Step 2.5**, also identify:
- Which user stories have corresponding screens/frames in the design
- Which stories share UI components (candidates for the same spec)
- Any design states (loading, error, empty, success) that imply acceptance criteria not written in the epic
- Gaps: stories with no design coverage, or designs with no matching story

**When mismatches are found, do NOT silently resolve them.** Use AskUserQuestion to surface each mismatch (or batch related mismatches) with a concrete recommendation so the user can decide quickly. For each mismatch, present:

1. **What the mismatch is** — be specific (e.g. "The design has a 'Settings' screen but no user story covers settings in this epic")
2. **Why it matters** — what breaks if we ignore it (e.g. "FE will build a screen with no acceptance criteria, or skip a screen the designer intended")
3. **Recommended action** — one of:
   - *Add a story to cover the design* (if it fits this epic's scope)
   - *Defer the design screen to a future epic* (if it's out of scope)
   - *Request a design for the uncovered story* (if the story is in scope but has no design)
   - *Escalate to PM + designer to resolve the contradiction* (if design and story disagree)
   - *Proceed without design for this story* (if the UI is trivial or backend-only)
4. **Alternative options** — so the user isn't locked into one path

Record all mismatch resolutions in Section 5.5 of the feature spec template. **Unresolved mismatches block the spec from reaching "Frozen" status.**

### Step 4: Pick a cutting strategy

See `references/cutting-strategies.md` for the full decision tree. The strategy depends on the persona detected in Step 1:

**PM / non-technical persona:**
- Default to **Dual-team** → Spec X.1 is always the FE spec (all presentation work for the epic). BE specs split by service or by stage. This is the most common and safest pattern for delegated teams.
- FE (or any presentation-only team) gets exactly one spec per epic. All of that team's work rolls up into Spec X.1. One doc per epic for that team — this simplifies their reading and keeps cognitive load low.

**Technical lead persona:**
- Follow the split approach they chose in Step 2. If they picked "by team boundary", use the Dual-team pattern. Otherwise, use the matching strategy from `references/cutting-strategies.md`.
- Do not force Spec X.1 = FE if they chose a different split. Respect their architecture judgment.

**Solo developer persona:**
- Default to **Vertical-by-value-slice** (ship incrementally). Spec X.1 = happy-path end-to-end, X.2 = error handling + resilience, X.3 = polish + edge cases.
- If they chose "by layer", use Horizontal-by-layer.
- Contracts between specs are optional but recommended as internal seams for AI agents.

If uncertain, ask the user rather than guessing. The wrong cut is the most expensive mistake this skill can make.

### Step 5: Draft the specs

Use `templates/feature-spec.md` as the starting structure. Fill each spec with:

- Linkage back to the epic (cite goal and story IDs from the original)
- Scope in/out (explicit; no overlap with sibling specs)
- SMART outcome (see `references/smart-checklist.md`)
- Dependencies (on sibling specs and external epics)
- **Handoff Contract** (most important section for multi-team setups — see below)
- Grouped user stories with acceptance criteria
- Decisions Already Made (cite the tech doc; don't re-argue)
- Test plan (how we verify independently)
- Out of Scope Within This Spec (prevents gold-plating)
- **UI Design Reference** (if designs were provided — see section below)

#### UI Design Reference in specs

If UI designs were gathered in Step 2.5, every spec that includes user-facing work MUST include a "UI Design Reference" section (see `templates/feature-spec.md` Section 5). This section contains:

1. **Screen-to-story mapping** — a table linking each screen/frame from the design to the user stories it covers in this spec. Include the design frame name/ID and a brief description.

2. **Component inventory** — list every design system component used in this spec's screens. For each component, note:
   - Component name (as it appears in the design tool)
   - Variants/states used (e.g. `Button/Primary/Disabled`, `Card/Expanded`)
   - Whether it already exists in the codebase or needs to be built
   - Props/configuration visible from the design

3. **Design tokens referenced** — colors, typography, spacing values from the design that the spec's UI must use. Extracted from the design tool's styles/variables.

4. **State-to-screen mapping** — for each state in the handoff contract (or domain logic), which design screen/variant shows that state. This is critical for FE acceptance criteria:
   - `idle` → "Inbox/Default" frame
   - `processing` → "Inbox/Processing" frame (shows spinner)
   - `failed` → "Inbox/Error" frame (shows retry button)
   - `complete` → redirects to "Library/NoteDetail" frame

5. **Design gaps and open questions** — screens or states that have no design coverage yet, or designs that are ambiguous. Each gap gets an owner and deadline.

For **PM / non-technical persona**: this section is especially important — it's the bridge between "what the designer intended" and "what the developer builds". Include screenshot references or frame links wherever possible.

For **Technical lead persona**: focus on the component inventory and state mapping. They'll extract implementation details themselves.

For **Solo developer persona**: include design links and a lightweight component list. Skip the detailed token extraction unless they request it.

### Step 6: Author the handoff contract

**Skip this step if the user is a solo developer who opted out of typed contracts.**

For each spec that crosses a team boundary (or an internal seam the user wants enforced), produce a TypeScript contract file using `templates/handoff-contract.ts`. The contract defines:

- Mutations (actions the presentation layer calls)
- Selectors / hooks (state the presentation layer reads)
- Types (discriminated unions for state machines — always prefer these over loose `status: string` fields; they force exhaustive rendering)
- Events (optional subscriptions)

**Critical rule:** the contract is coarser than the internal state it represents. If BE has internal stages (e.g. `whisper-running`, `structuring`, `dlq-retry`), those should collapse to a single `processing` state at the contract boundary. The contract is a *seam*, not a mirror.

**For PM / non-technical persona:** Also produce a prose `BE-HANDOFF.md` (see `templates/be-handoff-narrative.md`) that documents the contract in human-readable form for Notion review. The `.ts` file is canonical; the `.md` is explanation.

**For Technical lead persona:** Skip the prose companion unless explicitly requested. They can read the `.ts` file directly.

### Step 7: Validate independence (SMART check)

For each spec, run through `references/smart-checklist.md`. The most important test:

> *"Can this spec's acceptance criteria be verified with sibling specs mocked out?"*

If no, cut differently. Typical fixes:
- Merge two specs that have circular dependencies
- Extract the shared dependency into a new spec that both depend on (counts toward the 5-spec ceiling)
- Move scope out (it belongs to another epic)

**Additional validation when designs are present:**
- Every screen in the design is covered by exactly one spec (no orphan screens)
- Every design state (loading, error, empty, success) has a matching acceptance criterion
- The component inventory doesn't have components split across specs without a clear owner

### Step 8: Write files and produce a dependency graph

Write each spec to the agreed storage path using the naming convention:

```
spec-{epic-number}.{spec-number}-{team}-{short-title}.md
```

Examples:
- `spec-3.1-fe-processing-surface.md`
- `spec-3.2-be-upload-transcription.md`
- `spec-3.3-be-structuring-note-creation.md`

**For non-team-boundary splits** (technical lead or solo developer who split by service/layer/slice), adapt the naming:
- `spec-3.1-api-auth-endpoints.md`
- `spec-3.2-worker-transcription-pipeline.md`
- `spec-3.1-slice-happy-path.md`

Write contract files to the agreed contracts path:

```
contracts/{feature-area}.ts
```

Example: `contracts/processing.ts`

Also produce a short mermaid diagram showing spec → spec dependencies, so the team can see the ordering at a glance. Include it in the epic's existing `.md` file as an appendix or in a new `SPECS-OVERVIEW.md` in the spec folder.

### Step 9: Present results

Output to the user, adapted to their persona:

**For PM / non-technical persona:**
- List of files written (with paths)
- The dependency graph (mermaid block)
- A **"What each team reads first"** summary — e.g. "FE team starts with Spec 3.1. BE team starts with Spec 3.2 and 3.3 in parallel."
- Design coverage summary — which screens are covered, any gaps flagged
- Any open questions or places where the user should review before finalizing

**For Technical lead persona:**
- List of files written (with paths)
- The dependency graph (mermaid block)
- Contract surface summary (types and interfaces defined)
- Implementation ordering recommendation
- Open questions

**For Solo developer persona:**
- List of files written (with paths)
- The dependency graph (mermaid block)
- Suggested implementation order (which spec to start with)
- Open questions

### Step 10: Offer sub-spec decomposition

After presenting feat specs, prompt the user whether to decompose them further into sub-specs. Use AskUserQuestion:

> "Your feat specs are ready. Each one is sized as a team contract (~20–35 stories on average). To hand them to an AI coding agent (e.g. [hoangsa](https://github.com/unknown-studio-dev/hoangsa)), each feat spec needs to be decomposed into 3–5 sub-specs — one per shippable PR, ~5–15 stories each, written as a Notion page. Want me to do that now?"

Present options:

- **Yes — decompose all feat specs into sub-specs** (recommended when shipping with hoangsa or a similar harness).
- **Yes — decompose one feat spec only** (pick which). Useful when only one team uses the harness, or when sizing up the pattern on a single spec first.
- **No — feat specs are sufficient** (teams will hand-write sub-specs or aren't using a harness yet).

If the user picks "no", stop here. The skill is done.

If the user picks "yes", proceed to Step 11. Before drafting, **read `references/sub-spec-cutting.md`, `references/plan-split-patterns.md`, and `templates/sub-spec.md` in full** so the AI agent has the patterns and the template loaded.

### Step 11: Sub-spec decomposition

For each feat spec the user picked, run the following sub-workflow:

#### 11a — Gather sub-spec context

Ask the remaining context questions via AskUserQuestion:

1. **Notion integration** — Is the Notion MCP connected, and where should sub-spec pages land? Present options:
   - **Yes — write to Notion database** (provide URL or ID of the destination database/data source). The skill will use `notion-fetch` on that URL first to discover the actual property schema, then `notion-create-pages` to create one page per sub-spec.
   - **No — markdown files only** (skill writes to repo; user creates Notion cards manually later).
2. **Sub-spec storage location** — defaults to `<feat-spec storage>/sub-specs/`. Confirm or change.
3. **Sub-spec naming** — defaults to `spec-X.Y.{letter}-<slug>.md` with `.A` through `.E`. Cap at 5 per feat spec.

#### 11b — Propose sub-spec boundaries (do not write yet)

Read the feat spec's `§3 Scope` subsections, story list, and (if present) `§5 UI Design Reference`. Apply the cutting strategy from `references/sub-spec-cutting.md`:

- **FE feat spec:** apply FE patterns in order — FE-1 (co-shipping coupled foundations as the first sub-spec, always), FE-2 (one sub-spec per coherent user-facing surface), FE-3 (stub-first dependent discipline within FE-2 sub-specs).
- **BE feat spec:** apply BE patterns — BE-1 (service / domain boundary as default), BE-2 (endpoint cluster when one service is too large).
- **Small / single-concern feat spec:** apply the fallback — output a single sub-spec with `.A` and note no siblings.

Then propose the boundaries to the user via AskUserQuestion. Present the proposed sub-spec list as: `7.1.A — <scope>`, `7.1.B — <scope>`, etc., with a one-line cohesion rationale for each. Ask: "Does this split look right, or would you like to adjust the boundaries?"

If the user proposes a different cut, accept it. The wrong cut is the most expensive mistake the skill can make at this layer.

If the proposed cut would need 6+ sub-specs to fit the work, escalate to the user: "This feat spec wants 6+ sub-specs. The .A–.E ceiling means we should either split the feat spec itself first, or pick the 5 most cohesive groupings and merge the rest. Which do you prefer?"

#### 11c — Draft each sub-spec

For each sub-spec, use `templates/sub-spec.md` as the starting structure. Fill in:

- **Required top-matter:** `Parent spec` (path + section list of the parent feat spec), `Contracts` (path to consumed contract, or "none consumed directly"), `Stories` (comma-separated story IDs inherited from the parent).
- **§1 Context** — write a 2–4 sentence cohesion rationale that quotes WHY these stories ship together. If using stub-first, add a sentence naming which stubs from sibling sub-specs this one replaces, and which of its own stubs siblings will replace later.
- **§2 SMART Outcome** — tight, measurable independently of sibling sub-specs.
- **§3 Scope (In Scope / Out of Scope)** — concrete file list grouped by feature module. **Out of Scope MUST name every sibling sub-spec by ID** (`7.1.C`, `7.2`, etc.). Anonymous deferrals fail SMART independence.
- **§4 Design Reference** — only frames this sub-spec touches; inherit tokens from parent §5.3.
- **§5 Contracts Consumed** — list types imported from `<contract>.ts`. If none, write "No contracts consumed — this sub-spec is structural."
- **§6 Acceptance Criteria** — flat numbered ACs, each tagged with parent story ID. **REQ-ready format:** hoangsa's `/hoangsa:menu` maps each AC 1:1 to a `[REQ-xx]` marker. Do NOT group ACs under story headings.
- **§7 Plan Split (only when warranted)** — see 11d.
- **§8 Dependencies / §9 Test Plan / §10 Decisions Already Made** — fill normally.

#### 11d — Decide if Plan Split is needed (skill-internal trigger)

Run the heuristic from `references/plan-split-patterns.md` (file count × per-type weight). **The heuristic is internal-only — never written into the output.**

If the heuristic sum is clearly above 250k, emit a §7 Plan Split section in the sub-spec, choosing the pattern:

- **FE-Plan (Substrate / Wiring)** — for FE sub-specs with both logic and UI.
- **BE-Plan-1 (Domain core / Transport)** — default for BE sub-specs.
- **BE-Plan-2 (Migration / Application)** — when migrations are nontrivial.

If the heuristic is comfortably below the threshold, **omit the §7 Plan Split section entirely.** Absence means "plan as one hoangsa session."

When emitting the Plan Split section, follow the template in `templates/sub-spec.md` §7 exactly. Two rules:
1. **No token numbers in the output.** Hoangsa is the budget authority.
2. **Include the Coverage check footer** — the qualifier-overlap pattern (`REQ-11 (logic only)` in Plan-1, `REQ-11 (UI)` in Plan-2) reads as a coverage gap without it.

#### 11e — Write outputs

For each sub-spec:

1. **Write the markdown copy** to `<sub-spec storage>/spec-X.Y.{letter}-<slug>.md`. This is the canonical copy that lives in git.
2. **Write the Notion page** (if Notion integration was chosen in 11a) using `notion-create-pages`. Discover the database's property schema via `notion-fetch` first; map only properties that actually exist:

   | Default mapping (only if property exists in the database) | Source |
   |---|---|
   | Task name | "Spec X.Y.{letter} — <short scope>" |
   | Description | Sub-spec §1 Context, first sentence |
   | Effort level | Heuristic from file count: Low (<5), Medium (5–15), High (>15) |
   | Priority | Inherit from epic, or default High |
   | Status | Always "Draft" |
   | Tags | Inherit from parent feat spec team tag |
   | Task type | Default "Feature request" |

   The page body is the full sub-spec markdown.

#### 11f — Present results

List the sub-spec markdown paths and Notion page URLs. For each sub-spec note:

- Stories covered
- Whether Plan Split was recommended (and which pattern)
- One-line "next step": *"Feed this to `/hoangsa:menu` when you're ready to implement."*

Also produce or update the dependency graph (mermaid) to include sub-spec → sub-spec relationships so the team can see the ordering at a glance.

## Handoff contract: the discipline

When a spec crosses a team boundary, follow these rules to prevent drift (the #1 failure mode of parallel teams):

1. **Freeze before coding.** The contract must be agreed by both team leads before either side writes production code. AI agents can work against mocks only if the mock shape is trustworthy.
2. **One source of truth.** The `.ts` contract file lives in one repo (the BE-owning repo is a good default). Other repos either import it as a package, sync via a small script, or copy-paste with a CI diff check. Do not rely on memory or Notion alone — AI agents need a file they can read.
3. **Amendments require co-review.** If a contract needs to change mid-implementation, both team leads sign off in the same PR. Amending quietly in one repo is the failure mode.
4. **Contract is coarser than internals.** FE sees `processing`, BE knows whether it's in Whisper-stage or DLQ-retry. Leaking internal states into the contract couples the teams and defeats the purpose.

See `references/team-split-patterns.md` for variants: FE/BE, FE/BE/Mobile, single team with service boundaries, solo developer, etc.

**Note:** For solo developers and single-team setups, the contract discipline is lighter — contracts serve as internal seams for AI agents rather than team coordination tools. The "freeze before coding" and "co-review" rules don't apply, but "one source of truth" and "coarser than internals" still help agents stay bounded.

## Anti-patterns to watch for

- **Spec 3.1 referenced in Spec 3.2's acceptance criteria** — that's a dependency cycle. Cut differently.
- **A spec with no handoff contract** — only OK for a spec that lives entirely within one team's ownership (e.g. a pure-backend worker) or for solo developers who opted out. If two teams touch it, contract is mandatory.
- **Stories copy-pasted verbatim from the epic** — preserve IDs, but rewrite acceptance criteria in the spec's voice with concrete, testable conditions.
- **Duplicating tech-doc decisions in every spec** — cite, don't re-state. The tech doc is authoritative.
- **More than 5 specs per epic** — the epic itself is probably too big. Escalate to the user: "Do we want to split the epic first?"
- **FE spec that also contains BE behaviour** — FE spec is presentation + input validation only. Domain logic goes to BE specs. (Applies to dual-team splits; for other split types, boundaries are defined by the user's chosen strategy.)
- **FE spec that ignores the design** — if designs were provided, every FE acceptance criterion should trace to a design screen or state. "It works but doesn't match the design" is a spec failure.
- **Design components split across specs with no clear owner** — if two specs render the same component, one must own it (build/export) and the other must consume it. Make this explicit.

### Sub-spec layer anti-patterns

- **ACs grouped under story headings instead of flat-numbered.** Sub-spec §6 must be a flat numbered list (`AC1, AC2, …`) with each AC tagged with its parent story ID. Story-grouped ACs break hoangsa's 1:1 AC → REQ mapping.
- **Anonymous "owned by another sub-spec" in Out of Scope.** Always name the sibling sub-spec by ID. Fails SMART independence otherwise.
- **More than 5 sub-specs per feat spec.** Hard ceiling at `.E`. If the work needs 6+ sub-specs, the parent feat spec itself is probably too big — escalate to the user before overflowing.
- **Skeleton sub-spec that doesn't ship stubs for siblings.** If `.A` omits provider stubs, every subsequent sub-spec (`.B`, `.C`, `.D`, `.E`) has to add the provider chain back to `_layout.tsx`, creating merge conflicts. The skeleton sub-spec MUST ship stubs.
- **Splitting a single user surface into multiple sub-specs by layer** (e.g., "types and hooks" as Sub-spec X.Y.A and "components" as Sub-spec X.Y.B). That's a **Plan Split** within one sub-spec, not two sub-specs. Sub-specs are shippable PRs; pure-substrate code does not ship alone.
- **Emitting token numbers in the Plan Split section.** The skill's heuristic is internal-only. Hoangsa's `hoangsa-cli budget estimate` is the authority on tokens — anchoring hoangsa on our number is garbage-in.
- **Missing the Coverage check footer in a Plan Split section.** The qualifier-overlap pattern (`REQ-11 (logic only)` / `REQ-11 (UI)`) reads as a coverage gap without it.
- **Generating `DESIGN-SPEC.md`, `TEST-SPEC.md`, or `plan.json`.** Those belong to hoangsa. The skill stops at the sub-spec layer.

## When to stop

You're done at the **feat-spec layer** when:
- Each feat spec is independently testable (SMART-independent)
- Each cross-team boundary has a TypeScript contract (or the user opted out for solo work)
- The user has reviewed the dependency graph and said "yes this ships in this order"
- Files are written to the agreed paths
- If designs were provided: every screen has a spec owner, and every spec's design section is complete
- Step 10 has been offered (sub-spec decomposition) and the user has either declined or completed Step 11

You're done at the **sub-spec layer** (Step 11) when:
- Each sub-spec is independently shippable (one PR per sub-spec)
- Each sub-spec's Out of Scope names its sibling sub-specs by ID
- ACs are flat-numbered and tagged with parent story IDs (REQ-ready)
- If a Plan Split section was emitted: it names boundaries by REQ + file category (no token numbers) and includes the Coverage check footer
- Markdown copies are written to `<sub-spec storage>/`; if Notion integration was chosen, Notion pages are created with discovered properties
- Sub-spec → sub-spec dependency graph is updated

If the user wants a worked example or a single spec drafted in full detail, offer to draft Spec X.1 end-to-end (the FE-heavy one when teams are split — it's the hardest to get right, so stress-test it first). For sub-spec examples, offer to draft Sub-spec X.1.A (the skeleton — same reasoning).

## References

**Feat-spec layer:**
- `templates/feature-spec.md` — the full feat spec template (includes UI Design Reference section)
- `templates/handoff-contract.ts` — TypeScript contract starter
- `templates/be-handoff-narrative.md` — prose companion for Notion review
- `references/cutting-strategies.md` — decision tree for cutting epics into feat specs (persona-aware)
- `references/team-split-patterns.md` — FE/BE, FE/BE/Mobile, single-team, solo-developer variants

**Sub-spec layer (new in v0.3):**
- `templates/sub-spec.md` — the sub-spec template (mirrors feat spec template, tighter scope, REQ-ready ACs, optional Plan Split section)
- `references/sub-spec-cutting.md` — decision tree for cutting feat specs into sub-specs (FE / BE / fallback)
- `references/plan-split-patterns.md` — when and how to emit a Plan Split section for hoangsa

**Shared:**
- `references/smart-checklist.md` — the SMART-independence validation (applies to both feat specs and sub-specs)
