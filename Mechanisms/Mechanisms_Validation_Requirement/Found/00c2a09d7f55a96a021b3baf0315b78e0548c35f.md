---
name: verify-and-report
description: >-
  The completion gate: before declaring done, re-read the diff as a hostile
  reviewer, run the project's real build/lint/test gates after the last
  edit, exercise the actual behavior, then write a report where every claim
  traces to something observed this session. Use before declaring any
  coding task complete, before writing a final summary, PR description, or
  status update, and whenever asserting "tests pass" or "this works".
  Keywords: done, verify, final check, summary, PR description, tests pass,
  self review, report.
license: MIT
metadata:
  author: jvenuto80
  version: "1.0"
  derived-from: adamentwistle/fable-skills (MIT)
---

# Verify and Report

Three habits separate a strong run from a weak one: claims are observed not
remembered, "done" is verified not felt, and the report matches the
evidence.

## 1. Evidence before assertion

Every load-bearing claim — a diagnosis, a location, a config value, a
behavior — must trace to a tool observation from **this session**. Not
training data, not memory, not "how these things usually work".

- "Function A calls B" → you read A's body. "The config is Y" → you read
  the config. "Tests pass" → you ran them after your last edit.
- **Docs and memory are hypotheses**: they describe what was true when
  written. Verify a flag/file/function still exists before recommending it.
- **Negative claims need double coverage**: "there is no X" requires at
  least two search strategies (different keyword, casing, directory).
- **Edits invalidate prior verification**: anything checked before your
  edit is stale after it. The verification that counts ran last.
- Can't verify? Say so explicitly ("I haven't verified this") — or go spend
  the one search it costs.

Anti-patterns: diagnosing from the error message without reading the code
path; trusting a function's name over its body; extrapolating one file's
pattern to the codebase; "should work" in place of running it.

## 2. The done gate

You are done when a hostile reviewer would find nothing — not when the edit
is written.

1. **Re-read the diff as that reviewer** (`git diff`): every hunk belongs
   to this task; renames reached every call site (search the old name →
   zero hits); no debug prints, swallowed errors, or types widened to
   compile; new code matches neighboring conventions.
2. **Run the project's real gates after the last edit** — build/typecheck,
   lint, tests, per the project's own commands (check AGENTS.md /
   package.json / Makefile). A gate run before your final change proves
   nothing.
3. **Exercise the behavior, not just the types**: run the affected test,
   hit the endpoint, load the page. Compilation proves well-formed, not
   correct. If you genuinely can't exercise it, the summary must say so
   plainly.
4. **Hunt your own edge cases**: empty/zero/null input, first-vs-repeat
   call, concurrent use, the error path (see edge-case-sweep). Considered
   consciously, not skipped.

Trivial changes still get the diff re-read and the relevant gate — no
change is too small to break a build.

## 3. Report what happened

The user reads one thing: your final message. Write it for a teammate who
stepped away.

- **Lead with the outcome** — what happened or what you found, first
  sentence. Bad news (failing tests, can't reproduce, blocked) leads too,
  never buried under process narration.
- **Claims match evidence, exactly**: "tests pass" names the suite and
  means after-the-last-edit. Distinguish verified / probable / assumed.
  Report failures and skips faithfully — hiding a skipped step costs 10x
  when discovered.
- **No invented shorthand**: no codenames from mid-task ("the v2
  approach"); each claim carries its context in place ("the retry loop in
  lib/queue.ts:80").
- **Selectivity, not compression**: cut what doesn't change the reader's
  next action; write what remains in complete sentences.

Final check: reread as the recipient. Anything they'd reread twice, ask "so
what happened?", or discover missing — fix before sending. A last paragraph
promising work ("I'll…") means you aren't done: do it now.
