---
name: statedd-protocol
description: >
  Enforces the StateDD truth-first workflow for repo governance: read-order
  discipline, backlog currency, evidence capture, browser verification,
  screenshots, clean worktree closure, docs sync, and honest handoffs. This
  skill is mandatory for every SupportPlane coding-agent session.
---

# StateDD Protocol Skill

## Activation

This skill applies to every SupportPlane coding-agent session. It is loaded
automatically via `instructions` in `.opencode/opencode.json`.

## Mandatory Session Start

1. Read these files in order:
   - `AGENTS.md` — session contract and universal rules
   - `STATUS.md` — human truth snapshot
   - `PROJECT_STATE.yaml` — structured truth
   - `PROJECT_DNA.yaml` — architecture contract
   - `NEXT_ACTIONS.md` — active queue
2. Read `BACKLOG.md` and `WORKLOG.md` when planning or reviewing history.
3. Read `PROJECT_ADAPTER.yaml` when stack/port/integration details matter.
4. Summarize current truth before making any edit.

## Mandatory Behaviors

### Truth Discipline

- Never claim completion from code changes alone.
- User-facing behavior requires direct runtime verification.
- Negative searches stay negative: use `not found`, `not currently locatable`,
  or `not proven`. Never claim absence proven by search alone.
- Mark unknowns honestly with claim-state labels:
  `observed`, `unknown`, `reported`, `blocked`, `assumed`, `stale`, `invalid`.

### Evidence Capture

- Every user-visible change requires browser verification or test output.
- Evidence is not optional. "I'll do it later" or "the user didn't ask" is not
  acceptable.
- Each backlog item gets exactly one evidence folder under `output/playwright/`.
- Folder names use the next sequential session number (e.g., `session-128-...`),
  never raw BL numbers.
- Max 20 files per evidence folder. Verify with `ls <folder> | wc -l`.
- No redundant `.html` wrappers.
- Delete superseded evidence folders for the same backlog item.

### Browser Verification

- Use Playwright MCP for user-visible behavior verification.
- Capture screenshots that show distinct states, interactions, or panels.
- Viewport-only captures preferred; full-page only when vertical context matters.
- Each screenshot filename must describe visible content.
- Run duplicate detection after capture (`md5sum`), report results.
- Commit the reproducible screenshot script.

### Code Quality

- Before closure, run relevant lint/typecheck/tests:
  - `npm run lint`
  - `npm run typecheck`
  - `npm test` (workspace-scoped)
- Never introduce secrets or credentials to code or model context.
- Prefer small, reversible patches.
- Follow existing code conventions (imports, naming, patterns).

### Docs Sync

- Update state docs to match actual truth.
- `BACKLOG.md` must have honest status markers for affected items.
- `NEXT_ACTIONS.md` must remove closed items, add new items.
- `STATUS.md` updated if project state changed.
- `PROJECT_STATE.yaml` updated if structured truth changed.
- `docs/EVIDENCE_LOG.md` updated if evidence captured.
- `docs/README.md` updated if docs added/removed/reorganized.
- No stale claims, TODO drift, or contradicted states.

### Clean Worktree

- Ensure `git status --short --branch` is clean before closure unless user
  explicitly asked not to commit.
- Never commit secrets, `.env`, or output/ directories.

### Closure Gate

Refuse closure if:

- Runtime identity, docs, evidence, or tests contradict the claim.
- Required browser-proof states from the prompt are missing.
- Any `501 Not Implemented` stub is presented as complete without honest labeling.
- Database schema drift exists without committed migrations.
- Validation gates report incomplete (missing exact commands, pass/fail counts).
- Any required section of the final handoff report is missing.

## Final Handoff Report Structure

Every session must end with these 7 sections:

1. **Commits** — full hashes for all commits in the slice
2. **Worktree** — `git status --short --branch` output
3. **What Changed** — concise bullet list
4. **Verification** — exact commands and pass/fail results (counts, not "tests pass")
5. **Evidence Inventory** — folder path, file count, numbered list mapping files to states
6. **Risks and Limitations** — honest list of what is NOT implemented
7. **Next Recommended Action** — one concrete next step or backlog item

Use `prompts/FINAL_HANDOFF_TEMPLATE.md` for canonical shape.

## Services and Ports (SupportPlane)

Keep these in mind during verification:

- Web UI: `localhost:3200` (Next.js)
- API: `localhost:4110` (NestJS)
- Database: PostgreSQL on host port 5434
- MinIO: S3-compatible object storage
- NATS: message queue

Leave services running only if project rules say that is preferred.
