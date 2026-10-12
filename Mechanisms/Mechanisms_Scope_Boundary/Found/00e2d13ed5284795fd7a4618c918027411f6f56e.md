---
name: devops-refactoring
description: >-
  Iteratively refactors the CI/CD pipeline and infrastructure-as-code the current branch
  (or a specified PR) adds or modifies, improving internal structure over small
  behaviour-preserving passes that keep
  the produced infrastructure and pipeline behaviour identical. Runs each pass against a
  known-green safety net (validate/plan/lint), guards against oscillation, caps at five
  passes, then prints a summary of the changes in the terminal. Use when the user asks to
  refactor or clean up the pipeline or infrastructure code of the current branch (or a PR)
  without changing what it deploys or runs.
---

# DevOps Refactoring skill

Act as a principal DevOps / platform engineer. You own the delivery path: CI/CD pipelines, infrastructure-as-code, deployment topology, and the cross-cutting concerns (secrets, least privilege, rollout safety, cost) that keep environments reproducible and safe. When you refactor, you improve the internal structure of workflows, modules, manifests, and templates while keeping the resulting infrastructure and pipeline behaviour identical.

Iteratively improve the internal quality of the pipeline and infrastructure code that the current branch (or a specified PR) adds or modifies **without changing observable behaviour**, over multiple passes until the code converges. Scope is strictly the change set — not a repo-wide cleanup. Local verification gates every pass; never apply infrastructure and never push changes.

**Focus primarily on delivery-path concerns**: pipeline/job structure, reusable workflow and module boundaries, variable and secret organisation, environment/stage parameterisation, template and manifest clarity, and provisioning-logic structure.

## Prime directive

**Behaviour must not change, on any pass.** The planned infrastructure (the `terraform plan` diff against the same state, rendered Helm/Kustomize output, generated manifests), the set of resources and their arguments, pipeline triggers, the job/stage graph and its ordering, the produced artifacts, secret and permission scopes, and the deploy targets must be identical before and after the entire loop. If an improvement requires a behaviour or contract change (a different plan, a renamed resource that forces replacement, a changed trigger) → hard stop.

## Loop termination — combined stop conditions

The loop ends when any of these is true:

1. **Quality floor reached** — a pass finds no remaining blocker/major refactor candidate. Target outcome.
2. **Max passes** — **5** passes completed. Hard ceiling.
3. **Diminishing returns** — a pass produces no change, or two consecutive low-value passes.
4. **Hard stop** (below) triggers.

Never continue "just to be thorough" past the quality floor.

## Anti-oscillation rule

Maintain a cross-pass **change log** (what each pass changed and why). Before applying any refactor, check it would not revert or thrash a prior pass's decision. If a later pass "wants" to undo an earlier one, stop and report.

## Hard stop conditions

1. A worthwhile improvement cannot be done without changing the plan/rendered output, a resource address (forcing replacement), the pipeline trigger/graph, or a permission scope.
2. Verification over the changed code is too thin to detect a behaviour change (no plan/render/lint is runnable) and a safe equivalence check cannot be established first.
3. A refactor would force changes outside the changed surface large enough to shift the scope/intent (e.g. a state migration / `terraform state mv` across many resources).
4. The loop is oscillating (anti-oscillation rule).
5. A refactor and a policy/architecture rule cannot both be satisfied and the resolution is a judgement call.

## Workflow

### Phase 1 — Scope & safety net (once)

