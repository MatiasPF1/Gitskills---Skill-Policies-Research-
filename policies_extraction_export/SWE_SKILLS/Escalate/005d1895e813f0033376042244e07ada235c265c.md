---
description: Execute the autonomous backlog cycle — triage, delegate, review, test, commit, retrospect
---

Execute against the backlog leveraging the team of expert agents. A single `/cycle` invocation processes MULTIPLE backlog items: pick the highest-priority unblocked item, run the full per-item protocol (triage → engage → execute → test → commit → update backlog → brief retro), then re-enter the loop on the next highest-priority unblocked item. Each item gets its own atomic commit(s) and its own clean-tree gate before the loop advances. Stop when a budget/safety gate trips (see below).

## Backlog 

Read `.claude/BACKLOG.md` as the backlog source.

## Loop & Stop Conditions

`/cycle` LOOPS over backlog items within a single invocation. `/run-task` does NOT — it runs exactly one item per invocation. Do not conflate them.

**Loop entry**: Step 2 selects the highest-priority unblocked item to start an iteration.
**Per-item boundary**: Steps 3–9 run for the selected item. The Step 7a clean-tree gate MUST pass before the loop advances to the next item. A dirty working tree blocks loop advancement.
**Loop re-entry**: After Step 9's brief per-item retro, return to Step 2 to select the next highest-priority unblocked item.

**Stop the loop and surface control to the user when ANY of these trip** (then proceed to per-invocation Steps 10 and 11):

