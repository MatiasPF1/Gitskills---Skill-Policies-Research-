---
name: development-pattern-guide
description: Examine a repository, repo URL, or local folder; derive a reusable, general-purpose development pattern from its architecture; and generate a paginated, fully offline HTML tutorial website (one chapter per page) that teaches developers to build similar projects with that pattern. Also adds chapters to, and restyles, existing generated guides. Use when the user wants a "development pattern guide", "developer guide website", a pattern tutorial, or to add a chapter / change the style of an existing one.
argument-hint: ["<repo-path | repo-url | folder> [--output repo|cwd] [--style-guide <style-guide.html> --style-css <style-guide.css>]", "add chapter \"<title>\" [after <n> | before <type>] [in <guide-path>]", "update style [--style-guide <style-guide.html> --style-css <style-guide.css>] [in <guide-path>]"]
---

# development-pattern-guide

Turn a real codebase into a **paginated, offline HTML tutorial** that teaches the
*pattern* behind it — so a developer can engineer their own project the same way.
A trivial example of the output: a tutorial on using the **Singleton Pattern** to
write a **database library**.

The generated site is plain static HTML + CSS + vanilla JS. It opens directly in a
browser: **no build step, no server, no CDN, no network**. All assets (including
fonts) are bundled.

> **Skill assets** live next to this file under `assets/`:
> `default-global.css`, `guide.js`, `fonts/` (bundled WOFF2 + `FONTS.md`),
> `templates/` (`page-template.html`, `toc-template.html`,
> `architecture-template.html`), and `guide.schema.json`.
> Resolve them relative to this `SKILL.md`; call that directory `SKILL_DIR`.

---

## 1. Detect the operation

Read the user's request and pick exactly one:

| Intent | Trigger | Go to |
|--------|---------|-------|
| **Create** a new guide | A repo path, repo URL, or folder is given (the default) | §3 |
| **Add a chapter** | "add a chapter", "insert a chapter", names a chapter to add | §4 |
| **Update style** | "update/change the style", "re-skin", supplies a new style-guide | §5 |

If the request is ambiguous (e.g. a path **and** "add a chapter"), ask the user
which operation they want before proceeding.

A user-supplied **style guide** (`style-guide.html` + `style-guide.css`) may be
provided to Create or Update style. See §6.

---

## 2. Output location (all operations that write a guide)

- The guide is **always** written into a subfolder named **`development-pattern-guide/`**.
  Create it if it does not exist; reuse it if it does.
- Deciding the **parent** of that subfolder:
  - **Local repository source** → you MUST ask the user where to put it:
    > "Create the guide inside the repository (`<repo>/development-pattern-guide/`)
    > or in the folder you started from (`<cwd>/development-pattern-guide/`)?"
  - **Repo URL source** (cloned to a temp dir) → use the current working directory
    (the folder the user started in). Do not write the guide into the temp clone.
  - **Local folder source that is not a git repo** → default to that folder; if it
    is clearly read-only or not the user's project, ask.
- Inside the guide folder, copy the skill assets into an `assets/` subfolder
  (see §3, step 7). Never modify the originals in `SKILL_DIR`.

---

## 3. Create a new guide

### Step 0 — Parse inputs
Identify the source (repo path / repo URL / folder) and any `--style-guide` /
`--style-css` paths. Report the plan to the user in one short line.

### Step 1 — Acquire the source
- **Repo URL** → `git clone --depth 1 <url>` into a temp directory; analyze there.
- **Local path / folder** → analyze in place (read-only; do not modify the source).
- Verify the path exists; if not, stop and tell the user.

### Step 2 — Resolve the output location
Apply §2. Confirm the final guide path with the user before generating files.

### Step 3 — Research the codebase (do this thoroughly and deeply)
Build a **deep** understanding before writing anything. Shallow, surface-level
research produces a shallow guide, which is the failure mode to avoid. Read the
actual implementation, not just file names and signatures. Prefer, in order:
available code-intelligence tools → language servers → `glob`/`grep` → reading
key files. Trace at least one real end-to-end path through the code yourself.
Determine:
- **Tech stack**: languages, frameworks, runtimes, package managers, notable
  libraries/SDKs, cloud services (note **.NET Aspire** if present — see §5/Deployment).
- **High-level architecture**: the core systems, sub-systems, major components,
  and how they interact (entry points, control flow, data/request flow).
- **Key classes/modules/services** and their responsibilities, including the
  **contracts and invariants** they uphold (what must always be true) and the
  **boundaries** between them (interfaces, abstractions, seams).
