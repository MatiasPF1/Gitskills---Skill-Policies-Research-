---
name: subagent-orchestration
description: Use when a coding task may benefit from Pi subagents for recon, planning, implementation, review, or summarization. Teaches the parent agent to dispatch subagents in fresh, isolated contexts with an explicit handoff contract, scale effort to complexity, and synthesize — never duplicate — subagent work.
---

# Subagent Orchestration

## Purpose

The parent agent is the **orchestrator**. It does not read files, run searches, or write code
itself; it decomposes the task, dispatches subagents in **isolated, fresh contexts**, evaluates
the results against an explicit handoff contract, and synthesizes the answer for the user.

Subagents exist to (a) keep the parent's context clean, (b) get role-appropriate tool sets and
thinking budgets, and (c) get an adversarial second opinion on non-trivial work. They are not a
way to push the parent's hard work into a side window.

## The Hard Rule: Context Isolation

Every subagent dispatched by the orchestrator runs in a **fresh context window** with:

- **no parent conversation** — `inherit_context: false` is mandatory on every agent template;
- **no shared state with siblings** — sibling subagents do not see each other's outputs;
- **no implicit access to the user's full conversation** — if a subagent needs task context,
  the orchestrator passes it in the structured handoff contract, not via context inheritance.

If `inherit_context: true` appears on any agent template, it is a bug. Audit and fix before
dispatch. If the harness does not support `inherit_context`, set it explicitly anyway so the
contract is documented.

## The 5 Orchestrator Responsibilities

1. **Select dynamically.** Do not run the full pipeline for trivial queries. A 1-tool-call
   lookup does not need a planner, a worker, and a reviewer. Match the pipeline to the task.

2. **Partition the problem space deliberately.** If the task has N distinct aspects, the plan
   must address all N with no gaps. Partitioning by role is not enough — partition by
   *concern* and verify the union of partitions covers the original request.

3. **Scale effort to complexity.** Encode explicit rules:

   | Task shape | Pipeline |
   |---|---|
   | Simple fact-finding / 1-tool lookup | 1 scout, 0–1 reviewer, no planner overhead |
   | Multi-step single-domain work | planner → worker → reviewer |
   | Breadth-first / parallelizable / multi-domain | planner → N parallel specialists (each in its own worktree or scope) → integrator/reviewer |
   | Long-running, high-stakes change | planner → N workers in serial phases → reviewer per phase → final integrator |

   Do not burn 15× tokens on a 1-tool-call lookup. Do not skip a reviewer on a multi-file
   refactor.

4. **Evaluate the synthesis before returning.** Before handing the result back to the user, the
   orchestrator must check:
   - **Coverage** — every part of the original request is addressed.
   - **Validity** — subagent output is judged against the contract, not trusted on faith.
   - **Consistency** — sibling subagents that touched overlapping concerns agree.

5. **Pass context explicitly, every time.** The subagent only knows what is in the task prompt.
   Missing a critical detail is the orchestrator's failure, not the worker's. The contract
   template below is the only sanctioned way to pass context.

## Subagent Chaining Rule

Decomposition is the orchestrator's job. The chain runs **`orchestrator → subagent → orchestrator → subagent`**, never `subagent → subagent`.

A subagent must never spawn, dispatch, or invoke another subagent. If a subagent's task
discovers work that needs a different role, it reports the gap back to the orchestrator in its
output and the orchestrator decides what to dispatch next.

This rule is encoded as a **forbidden action** in every agent template.

## The Structured Handoff Contract (Mandatory)

Every dispatch from the orchestrator to a subagent must include a handoff contract built from
this template. Fill every field. If a field does not apply, write `n/a` and explain why —
do not omit it.

```text
## Handoff Contract

### Objective
<one or two sentences: what success looks like>

### Context (passed by orchestrator)
- Repo / working dir: <path>
- User goal: <restatement in your own words>
- Prior phase outputs: <paths to artifacts, or one-line summaries>
- Constraints / user-specified tech: <bullets — frameworks, libraries, versions, "do not use X">
- Reference material: <file paths the subagent should read; do not paste contents>

### Scope Boundary
- In scope: <paths, globs, concerns>
- Out of scope: <paths, globs, concerns>
- If you must expand scope, STOP and report why — do not silently broaden.

### Allowed Tools
<explicit list. Examples:>
- read-only: read, bash (for rg/git/find only), grepsearch, websearch, web_fetch, codesearch, context7
- implementer: + edit, write
- never grant a scout write tools, never grant a reviewer write tools

### Forbidden Actions
<explicit list. Examples:>
- do not write or modify any file
- do not spawn or invoke another subagent
- do not edit files in <list>
- do not run destructive commands (rm -rf, force push, etc.)
- do not substitute the user-specified technology with an alternative

### Output Schema
<exact structure the subagent must return. See per-role schemas below.>

### Success Criteria
<bulleted list the orchestrator will use to judge the output. Each item must be checkable.>

### Length budget (Summarizer only; n/a otherwise)
<target word count, e.g., 500 words, or "1 paragraph">

### Audience (Summarizer only; n/a otherwise)
<who reads the summary, e.g., "engineering lead" or "user via UI">

### Fallback Behavior
- If blocked: <report blocker + partial findings; do not fabricate a workaround>
- If out of scope: <report the gap and stop>
- If ambiguous: <state the ambiguity, list the interpretations you considered, pick the safest, explain>
- If input contract is incomplete: <REFUSE — see refusal guard below>

### Artifact Path (if output is large or shared with other subagents)
- Write full output to: <absolute path>
- Return to orchestrator: one-line summary + path
```

