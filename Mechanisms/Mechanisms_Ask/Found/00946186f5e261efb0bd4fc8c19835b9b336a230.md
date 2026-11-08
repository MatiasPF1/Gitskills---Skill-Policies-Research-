---
description: Implement a small net-new feature end to end without a plan artifact, with full per-file integrity gates
argument-hint: <one-line feature description>
model: sonnet
effort: xhigh
disable-model-invocation: true
---

## When to use this

Small net-new work where a full `/flow-preflight` -> `/flow-plan` -> `/flow-implement` -> `/flow-review` cycle is overhead, but the per-file integrity gates still apply and the work should hard-stop if it outgrows its premise.

Use `/flow-fix` instead when the trigger is a failing signal (test, type error, runtime, lint).
Use the full `/flow-*` cycle when the work involves a design choice worth recording, more than 5 files, a new module or component, or any change to a public API.

## Procedure

1. Read $ARGUMENTS. State the feature in one sentence in your own words to confirm understanding. If $ARGUMENTS is missing or ambiguous beyond one focused clarifying question, stop and ask.
2. Identify the files the change will touch. Read them before editing. If the target files cannot be identified from $ARGUMENTS alone with one quick search, stop and escalate to `/flow-plan`.
3. Load the patterns skill for the stack if the change is stack-specific.
4. State the approach in one sentence before changing anything: which files, what each gets, what the verification will be. This is the no-artifact equivalent of a plan; it lives in the chat, not in `~/.claude/scratch/`.
5. Make the changes. After each file, apply the code-level integrity gates from `/flow-implement`:
   - Match existing style, naming, and patterns. Read a nearby file first if unsure.
   - Cohesion: each function does one thing; if the function name needs an "and", split it.
   - Coupling: a new module depends on the fewest concrete other modules possible. If a new file imports more than five non-stdlib modules, name why.
   - Naming: names describe what, not how. `processItems` is weak; `validatePaymentBatch` is concrete.
   - Magic values: literal numbers or strings beyond 0, 1, -1, "", and obvious enums get a named constant with a comment explaining the value.
   - Single source of truth: a piece of data lives in one place. If you find yourself synchronizing two stores, stop and surface.
   - Comments: explain why, not what. Remove comments that paraphrase the next line.
   - Do not refactor unrelated code.
   - Do not upgrade or add dependencies unless the approach statement in step 4 explicitly includes them.
6. Run narrow verification: type check on the touched files, the closest tests, the project's linter on the touched files. Do not run the full suite; that is `/flow-checks` territory.
7. Self-check before reporting: would a senior reviewer accept this on first pass? If no, fix it before reporting.

## Hard stop conditions

Stop immediately and escalate to `/flow-plan` (do not continue, do not silently expand) if any of these become true during execution:

- The change touches more than 5 files.
- The change requires creating a new module, component, route, or top-level directory.
- The change touches a public API surface (exported types, exported functions, route handlers, public component props).
- The change requires editing project-level config (`tsconfig`, `next.config`, `eslint.config`, `package.json` scripts, CI workflows, `settings.py`, equivalents).
- The work reveals a design choice worth recording (more than one viable approach, tradeoffs worth naming).
- A drive-by fix becomes load-bearing for the feature. Note the drive-by, do not absorb it; escalate.

The stop is hard. Do not rationalize past it because the remaining work is "short" or "obvious" or "thematically related". If the premise of `/flow-quick` no longer holds, the right answer is `/flow-plan`, not a stretched `/flow-quick`.

## Output

Terminal only. No scratch artifact.

- One-sentence restatement of what was built.
- Files changed (path list).
- What each change accomplishes (one line each).
- Verification result: pass, fail, not run, with the commands run.
- Anything deferred: drive-bys noticed, follow-ups surfaced, edge cases that warrant a real test pass via `/flow-test`.

## Scope and discipline

- The one-line feature description in $ARGUMENTS is the scope anchor, the same role the plan artifact plays in `/flow-implement`. Stay within it.
- If the approach statement in step 4 turns out to be wrong once editing begins (a target file does not contain what was assumed, an API does not match memory), stop and surface. Do not pivot silently.
- Quality gates are not optional under time pressure. If verification fails, fix it or report the failure and stop. Do not declare the task complete with failing checks.