- **Control and data flow specifics**: how a request/operation actually moves
  through the system step by step, where state lives, and how errors, edge
  cases, and failures are handled.
- **The repeatable pattern**: the *core idea* that makes this design work and could
  be reused in another project (e.g. "a single shared accessor guards all access to
  a resource"). Capture it with real depth, not just a one-line label:
  - **Motivation**: the problem the pattern solves and why a naive approach falls short.
  - **Forces and trade-offs**: the competing concerns it balances, and what it
    deliberately gives up to gain what it gains.
  - **Structure**: the roles/participants in the pattern and how they collaborate.
  - **Consequences**: what becomes easy, what becomes hard, and the failure modes
    to watch for.
  This pattern, in this depth, is the spine of the tutorial.
- **Setup/run path**: how someone installs deps and runs it locally.

Carry this research forward into the approval summary in Step 6 and into the
chapter content; do not discard the depth once analysis is done.

### Step 4 — Generalize all names (critical)
The tutorial teaches a **reusable pattern**, so it must **not** use the source's
real identifiers. For every system, sub-system, class, and library, derive a
**general-purpose name from its purpose** and use that consistently everywhere.
- Example: `RetailerFinancialRecord` → `DataModel`; `AcmePaymentGateway` →
  `PaymentService`; `Foo.Bar.UserRepositoryImpl` → `Repository`.
- Keep a **naming map** (real → general) for your own consistency; write the
  general names into pages and into `guide.json`. Never leak the originals into the
  rendered guide. (You may keep the map in memory; do not ship it in the site.)
- **One exception: the "Sourced Repository" chapter** (Step 5). That chapter exists
  to describe the *real* originating repository, so it **does** use the source's real
  identifiers. This carve-out is **strictly limited to that single chapter** — every
  other chapter, the TOC, the architecture node graph, and `guide.json` must still
  use only the generalized names.

### Step 5 — Plan the chapters
Order is fixed for the framing chapters; pattern chapters sit in the middle.

**Required, in this order:**
0. **Table of Contents** — `index.html` (pretty landing page; links to all chapters).
1. **Introduction** — what this pattern does at its core.
2. **Sourced Repository** — a high-level, technically detailed overview of the
   **real originating source repository** the pattern was derived from: its systems,
   sub-systems, and key classes/modules/services, and how they fit together. The
   purpose is to give the reader the context needed to understand *what was actually
   studied* when deriving the pattern. **This chapter is the single explicit
   exception to the name-generalization rule (§3 Step 4 / §7): it uses the source's
   real identifiers.** See the per-chapter guidance below for what to cover.
3. **Prerequisites** — required tools, technologies, SDKs/packages, accounts or
   permissions, and assumed skills.
4. **High Level Architecture** — core systems/sub-systems, major components, how
   they interact, and data/request flow. Rendered as an interactive **left-to-right
   node graph**: clickable **nodes → modal dialogs**, with directional **labeled
   edges** showing each relationship (see §7 and `architecture-template.html`).

**Then the pattern chapters** — the "learn by doing" core. Break the pattern into
logical chapters, one HTML page each, sequenced so a reader can build their own
solution chapter-by-chapter.

**Then, last (in this order):**
- **Extending the System** — how to add features/plugins/modules, where they hook
  into the pattern, and common extension patterns.
- **Deployment** — *when applicable* (cloud-derived patterns): how to deploy. If the
  source uses **Aspire**, explain deploying with Aspire (e.g. `azd` / Aspire
  manifests). Omit this chapter if deployment is not relevant to the pattern.
- **Appendix: Additional Reading** — the **absolute last** chapter: curated URLs for
  the stack and concepts used by the pattern. Render these as a vertically stacked
  list of full-width cards using `<div class="resource-list">` containing one
  `<div class="resource-card">` per resource (each with a title, a short description,
  and the link). Do **not** use the multi-column `.card-grid`; full-width stacked
  cards give long URLs room to wrap so they never overflow.

Number chapters 1..N (the TOC page is number 0 / `index.html`). Name files
`NN-slug.html` (zero-padded), e.g. `01-introduction.html`.

**Chapter titles** must be **plain, specific, descriptive names** for the thing
the chapter covers, written for an engineer scanning a table of contents. Name
the component or concept directly (e.g. "Domain Model", "Repository Layer",
"Composition Root", "Data Import Service"). Do not use decorative, abstract, or
"artistic" phrasing, marketing language, or prose instructions (avoid "The Heart
of the System", "Bringing It All Together", "Start with the Data"). Keep titles
short and concrete. Write them in **title case** (capitalize principal words as
for the title of a book or article), not sentence case or prose. The same rule
applies to the section titles within each chapter (see §7).

**Sourced Repository chapter — what to cover.** This chapter is unique: it
describes the **real source repository** the pattern was derived from, so the
reader knows exactly what was studied. Write it from the deep research in Step 3 and
cover, with genuine technical depth (per §7):
- **What the project is**: its purpose, domain, and tech stack (languages,
  frameworks, runtimes, notable libraries/SDKs/services).
- **Systems and sub-systems**: the major systems, the sub-systems inside them, and
  how they interact (entry points, control flow, data/request flow).
- **Key classes/modules/services**: the important real types and their
  responsibilities, the contracts/invariants they uphold, and the boundaries
  (interfaces, seams) between them.
- **How it maps to the pattern**: close by pointing out which parts of this real
  structure the rest of the guide generalizes, so the reader can connect the
  concrete source to the abstracted lesson that follows.
This is the **one place real source identifiers are used** — see §3 Step 4 / §7 for
the strict boundary. Standard cards (`.card-grid`/`.card`) are appropriate here; do
**not** use the architecture node-graph template (that is the High Level
Architecture chapter, which stays generalized).

### Step 6 — Present the summary and table of contents for approval (required gate)
Before writing **any** files, stop and present the following to the user, then
**wait for explicit acceptance**:
1. A concise **high-level summary of the repository as you evaluated it**: the
   tech stack, the high-level architecture and key components, and — most
   importantly — the **derived reusable pattern** with its motivation, forces/
   trade-offs, and consequences (from Step 3). This shows the user the depth of
   understanding the guide will be built on.
2. The **proposed table of contents**: the ordered chapter list (numbers +
   title-cased titles) you planned in Step 5, including the framing chapters and
   the pattern chapters.

Ask the user to **accept the summary and table of contents, or request changes.**
- Do **not** proceed to scaffolding or page generation until the user explicitly
  accepts.
- If the user requests changes (different framing, more/fewer chapters, a
  different pattern emphasis, deeper analysis of some area), revise Step 3–5 as
  needed and **re-present** until they accept.

(This approval gate applies to the Create operation only; it does not apply to
§4 add-chapter or §5 update-style.)

### Step 7 — Scaffold the site assets
From the **chosen guide folder**:
1. Create `assets/`.
2. **Default style** (no custom style guide): copy `SKILL_DIR/assets/default-global.css`,
   `SKILL_DIR/assets/guide.js`, the whole `SKILL_DIR/assets/fonts/` folder
   (WOFF2 + `FONTS.md`), and the whole `SKILL_DIR/assets/vendor/` folder
   (`highlight.min.js` + `HIGHLIGHTJS-LICENSE`, the bundled syntax highlighter)
   into `<guide>/assets/`.
3. **Custom style** (style guide supplied): follow §6 instead — link the user's
   `style-guide.css`, still copy `guide.js` and `vendor/`, and localize referenced fonts/assets.
4. Confirm there are **no CDN/`http(s)://` references** in the copied CSS.

### Step 8 — Generate the pages
For each chapter, copy the matching template and replace **every** `{{PLACEHOLDER}}`:
- **Delete every `<!-- TEMPLATE-GUIDE … -->` comment** — these are author guidance,
  not output, and they contain `{{…}}` tokens that must not ship.
- Most chapters → `templates/page-template.html`.
- Sourced Repository → `templates/page-template.html` (standard chapter; uses the
  real source identifiers per §3 Step 4 / Step 5, not the architecture node graph).
- Table of Contents (`index.html`) → `templates/toc-template.html`.
- High Level Architecture → `page-template.html` with its `{{CHAPTER_BODY}}` built
  from `templates/architecture-template.html`. Build the **node graph**: place each
  component as an `.arch-node` (unique `id`, `data-modal` → matching modal) inside
  left-to-right `.arch-layer` columns (sources left, dependents right), and list the
  relationships in the hidden `.arch-edges` `<ul>` (`data-from`/`data-to`/`data-label`,
  where the label is the relationship). **If the graph would be busy enough that edges
  must cross, group the dense region into a system node** (`.arch-node--system`) whose
  modal embeds a nested `.arch-graph`; give that system node a single aggregated edge
  (`data-aggregate`) to each external node it relates to (see §7). The graph
  **auto-scales to fit** the content column and is **centred** (handled by
  `guide.js`) — never hand-size it; instead group into system nodes when it is large.
- Set `{{ASSETS}}` to `assets` (all pages sit at the guide root).
- Apply the **content & style rules** in §7 to every page.
- Use **general-purpose names** only (Step 4).

### Step 9 — Wire navigation and write the manifest
- Build the **fly-out TOC link list** once and embed the *identical* `{{TOC_LINKS}}`
  on every page. `guide.js` auto-marks the current page.
- Build the **TOC landing grid** (`{{TOC_ENTRIES}}`) on `index.html`.
- Set **footer prev/next** on every page from chapter order: each button shows the
  adjacent chapter's number + title; **Previous is left-aligned, Next right-aligned**.
  On the first chapter omit the `chapter-nav__prev` anchor; on the last omit
  `chapter-nav__next` (the remaining button keeps its side).
- Write **`<guide>/guide.json`** per `assets/guide.schema.json` (chapter order,
  types, titles/subtitles, files, `siteTitle`, `stylesheet`, and—if used—`styleSource`).
  This manifest is the source of truth for §4 and §5.

### Step 10 — Verify
- Confirm every `{{PLACEHOLDER}}` is gone and every `TEMPLATE-GUIDE` comment was
  removed (`grep -R "{{" <guide>` and `grep -R "TEMPLATE-GUIDE" <guide>` return nothing).
- Confirm every internal `href` resolves to a file that exists, and every
  `data-modal="X"` has a matching `id="X"`.
- Architecture graph: every `.arch-edges` `data-from`/`data-to` matches an
  `.arch-node` `id` **in the same graph**; every `.arch-node--system` modal contains a
  nested `.arch-graph`; edges carry a `data-label` relationship.
- Confirm `assets/` has the stylesheet, `guide.js`, fonts, and `vendor/highlight.min.js`;
  no network URLs. Spot-check that chapter pages still include the deferred
  `vendor/highlight.min.js` script (it ships in `page-template.html`) and that
  code blocks render highlighted.
- Open `index.html` in the browser if possible and sanity-check the fly-out TOC,
  a modal, and prev/next. Report the guide path and chapter list to the user.

---

## 4. Add a chapter to an existing guide

1. Locate the guide folder (the `development-pattern-guide/` containing `guide.json`).
   If you can't find `guide.json`, ask the user for the guide path.
2. Read `guide.json`. Determine **placement** from the user (e.g. "after chapter 6",
   "before Deployment"); if unspecified, ask. Keep the required framing chapters
   (TOC, Intro, Sourced Repository, Prerequisites, Architecture) at the front and
   Extending/Deployment/Appendix: Additional Reading at the back (Additional
   Reading absolute last) unless the user says otherwise.
3. Create the new page from `page-template.html`, following §7 and using the existing
   guide's general-purpose naming.
4. **Renumber** affected chapters and **rename files** if numbering shifts; update
   every page's `{{TOC_LINKS}}`, the `index.html` grid, and all prev/next footers so
   the chain stays consistent.
5. Update `guide.json` to match. Re-run the §3 Step 10 checks.

---

## 5. Update the style of an existing guide

1. Locate the guide and read `guide.json`.
2. **Two modes:**
   - **Token/CSS tweak** (no new style guide): edit the active stylesheet in
     `<guide>/assets/` (prefer the `:root` token block between `TOKENS:START` /
     `TOKENS:END` for color/font/spacing changes) and adjust pages only if class
     names change.
   - **Apply the dot-fade / binary-fade treatment to specific section(s)**: the default
     stylesheet already ships the `.dot-fade` and `.binary-fade` decorative sections
     (see §7). When the user asks for one on a named section, no CSS change is needed:
     add `class="dot-fade"` (navy dot-matrix) or `class="binary-fade"` (tiled 1's and
     0's) to that `<section class="chapter-section">` (its background bleeds full-width
     while the content stays put), and optionally use the matching `.dot-fade__grid` /
     `.binary-fade__grid` text-left / pattern-right layout. Apply it only to the
     sections the user specifies.
   - **Re-skin from a supplied style guide** (`--style-guide` + `--style-css`):
     follow §6, then regenerate page markup as needed to fit the new design system.
3. Keep the structure intact: every page must still have the fly-out TOC, stylized
   section dividers, chapter header+subhead, interactive cards, the architecture
   node graph (nodes→modals with labeled edges), and footer prev/next (mapped onto the
   new design — see §6).
4. Update `guide.json` (`stylesheet`, and `styleSource` if applicable). Re-run §3
   Step 10 checks. Confirm the result stays fully offline (no CDN references).

---

## 6. Bring-your-own style guide (`style-guide.html` + `style-guide.css`)

When the user supplies their own style guide, **use it in place of the default**.

1. **Inventory the design system.** Read `style-guide.html` to discover the
   available components, class names, design tokens, and layout patterns it offers.
   Read `style-guide.css` to learn its variables and conventions.
2. **Install the stylesheet.** Copy `style-guide.css` into `<guide>/assets/` and link
   it from every page instead of `default-global.css`. Record it as `stylesheet`
   (and the HTML path as `styleSource`) in `guide.json`. Still copy `guide.js`.
3. **Map required features onto the closest available styles.** Generate pages using
   the discovered vocabulary, matching these required capabilities to whatever the
   design system provides:
   fly-out Table of Contents · stylized section dividers · chapter header+subhead ·
   interactive (hover-reactive) cards · an architecture node graph whose nodes open
   modal dialogs and whose labeled edges show relationships ·
   footer prev/next (Previous left, Next right).
4. **Synthesize gaps in-style.** If a required component has no equivalent, create a
   small complementary style **consistent with the supplied system's tokens,
   spacing, and type** — do not fall back to the default look. Keep added CSS in the
   user's stylesheet (or a clearly-marked appended block).
5. **Stay offline.** Bundle any fonts/images the custom CSS references into
   `<guide>/assets/` and rewrite URLs to be relative. If something can't be
   localized (e.g. a remote-only asset), warn the user.
6. The `guide.js` behavior (fly-out toggle, modal open/close, current-page marking)
   is driven by the class/attribute **hooks** it expects
   (`.toc-flyout`, `.toc-flyout__tab`, `.toc-flyout.is-open`, `.modal`,
   `[data-modal]`, `[data-close]`, `.toc-flyout__link`). Preserve these hooks in the
   markup even when the visual styling comes from the user's CSS, or adapt `guide.js`
   accordingly.

---

## 7. Content & style rules (apply to every page)

- **Teach the why, not only the how (depth requirement).** This is the most
  important content rule. Every chapter and every section must explain the
  **reasoning** behind the technique, not just the mechanics. For each meaningful
  step, cover:
  - **Why** it is done this way: the motivation and the problem it solves.
  - **What it trades off**: the alternatives that were possible and why this
    approach was chosen over them.
  - **What it enables and what it costs**: the consequences, and the failure
    modes or pitfalls a reader should watch for.
  Tie each section back to the overall pattern and its forces (from §3 Step 3).
  Avoid shallow, one-line sections and "type this, then type that" instructions
  with no rationale. Use concrete, non-trivial code, and explain what each part
  does and *why it matters*. Depth and insight are the point of the guide.
- **Chapters are chunked.** Split each chapter into logical sections, each separated
  by a **horizontal rule**: `<hr class="section-divider">` (a thin navy hairline that
  matches the rule under the chapter header).
- **Titles + subtitles everywhere.** Every chapter has a header title + subhead
  subtitle (`.chapter-header`). Every section has its own title + subhead
  (`.section-heading` with `<h2>` + `.section-subhead`) briefly stating what it covers.
  - **Title style.** Both chapter titles and section `<h2>` titles must be
    **plain, specific, descriptive names** for the thing being covered, written
    for an experienced engineer (e.g. "Domain Model", "Repository Layer",
    "Composition Root", "Configuration Binding"). Do not use decorative,
    abstract, or "artistic" phrasing, marketing language, or prose instructions
    (avoid "The Heart of the System", "Bringing It All Together", "Start with the
    Data", "Declare the Properties"). Keep the title short and concrete. Write
    every title in **title case** (capitalize the principal words as for the
    title of a book or article), never sentence case or prose case. Put the
    descriptive, "what this covers" wording in the subhead.
  - **Subheads must not be templated (read this).** The section subhead
    (`.section-subhead`) is where AI tells show up most. Do **not** churn out
    subheads on a fixed grammatical frame. Specifically, **avoid** the repeated
    shapes that scream "generated":
    - "Why the …" / "What the …" / "How the …" openings used over and over.
    - "The X that …, and why …" (a noun phrase plus a tacked-on "and why" clause).
    - "A/An X that …" noun-phrase fragments for every section.
    - The **"short phrase, colon, explanation"** shape (e.g.
      "The boundary to the outside world: locating and reading the source").
    Within a single chapter, **no two subheads may share the same opening
    structure.** Mix it up: sometimes a full casual sentence, sometimes a
    question, sometimes a short remark a person would actually make out loud.
    The subhead should sound spoken, not catalogued. Example of the trap and the
    fix:
    - Robotic: `The two failure cases this method guards against, and why it
      fails loudly for one and quietly for the other.`
    - Coffee-chat: `One of these failures should crash the program. The other
      absolutely should not. Here's the difference.`
  - **Voice and prose style (two engineers over coffee).** The guide is accurate
    technical documentation for an experienced software engineer, but the *voice*
    should sound like **two engineers talking shop over coffee**, not a whitepaper
    and not marketing copy. Picture explaining this code to a friend you respect:
    warm, plain-spoken, a little wry, occasionally thinking out loud. Describe the
    technical facts accurately, what the code does, how it works, why it's built
    this way, what it trades off, but say it the way a person actually talks.
    - **Be genuinely casual.** Address the reader as "you", use contractions
      freely ("it's", "you'll", "doesn't", "that's"), and let the rhythm breathe.
      You may use the **first-person plural "we"** when walking through something
      together ("we hand that off to the next layer"). You may ask the occasional
      **rhetorical question**, drop a short **casual aside**, react to the code
      like a human would ("nothing fancy here, and that's the point"), and use
      **light humor** when it lands naturally. A well-chosen, concrete **analogy
      or metaphor** is welcome when it makes an idea click, used sparingly and
      tied to something real. Vary your register the way real conversation does:
      some sentences are tight and technical, some are loose and offhand.
    - **Never use first-person singular "I".** The voice is "you" and "we", never
      "I" or "me". Don't narrate your own process or opinions in the first person.
    - **Casual still is not hype.** Warm and conversational is the goal;
      sales-pitch is not. Do **not** use flowery or marketing language
      ("elegantly", "powerful", "seamless", "beautiful", "unlock", "delightful",
      "robust and scalable", "best-in-class"), and don't flatter the reader or
      manufacture suspense. Humor and analogies add warmth and clarity, never
      hype.
    - **Preserve the terminology.** Keep technical terms, code identifiers, type
      and method names, and API names exact and unchanged; the relaxed tone never
      softens or paraphrases precise vocabulary. Stay precise and assume the
      reader knows how to program; prefer concrete, specific statements over
      abstract or aspirational ones. When you use a specialized term, ground it in
      a concrete example. Casual is about *register*, not about being vague.
    - **Avoid the obvious AI tells.** Vary sentence structure and length so the
      prose doesn't fall into a repetitive template, and throw in a genuinely
      short sentence now and then. Don't open every section the same way or with
      formulaic scaffolding ("In this section, we will…", "Let's dive into…").
      Don't start paragraphs (or most sentences) with the "short noun phrase,
      colon, explanation" pattern. Skip hollow summaries that just restate the
      heading, reflexive hedging, and padding; every sentence should carry real
      information. Don't feel obliged to bolt a transition word onto every idea.
      Draw on specific examples and concrete analogies rather than generic
      explanations. Avoid academic filler like "delve", "explore", or "unpack"
      unless it's genuinely the best word. Write with the confidence of someone
      who actually knows this code, not someone carefully balancing viewpoints,
      and don't qualify every statement with politeness markers.
    - **Quick before/after to calibrate the register:**
      - Robotic: `The repository pattern provides an abstraction layer that
        decouples the persistence mechanism from the consuming code.`
      - Coffee-chat: `The repository is a thin wall between the rest of your code
        and the database. Code on this side asks for records; it never has to
        know they're sitting in SQLite.`
      - Robotic: `This approach offers several benefits in terms of testability
        and maintainability.`
      - Coffee-chat: `The nice part is testing. Swap in a fake repository and the
        layers above don't notice the difference.`
- **Flow and transitions (no abrupt stops).** The guide should read as one
  continuous lesson, not a stack of disconnected fragments. Connect the parts:
  - **Within a chapter**, let each section lead into the next. When a section
    builds on something just established, say so in a sentence rather than
    restarting cold. Don't end a section on a bare code block or a single
    abrupt line; add a sentence or two that interpret what the reader just saw
    and point to what's coming.
  - **Across chapters**, open each chapter by briefly orienting the reader
    relative to what came before (what they've built or learned so far, and how
    this chapter fits), and close it with a short bridge to the next chapter so
    the hand-off feels deliberate. Keep these intros and outros to a sentence or
    two; they should orient, not pad.
  - Replace generic transitions ('furthermore,' 'moreover') with natural 
    connection words ('though,' 'still,' 'actually').
  - Feel free to occasionally start sentences with 'But' or 'And' if it flows 
    naturally.
  - The first chapter has nothing before it and the last has nothing after, so
    skip the backward/forward bridge that doesn't apply.
- **No em-dashes in generated content.** Do **not** use em-dashes (—) anywhere in
  the rendered guide — not in titles, subheads, prose, cards, modals, or captions.
  Rewrite using a comma, parentheses, a colon, or two separate sentences instead.
  (Hyphens in compound words and code are fine; this rule is about the em-dash.)
- **Code in code blocks.** Use `<pre class="codeblock"><code>…</code></pre>` for
  multi-line code and inline `<code>` for short snippets, wherever applicable.
  Keep code generic (use the generalized names).
  - **Syntax highlighting.** Tag each multi-line block with the snippet's language
    so the bundled highlighter (highlight.js) colors it:
    `<pre class="codeblock"><code class="language-csharp">…</code></pre>`.
    Use the matching token, e.g. `language-csharp`, `language-javascript`,
    `language-typescript`, `language-python`, `language-java`, `language-go`,
    `language-bash`, `language-json`, `language-xml` (for HTML/XML/`.csproj`),
    `language-css`, `language-sql`, `language-yaml`. If the language is unknown or
    not one of highlight.js's common languages, **omit the class** and auto-detection
    handles it. Always keep code **HTML-escaped** (`<`→`&lt;`, `&`→`&amp;`).
  - **Titlebar + copy + scroll (automatic).** Keep authoring plain
    `<pre class="codeblock"><code>…</code></pre>`. At runtime `guide.js` wraps each
    block in a macOS-style titlebar (traffic-light dots) with a right-aligned **Copy**
    button that copies the code to the clipboard, and the block scrolls horizontally
    (never word-wraps) when a line is wider than the column. Do not hand-author the
    titlebar or wrapper markup.
- **Interactive cards.** Use `.info-card` (in `.card-grid`) for important callouts;
  they have reactive hover effects already. For the **Appendix: Additional Reading**
  chapter, use `.resource-card` inside `.resource-list` instead: these are full-width cards
  stacked one per row, sized to the content column, so long URLs wrap inside the
  card rather than overflowing it. The architecture chapter uses clickable
  `.arch-node`s (graph nodes) → `.modal`.
- **Dot-fade / binary-fade decorative section (opt-in).** The default stylesheet ships
  two optional decorative treatments that share a left-to-right gradient base with a
  pattern that fades in toward the right: `.dot-fade` overlays a navy **dot-matrix**,
  and `.binary-fade` overlays a tiled monospace pattern of **1's and 0's** (binary
  data). The **background bleeds to the full page width** while the
  section's content stays put in the reading column (the full-bleed is painted by a
  `::before` layer, so you don't restructure or move the content). Use them **only when
  the user explicitly asks** for one on specific section(s); they are never the default,
  and pattern/architecture sections keep their normal styling. Add `class="dot-fade"`
  (or `class="binary-fade"`) to a
  `<section class="chapter-section">`. For the **text-left / pattern-right** layout, nest
  a `.dot-fade__grid` (or `.binary-fade__grid`) with the reading copy in
  `.dot-fade__main` (left) and a small
  decorative element (a `.pull-quote`, stat, or graphic) in `.dot-fade__aside` (right),
  where the pattern is densest. It collapses to a single column on narrow screens. Minimal
  shape:
  ```html
  <section class="chapter-section dot-fade">
    <div class="dot-fade__grid">
      <div class="dot-fade__main">
        <header class="section-heading"><h2>…</h2><p class="section-subhead">…</p></header>
        <div class="prose"><p>…</p></div>
      </div>
      <aside class="dot-fade__aside"><blockquote class="pull-quote">…</blockquote></aside>
    </div>
  </section>
  ```
  Keep real content in `.dot-fade__main`; the pattern is purely decorative (the aside
  may be `aria-hidden="true"` when it carries no meaningful text). For `binary-fade`,
  swap the `dot-fade*` class names for their `binary-fade*` equivalents.
- **Architecture node graph.** Render the architecture as a left-to-right layered
  **node graph**, not a flat card grid:
  - Each component is an `.arch-node` button (unique `id`, `data-modal` → its detail
    `.modal`) placed in an `.arch-layer` column; sources on the left, dependents to the
    right.
  - Declare relationships in a hidden `<ul class="arch-edges">` of
    `<li data-from="node-a" data-to="node-b" data-label="imports">`. `guide.js` draws
    non-overlapping SVG arrows; `data-label` is printed on each edge to name the
    relationship. `guide.js` constrains each label to the gap between its two nodes
    and wraps it onto multiple lines so it never overlaps the nodes or other text,
    but **keep `data-label` values short** (a few words) so they stay readable.
  - **Auto-fit & centred.** `guide.js` measures the graph and, if it would be wider
    than the content column, scales the whole graph (nodes + edges together) down so it
    always fits — it never scrolls. The graph is centred in the column. You never set a
    width or scale by hand; just keep graphs readable by grouping (below).
  - **Avoid overlapping edges by grouping.** If the graph is busy enough that arrows
    would have to cross, collapse the dense region into a **system node**
    (`.arch-node--system`). Its detail modal embeds a nested
    `<div class="arch-graph arch-graph--nested">` showing only that system's internal
    components and their edges. In the main graph the system node keeps **one
    general-purpose (aggregated) edge** — mark it `data-aggregate` — to each external
    node it relates to.
  - Contracts: every edge `data-from`/`data-to` matches a node `id` in the same graph;
    every node `data-modal` has a matching modal `id`; every system node's modal
    contains a nested `.arch-graph`. Use general-purpose names only.
- **Fly-out Table of Contents.** Present on every page (the vertical **Contents**
  button on the left that reveals the panel on hover/focus/click).
- **Light/dark theme toggle.** A sun/moon button sits at the far right of the site
  header (in `.site-header__right`, after the meta text). `guide.js` toggles a
  `data-theme="dark"` attribute on `<html>` and persists the choice in
  `localStorage` (`guide-theme`); a small synchronous script in each page `<head>`
  re-applies the saved theme before paint to avoid a flash. Light is the default
  and the OS setting is ignored. Dark colors come from the
  `html[data-theme="dark"]` token block in the CSS; **code blocks are intentionally
  identical in both themes** (do not theme the `--code-*` tokens). Keep both the
  header button markup and the `<head>` init script on every page.
- **Footer prev/next.** Present on every page; each button labeled with the adjacent
  chapter's number **and** title; Previous left-aligned, Next right-aligned.
- **Accessibility.** Keep the skip link, `role="dialog"`/`aria-modal` on modals,
  `aria-label`s, and don't remove the reduced-motion / print guardrails in the CSS.
- **Offline.** No `http(s)://` asset references anywhere; everything lives in `assets/`.

---

## 8. Placeholder reference

`page-template.html`: `{{PAGE_TITLE}}`, `{{CHAPTER_NUMBER}}`, `{{CHAPTER_TITLE}}`,
`{{CHAPTER_SUBHEAD}}`, `{{ASSETS}}`, `{{TOC_LINKS}}`, `{{SITE_TITLE}}`,
`{{CHAPTER_BODY}}`, `{{PREV_HREF}}`, `{{PREV_NUMBER}}`, `{{PREV_TITLE}}`,
`{{NEXT_HREF}}`, `{{NEXT_NUMBER}}`, `{{NEXT_TITLE}}`, `{{FOOTER_TEXT}}`.

`toc-template.html`: `{{SITE_TITLE}}`, `{{GUIDE_TITLE}}`, `{{GUIDE_SUBHEAD}}`,
`{{ASSETS}}`, `{{TOC_LINKS}}`, `{{TOC_ENTRIES}}`, `{{FOOTER_TEXT}}`.

Replace **all** of them; none may remain in a finished page.

---

## 9. Generated site layout (reference)

```
<parent>/development-pattern-guide/
├── index.html                         (Table of Contents)
├── 01-introduction.html
├── 02-sourced-repository.html         (real source repo — real identifiers)
├── 03-prerequisites.html
├── 04-high-level-architecture.html    (node graph → modals)
├── 05..NN-<pattern chapters>.html     (learn-by-doing)
├── <NN>-extending-the-system.html
├── <NN>-deployment.html               (when applicable)
├── <NN>-appendix-additional-reading.html  (absolute last)
├── guide.json                         (manifest — source of truth)
└── assets/
    ├── default-global.css  (or the user's style-guide.css)
    ├── guide.js
    ├── vendor/  (highlight.min.js + HIGHLIGHTJS-LICENSE — offline syntax highlighting)
    └── fonts/  (bundled WOFF2 + FONTS.md)
```