1. **Budget**: token/context budget is running low (e.g., approaching the model's context window or the session's effective working budget).
2. **Complexity gate**: the next selected item triages to **Complex** tier (per Step 3's execution-model classification). Complex-tier work warrants a fresh invocation with full attention, not a tail-end loop iteration.
3. **One-way door**: the next iteration would require an irreversible action — `git push`, package publish, destructive migration, resource deletion, production deploy. Surface to the user for explicit approval; do not perform the action inside the loop.
4. **User-only decision**: a decision only the user can make is reached (scope ambiguity, product trade-off, sensitive trust call).

On any trip, do NOT silently skip the item — stop the loop, run Steps 10 and 11, and report which gate tripped, the item it tripped on, and what the user needs to decide.

## Cycle Protocol

### Step 1 — Read Context (once per invocation)
Read `.claude/CLAUDE.md` to understand project constraints. Run this ONCE at the start of the invocation, not per loop iteration.

### Step 2 — Load Backlog (loop entry)

Read `.claude/BACKLOG.md`. If empty, prompt the user for input and exit.

Select the highest-priority unblocked item to start this iteration. If no unblocked items remain, stop the loop, proceed to Steps 10 and 11, and report "backlog drained".

### Step 3 — Triage
Perform two-dimensional triage (see CLAUDE.md § Two-Dimensional Triage):

**A. Execution Model** — Apply the 4-criterion checklist:

| # | Criterion | Check |
|---|-----------|-------|
| 1 | Spans multiple technical domains? | [ ] |
| 2 | Regulatory or compliance implications? | [ ] |
| 3 | Could impact production stability? | [ ] |
| 4 | Significant cost or resource commitment? | [ ] |

Score: 0-1 = Simple, 2-3 = Moderate, 4 = Complex. Check mandatory escalation triggers (security vulnerability/architecture change, PCI/regulatory, production stability risk, irreversible one-way doors) — these override scoring to Complex.

**B. Stakeholder Identification** — Identify which perspectives must be represented:
- **Mandatory pair (all tiers)**: Product + Tech.
- **Domain signals**: Scan the task for triggers — Security/compliance, Data modeling/pipelines, Cross-system integration, Infrastructure/CI-CD, Statistics/experimentation, ML systems, Test strategy/quality, SLOs/reliability, Requirements/process. Add the corresponding stakeholder for each signal detected.
- **Stakeholder escalation guard**: Simple with 4+ stakeholders → consider Moderate. Moderate with 5+ stakeholders → consider Complex. Many stakeholders needing deep analysis is itself a complexity signal.

> Full stakeholder mapping with profiles and key questions: `${CLAUDE_PLUGIN_ROOT}/reference/stakeholder-guide.md`

Output BOTH the execution model classification AND the stakeholder list before proceeding.

### Step 4 — Plan Stakeholder Engagement
Before spawning any agents, declare the engagement plan:
1. **Identify stakeholders**: Use the stakeholder list from Step 3. Map each stakeholder to an agent profile using `${CLAUDE_PLUGIN_ROOT}/agents/index.md` and the Stakeholder Guide (`${CLAUDE_PLUGIN_ROOT}/reference/stakeholder-guide.md`).
2. **Plan by execution model**:
   - **Simple**: Manager will apply stakeholder perspectives inline using compact profiles (`${CLAUDE_PLUGIN_ROOT}/agents/*-compact.md`). No agents spawned for analysis — the manager rotates through each lens directly.
   - **Moderate**: Plan Phase 1 (stakeholder analysis agents spawned in parallel), Phase 2 (lead implementation agent), Phase 3 (adversarial reviewer). Assign a profile to each phase.
   - **Complex**: Plan team formation — coordinator + stakeholder agents via `TeamCreate`. Identify the deputy coordinator role and assign stakeholder agents to parallel workstreams.
3. **State the plan**: Name each stakeholder perspective, their agent assignment (or "inline" for Simple), and expected deliverable before proceeding to execution.

> Steps 5–9 below execute for the SINGLE item selected in Step 2. They form one loop iteration. After Step 9 completes for the current item, return to Step 2 to select the next item (subject to the Loop & Stop Conditions above).

### Step 5 — Execute
Execute according to the execution model determined in Step 3 (see CLAUDE.md § Execution Models):

**Simple — Inline Perspective Rotation**:
The manager applies each identified stakeholder lens directly using compact profiles (`${CLAUDE_PLUGIN_ROOT}/agents/*-compact.md`). For each stakeholder, produce a PERSPECTIVE block:
```
PERSPECTIVE: [Stakeholder] ([profile].md)
LENS: [What this stakeholder examines]
ASSESSMENT: [1-2 sentence finding]
CONCERN: [Primary concern, or "None — [reason]"]
```
After all perspectives: synthesize into unified action. If code changes are needed, delegate implementation to an expert agent via the Task tool.

**Moderate — Task Tool Engagement (3 phases)**:

*Phase 1 — Stakeholder Analysis*: Spawn stakeholder analysis agents in parallel. Each agent examines the task from their stakeholder perspective. These agents analyze but do NOT implement.

*Phase 2 — Lead Implementation*: Synthesize Phase 1 findings. Brief the lead expert with the synthesized stakeholder analysis. The lead expert produces the primary deliverable.

*Phase 3 — Adversarial Review*: Spawn the reviewer with the Adversarial Review Protocol. The reviewer's job is to find the single most important problem. Peer review is integrated here — there is no separate review step.

All three phases are mandatory for Moderate tier.

> **Set `model` on every Task spawn per CONDUCTOR.md § Model Selection.** Function rules (terse): Phase-1 analysts → `sonnet` (`haiku` for bounded/docs-only lenses); Phase-2 Moderate lead → `sonnet` (escalate to `opus` for high-risk implementations or unresolved TENSION); Phase-3 adversarial reviewer → **always `opus`** regardless of the reviewer role's default. Per-role default fallback table is in CONDUCTOR.md § Model Selection — do not duplicate it here.

**Complex — Parallel Team (Swarm)**:

After tier classification confirms Complex, run `oj-helper agent-teams-check` and parse `.available` from the JSON stdout. The probe always exits 0 (Axiom 8 — never block on the probe itself); branch on the JSON value, not the exit code.

*When `.available == true` — TeamCreate path:*

1. **Team Formation**: Create the team via `TeamCreate`. Spawn a deputy coordinator and stakeholder agents as teammates.
2. **Deputy Coordinator**: A general-purpose agent briefed with the full stakeholder plan. Manages inter-stakeholder communication, creates tasks, synthesizes raw output, and relays concise updates to the manager.
3. **Parallel Execution**: Stakeholder agents work concurrently, coordinated by the deputy.
4. **Synthesis**: Coordinator synthesizes → manager reviews → user checkpoints as needed.
5. **Teardown**: Retrospective, then `TeamDelete` to clean up the team.

*When `.available == false` — Convene→Consult fallback (Axiom 8):*

1. **Deputy Spawn (via Task tool)**: Spawn ONE general-purpose deputy coordinator via the Task tool, briefed with the full stakeholder plan. `TeamCreate` is unavailable in this branch — do not call it.
2. **Parallel Stakeholder Consults (via Task tool)**: The deputy fans out the stakeholder analyses as parallel Task-tool invocations. Each stakeholder returns its handback to the deputy.
3. **Handback-only Synthesis**: The deputy synthesizes via the handback protocol only. `SendMessage` / Inform is unavailable in this branch — no peer messaging.
4. **Quality Gates Preserved**: User Checkpoint ("Should we proceed?"), pre-mortem (≥3 scenarios), and adversarial review remain mandatory — the fallback is an execution-substrate degradation, not a tier downshift.
5. **Teardown**: Retrospective only. Do NOT call `TeamDelete` or `shutdown_request` — those tools are unavailable in this branch.

*Runtime backstop (the probe is a hint, not a guarantee)*: `agent-teams-check` only inspects the env var; an environment where the var is set but `TeamCreate` is actually disabled at runtime (enterprise policy, future flag retirement) will steer this skill onto the team branch incorrectly. If the team branch is taken and the first `TeamCreate` call — or any agent-teams-gated tool (`TeamCreate`, `TeamDelete`, `SendMessage`, `shutdown_request`) — raises "Unknown tool" / "tool unavailable" at runtime, do NOT abort the loop iteration. Fall through to the deputy-coordinator parallel-Task-tool fan-out above (handback-only synthesis, no Inform). The runtime signal is authoritative over the probe; the User Checkpoint promised at triage MUST still fire before the iteration commits.

> **Set `model` on every Task spawn per CONDUCTOR.md § Model Selection.** Function rules (terse): Complex-tier lead implementer → **`opus`**; adversarial reviewer slot → **always `opus`** regardless of the reviewer role's default; deputy coordinator → `sonnet` (escalate to `opus` if it carries the synthesis weight); stakeholder analysts → `sonnet` (`haiku` for bounded/docs-only lenses); specialists on a domain trigger → `sonnet`, escalate to `opus` when their domain is the decisive risk (Security on auth/crypto, SRE on SLO-impacting change, Data Architect on destructive migration). Per-role default fallback table is in CONDUCTOR.md § Model Selection.

### Step 6 — Test
Validate with tests. Ensure a balanced test pyramid (unit > integration > e2e). Run existing tests to confirm no regressions.

### Step 7 — Commit
Create atomic commits with clear messages scoped to THIS item. Do NOT include "Co-Authored-By" lines or other AI attribution in commit messages. Each loop iteration produces its own commit(s); do not batch multiple items into one commit.

**Commit Verification Gate** (7a): After committing, run `git status` to confirm the working tree is clean — no uncommitted tracked changes or untracked files that should be committed. If uncommitted changes remain, stage and commit them before proceeding. Do not advance to Step 8, and do not advance the LOOP to the next item, until the working tree is clean. A dirty tree at this gate is a hard block on loop advancement.

### Step 8 — Update Backlog
- **BACKLOG.md**: Mark THIS item complete, add any discovered work, update `.claude/BACKLOG.md`. Commit this update as part of the per-item commit boundary (Step 7) — the loop must not advance with an unstaged backlog edit.

### Step 9 — Per-Item Retrospective
Brief retrospective on what worked and what to improve for THIS item. Keep it short (a few bullets) — full retros happen per-invocation if needed, and Complex-tier items trigger a stop (see Loop & Stop Conditions) so they get their own invocation. For Complex tier items (if one slipped through), write to `.claude/archive/retros/`.

> After Step 9 for the current item: re-enter the loop at Step 2 on the next highest-priority unblocked item, UNLESS a budget/safety gate (see Loop & Stop Conditions) trips. If a gate trips, skip directly to Step 9a, then Step 10, then Step 11 (which now run ONCE per invocation, not per item).

### Step 9a — Dev Mode Feedback (per invocation, after the loop ends)
After the loop has stopped (backlog drained or a gate tripped), run `oj-helper feedback-path` in bash. If the output is empty (dev mode is off), skip feedback. Otherwise, the output is the file path to write. Write ONE feedback file per invocation summarizing the full run — not one per item, to avoid file spam. Format:
```
---
date: YYYY-MM-DD
items: [KEY-NNN, KEY-NNN, ...]  # or [BACK-XXX, BACK-XXX, ...]
tiers: [Simple|Moderate|Complex, ...]
stop_reason: budget-drained | complex-next | one-way-door | user-decision | backlog-drained
---
### What Worked
- [bullet points across the run]
### What to Improve
- [bullet points across the run]
### OpenJunto System Suggestions
- [specific suggestions for improving OpenJunto itself — agent profiles, cycle protocol, CLAUDE.md instructions, etc.]
```
Fill in the actual date, the list of backlog item IDs processed during this invocation, the list of tiers in iteration order, the stop reason, and a run-level retrospective. Each `/cycle` invocation produces exactly one new feedback file.

### Step 10 — Artifacts (per invocation)
Store any design documents, ADRs, or analysis artifacts produced during the run in `.claude/artifacts/`.

### Step 11 — Notify (per invocation)
Tell the user the cycle invocation is complete. Summarize: (a) how many items were processed and their IDs, (b) which stop condition tripped (budget / complex-next / one-way-door / user-decision / backlog-drained), (c) for `complex-next` / `one-way-door` / `user-decision` — the item it tripped on and what decision the user needs to make. Suggest `/clear` before the next invocation if context is getting large.

## Constraints

- A single `/cycle` invocation iterates the per-item protocol over MULTIPLE backlog items, one item at a time, with a per-item commit boundary. (`/run-task` is the single-item form — use it when you want exactly one item.)
- Each loop iteration is scoped to ONE backlog item: triage, execute, test, commit, update backlog, brief retro — then re-enter the loop on the next item.
- Per-item atomic commits: each item gets its own commit(s); do not batch multiple items into one commit. The Step 7a clean-tree gate MUST pass before the loop advances.
- Stop the loop at any budget/safety gate: token/context budget low, next item triages Complex, irreversible / one-way-door action required, or a user-only decision is reached. See "Loop & Stop Conditions" above for the full enumeration.
- Prefer small, atomic commits over large monolithic ones.
- Do not proceed past review if peer review identifies blocking issues — stop the loop and surface.
- If blocked or uncertain, stop the loop and ask the user rather than guessing.