- Default to the changes on the current branch: `git diff <baseBranch>...HEAD`, `git diff --name-only <baseBranch>...HEAD`. If a linked issue or PR is given instead, additionally use the `github-issue-read` skill for issue context and `gh pr view <n>` / `gh pr diff <n>` for the PR diff and review threads (refactor targets often live there).
- Define the **refactor surface**: the exact files/regions this change set adds or modifies (workflows, modules, manifests, templates, variable files). Everything else is off-limits except minimal unavoidable reference updates (counts toward hard stop #3).
- Note the policy conventions and quality gates near this code (`.tflint.hcl`, OPA/Conftest, actionlint, kube-linter, yamllint), the environments and backends it targets, plus the project's verification commands.
- Capture a **known-green baseline** with read-only commands: `terraform validate` + `terraform plan` (no apply), `helm template`/`helm lint`, `kustomize build`, `actionlint`, `yamllint`, policy checks. Save the rendered plan/output as the equivalence reference. Record it.
- If no read-only command can detect a regression for the changed code, establish a safe equivalence check first (e.g. diff rendered output before/after). If infeasible → hard stop #2.
- Initialise the cross-pass change log (empty).

### Phase 2 — The refactoring loop

Each pass:

**2a. Survey.** Within the refactor surface only, list candidate refactors with reason and severity: duplicated job/step/resource blocks that should be a reusable workflow, composite action, or module; poor names / leaky abstractions; overlong low-cohesion pipelines or monolithic modules; hardcoded values that belong in variables/inputs; copy-pasted per-environment config that should be parameterised; tangled conditionals and matrix logic; inline scripts that belong in a versioned file; dead jobs/steps/resources; weak module/stack boundaries; conformance gaps to Phase 1 policy conventions. Discard taste-only candidates. Cross-check each against the change log.

**2b. Decide.** No blocker/major candidate remains → record "quality floor reached" and end the loop. Otherwise pick the highest-value / lowest-risk candidates and sequence them (structural moves before dependent local cleanups).

**2c. Apply (one refactoring at a time).** For each candidate, in order:

1. Apply exactly that one named refactoring; keep it small and focused.
2. Run the full local verification. The plan/rendered output must stay **identical** to the baseline reference and all lint/policy gates green — a resource address or plan diff must not change. Do not re-target state or re-baseline the plan to make it pass.
3. If the plan drifts or a gate goes red: revert that single change, diagnose, redo correctly or drop the candidate. Never proceed on drift.
4. Commit per refactoring with a message naming it (e.g. `refactor: extract network module — no plan change`). Append to the change log.

**2d. Pass review (termination check).** End the loop if any termination condition holds; otherwise begin the next pass.

### Phase 3 — Cumulative equivalence review (once, after the loop)

Review the entire cumulative diff for hidden behaviour drift, with a delivery-path lens:

1. Planned infrastructure unchanged (same `terraform plan` diff against the same state, same rendered Helm/Kustomize/manifest output, no resource additions/removals/replacements).
2. Resource identity unchanged (no changed addresses/names forcing destroy-and-recreate; same providers, versions, and backends).
3. Pipeline behaviour unchanged (same triggers, same job/stage graph and ordering, same conditions reachable, same produced artifacts and their names).
4. Secret, permission, and environment scopes unchanged (same IAM/RBAC, same OIDC/token trust, same deploy targets).
5. No implicit dependency ordering silently altered; concurrency/rollout guards preserved.
6. No file outside the refactor surface changed beyond unavoidable reference updates.

Any drift → fix or revert, then re-run local verification.

### Phase 4 — Final report

Print a detailed refactoring report **as a summary in the terminal** — do not post it as a PR comment, write it to a local file, or leave a report artifact in the repo. Include:

1. Pass-by-pass refactorings from the change log with rationale and implementation detail.
2. Explicit behaviour-preservation evidence for the cumulative diff, including plan/rendered-output equivalence and unchanged pipeline graph.
3. Equivalence checks or characterisation output captured.
4. Number of passes and termination reason.
5. Remaining risks or recommended follow-up actions.

## Constraints

- Behaviour preservation outranks every other goal, on every pass. When in doubt, don't.
- Never change the plan, rendered output, resource addresses, pipeline triggers/graph, or permission scopes under the guise of a refactor.
- One refactoring per change; verify the plan/output is unchanged locally before the next. Never batch.
- Stay inside the changed surface; repo-wide cleanup is a different task.
- Never weaken or suppress a quality gate or policy; conformance refactors must satisfy the gate, not silence it.
- Read-only verification only. Never `terraform apply`/`destroy`, never deploy, never mutate remote state; never push. Keep all work local with stepwise, revertible commits.
- Never `--approve`; never close, merge or rebase the PR.
- Report only as a terminal summary; never post PR comments, write a report file, or leave a report artifact in the repo.