### Per-Role Output Schemas

The `Output Schema` slot is filled with one of these role-specific structures.

**Scout (read-only recon):**
```text
## Findings
- <file:line> — <fact, 1 line>

## Open questions
- <question that this recon could not answer>

## Confidence
- high | medium | low — <one-line reason>

## Tool calls used
- <count>
```

**Planner (phased plan, no edits):**
```text
## Plan
### Phase 1: <name>
- Steps: <numbered bullets>
- Files touched: <list>
- Verification: <how to check this phase>
### Phase 2: <name>
...

## Spec compliance
- User specified: <tech> — plan uses: <tech> — pass | flag

## Risks
- <risk — mitigation>

## Open questions
- <question for the user or for a follow-up scout>
```

**Worker (bounded implementation):**
```text
## Files changed
- <path> — <one-line what changed>

## Acceptance criteria
- [x] <criterion> — <evidence: file:line, command output, etc.>
- [ ] <criterion not met> — <reason>

## Tests / checks run
- <command> — <result>

## Follow-ups / risks
- <item>

## Spec compliance
- User specified X — implementation uses X — pass | fail
```

**Reviewer (read-only validation):**
```text
## Specification compliance
- <criterion>: pass | fail — <evidence>

## Spec adherence
- User specified: <tech> — worker used: <tech> — pass | fail

## Out-of-scope findings
- <observation> — note: not in contract, do not act on this

## Changed files reviewed
- <path> — <one-line observation>

## Bugs / regressions
- <bug — file:line — severity>

## Missing edge cases
- <case>

## Verdict
PASS | FAIL — <one-line summary>
```

**Summarizer (compress prior outputs):**
```text
## Summary
- <bullet — preserves action items verbatim>

## Key artifacts
- <path> — <one-line what it contains>

## Decisions captured
- <decision — rationale>

## Open threads
- <item still in flight>

## Lost detail (call out, do not silently drop)
- <category of detail the source contained that the summary does not cover>
```

## Filesystem-Based State

When subagent output is too large to inline, or when multiple subagents need to coordinate on
a shared artifact, the orchestrator passes **paths**, not contents.

- The orchestrator declares an `Artifact Path` in the handoff contract.
- The subagent `write`s the full output to that path and returns a one-line summary + the path.
- The orchestrator (or the next subagent) reads the path when it needs the full content.
- Originals are kept alongside summaries so context loss is recoverable.

Use filesystem state when:

- The subagent output exceeds ~50 lines or includes diffs, logs, or structured data.
- Two or more subagents need to share an intermediate result.
- A long-running work item needs to survive a context truncation.

Do not use filesystem state for small inline answers — it adds a round trip with no benefit.

## Effort Sizing

| Role | Default `max_turns` | Tool budget | When to scale up |
|---|---|---|---|
| Scout (1 file, 1 question) | 3 | 1–3 tool calls | Never — split into multiple scouts if scope is wider |
| Scout (bounded area) | 8 | 5–10 tool calls | Architecture review with multiple files |
| Planner | 8 | Read-only | Multi-component changes with cross-file dependencies |
| Worker | 25 | Edits + tests | Bounded file list, clear acceptance criteria |
| Reviewer | 10 | Read-only | Phased work or a long diff |
| Summarizer | 5 | Read-only | Long log, multi-phase synthesis |

If the scope is broader than these budgets allow, **split the contract** — do not just raise
`max_turns`. A stuck agent is usually an over-scoped agent.

For read-only scouts, dispatch with the smallest available model that can reliably answer the
question. Larger models do not improve single-file lookups; they only add latency and cost.

## Parallelization Rules

> This section uses the Codex adapter / Pi harness API (specifically `run_in_background: true` and `get_subagent_result`). Adapt the API calls to your harness equivalents if you are not on the Codex adapter / Pi.

Parallelize only **independent** subagent dispatches. Two subagents are independent when their
contracts have no shared files, no shared artifact, and no causal dependency on each other's
output.

**Do not parallelize:**

- a worker writing code before scout/planner results are synthesized;
- multiple agents editing the same file or even the same logical concern;
- a scout on file A and another scout whose answer depends on A's output;
- parent doing the same exploration while a scout is running.

**Parallel launch pattern** (when independent):

```text
// Launch all in one tool block with run_in_background: true
subagent({ prompt: <contract>, subagent_type: "scout", model: "<small read-only model>", max_turns: 3, run_in_background: true })
subagent({ prompt: <contract>, subagent_type: "scout", model: "<small read-only model>", max_turns: 3, run_in_background: true })

// Then in the next tool block, wait on all in parallel
get_subagent_result({ agent_id: "<id-1>", wait: true })
get_subagent_result({ agent_id: "<id-2>", wait: true })
```

