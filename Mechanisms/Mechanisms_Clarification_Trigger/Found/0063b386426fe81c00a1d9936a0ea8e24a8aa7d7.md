---
name: vibe.engineer
description: Engineer Mode — produce a set of well-shaped beads issues for multi-step work. Does NOT execute; ends with a handoff to /vibe.execute.
argument-hint: [brief description of the work to plan]
allowed-tools: Bash, Read, Glob, Grep, Agent, AskUserQuestion, Skill
---

*Principles: 1, 2, 4 strong; 3 n/a (no code edits). See CLAUDE.md § First Principles.*

# Engineer Mode

Target: $ARGUMENTS

For work that requires more than 3 subtasks. Output is **beads issues**, not code. Execution happens via `/vibe.execute`. Entry points:

- New session with a task too big for Express Mode.
- Follow-up to `/vibe.express` or `/vibe.explore`.

Refuse to proceed if SessionStart status ≠ `beads: ready`.

## 1. Clarify before planning [P1]

Ask the user clarifying questions until scope, constraints, and definition of done are unambiguous. Specifically confirm:

- What problem is being solved and why now.
- The boundary between in-scope and out-of-scope.
- Hard constraints (deadlines, compatibility, cross-team deps).
- What "done" looks like — the user-observable outcome.

Do not skip [P1]. If the user's answers reference parts of the codebase you're unfamiliar with, dispatch `explore-scout` before step 2.

## 2. Build the minimal graph [P2]

Smallest graph that correctly captures the work. The graph is a contract with the executor.

Available node types (use only what the work requires):

- **Task** — default unit of executable work. One task = one worker dispatch ≈ one PR. Always needs concrete AC and a Verification step.
- **Epic** — multiple independent groupings that may span sessions or ship partially.
- **Feature/Story** — distinct capabilities that usefully group tasks. Omit if grouping adds no information.
- **Subtask** — sequential implementation steps that benefit from independent tracking.

Every work node (task, subtask) must have concrete AC and a Verification step **[P4]**. Context nodes (epics, features) describe the "why" — no Verification needed but must have clear context.

## 3. Verify the plan with the user

Show the full hierarchy with proposed titles and dependency links. Get explicit approval before creating issues. Iterate if the user pushes back.

## 4. Create beads issues

Create issues **one at a time** — invoke `/vibe.bd-new` sequentially, waiting for each ID before the next. Do NOT batch (`bd` CLI lock — concurrent calls fail).

Parallelism belongs in the **dependency graph**, not creation. Shape the graph so independent leaves have no `--deps` between them — `/vibe.execute` fans them out to `beads-worker` subagents automatically.

Each issue must ship with the full Issue Shape (context, AC, out of scope, verification, dependencies). Do not batch-create skeletons and backfill.

Link dependencies with `bd dep add` as you go, or pass `--deps` at creation. For Epics use `--type epic`, Stories `--type feature`, Tasks `--type task` (default). Use `--parent <epic-id>` for hierarchy.

Beads must be sufficiently shaped that a new agent could `/vibe.execute` to pick up without further clarification.

### Optional: model-routing hint per work issue

You have actual code context while shaping — better positioned than Execute to judge complexity. For each work node, classify per the rubric (see execute.md § Model-tier rubric) and (if confident) record via:

```
bd create --labels model:<tier>
```

Plus a one-line justification in notes: `**Suggested model:** sonnet — single-file edit, well-bounded`. Context nodes get no model labels. See execute.md § Model-hint convention for orchestrator behavior.

## 5. Hand off

Once the plan and issues exist, do NOT start implementation in this session. Ask the user:

> The plan is filed as `{epic-id}` with N child issues. My current context is at `{/context}`, would you like to:
>
> 1. Invoke `/vibe.execute` now?
> 2. Compact, and then let me invoke `/vibe.execute`?
> 3. Pause here so a future session can pick up from the beads queue?

Wait for a direct instruction before writing any code.