Always pair parallel dispatch with a `max_turns` cap so a stuck agent cannot blow the budget.

## Anti-Patterns (Hard "Do NOT" List)

The orchestrator must not:

- **Context Telephone** — pass summaries-of-summaries across handoffs. **Mitigation:** every
  handoff uses the structured contract above; originals (paths to source artifacts) are
  available alongside any summary.
- **God Agent** — pack research, plan, implement, test, and review into one subagent.
  **Mitigation:** phase decomposition; each agent owns exactly one role with one output schema.
- **Context Stuffing** — overload a subagent with all docs, the whole repo, or a wall of past
  conversation. **Mitigation:** apply the five-strategy framework — *select* the smallest
  relevant slice, *compress* to paths + one-line summaries, *order* by what the agent reads
  first, *isolate* by passing one concern per dispatch, *format* with the contract schema.
- **Premature Parallelization** — run dependent tasks in parallel. **Mitigation:** map the DAG
  first; only dispatch independent contracts concurrently.
- **Silent Failure Cascade** — let one phase's failure propagate to the next.
  **Mitigation:** phase-gate validation. After every subagent returns, the orchestrator judges
  the output against `Success Criteria` and either accepts, reruns a narrower contract, or
  surfaces the gap to the user. Never proceed on "the worker said it was done".
- **Scope Creep Spiral** — a subagent expanding scope until context exhausts.
  **Mitigation:** explicit `Scope Boundary` and `Acceptance Criteria` in every contract; the
  refusal guard below forces a stop when scope is exceeded.
- **Subagent Spawning Subagents** — a worker or scout dispatching its own sub-subagents.
  **Mitigation:** the chain rule above; this is encoded as a forbidden action in every
  agent template.

The orchestrator's most common failure mode is the first one: duplicating delegated work in
the parent because the contract was too loose. If a subagent result looks weak, narrow the
contract and rerun — do not start reading the same files in the parent.

## Per-Role Refusal Guards

Every agent template includes a refusal guard: if a required input is missing, the agent
must **refuse and ask** instead of producing reasonable-but-wrong output. The orchestrator
treats a refusal as a contract defect, not a worker failure, and fixes the prompt.

Examples:

- Scout with no path or no question → refuse: "Need a file path and a specific question."
- Worker with no acceptance criteria → refuse: "Need at least 3 checkable acceptance criteria."
- Reviewer with no changed-files list → refuse: "Need the list of files to review."
- Planner with no user goal → refuse: "Need a one-sentence user goal to plan against."

## Specification Adherence

User-specified technologies, languages, frameworks, libraries, and approaches are hard
constraints. Every worker and reviewer contract must echo them in `Constraints` and the
reviewer must fail the work if substitution occurred.

Common failure: a worker swaps the requested tool or stack for its own preference. The
contract must forbid the substitution explicitly and the reviewer must check.

## Failure Handling

When a subagent returns a partial result, the orchestrator chooses one path:

1. **Rerun narrower** — re-dispatch with a tighter contract (smaller scope, more specific
   question, lower `max_turns` cap).
2. **Escalate to user** — surface the gap and ask the user how to proceed.
3. **Switch to manual** — proceed in the parent, but only after announcing the switch and
   keeping parent exploration minimal.
   - Switch to manual **only** for trivial follow-ups (single short answer, single file read
     for a sanity check).
   - For anything bigger, re-dispatch a narrower contract or escalate to the user.
   - The orchestrator must not re-do the subagent's task in the parent. The contract template
     and the orchestrator's role forbid this.

Never silently ignore a weak subagent result and never duplicate the full subagent task in
the parent.

## Validation Checklist (Before Returning to User)

- [ ] Every dispatched subagent ran with `inherit_context: false`.
- [ ] Every handoff contract had all eleven fields filled (Objective, Context, Scope Boundary,
      Allowed Tools, Forbidden Actions, Output Schema, Success Criteria, Length budget, Audience,
      Fallback Behavior, Artifact Path).
- [ ] Subagent outputs were judged against `Success Criteria`, not trusted on self-report.
- [ ] Coverage check passed — every part of the original request is addressed.
- [ ] No subagent spawned another subagent.
- [ ] Scope was not silently broadened in any phase.
- [ ] User-specified tech was preserved (worker did not substitute, reviewer checked).

## Sources

- OpenAI Codex: Subagents — `https://developers.openai.com/codex/concepts/subagents`
- Claude Code: Create custom subagents — `https://code.claude.com/docs/en/sub-agents`
- Claude Code SDK: Subagents — `https://code.claude.com/docs/en/agent-sdk/subagents`
- Claude Code: Dynamic workflows — `https://code.claude.com/docs/en/workflows`
- Anthropic: How we built our multi-agent research system — `https://www.anthropic.com/engineering/multi-agent-research-system`
- Anthropic: Building effective agents — `https://www.anthropic.com/research/building-effective-agents`
- Anthropic: Effective context engineering for AI agents — `https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents`
