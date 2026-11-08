---
name: prd-taskmaster
description: >-
  PRD generator that creates comprehensive requirements, publishes as a GitHub issue,
  and triggers /agent-os:shape-spec for orchestrated execution. No deferred scope — every
  requirement is a must-deliver. Use when user requests "PRD", "product requirements",
  or wants to plan a feature for implementation.
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Bash
  - AskUserQuestion
  - Skill
---

# PRD Generator v3.0 — GitHub Issue + Shape-Spec Pipeline

Generate comprehensive, zero-compromise PRDs, publish them as GitHub issues, and trigger `/agent-os:shape-spec` with a scope-aware orchestration prompt that enforces Opus 4.6, one-shot delivery, and `/pr-handoff-to-codex` as final validation.

Source attribution: this bundled skill is sourced from `anombyte93/prd-taskmaster` and references Task Master / `task-master-ai` for downstream task orchestration.

## When to Use This Skill

Activate when user:
- Requests a PRD or product requirements document
- Says "I want a PRD", "create requirements", "write requirements"
- Asks to plan a feature for implementation
- Wants to document product/feature requirements for engineering

Do NOT activate for:
- Code documentation (API docs, technical reference)
- Test specifications or QA documentation
- Project management timelines without product context
- PDF document creation

## Core Principles

**Nothing Is Deferred. Ever.**
Phases are fine for sequencing work. But there are NO "nice-to-haves," "future work," "stretch goals," or "do laters." Every requirement in the PRD is a must-deliver. If something isn't important enough to build, it doesn't belong in the PRD at all.

**GitHub Issue Is the Source of Truth**
The full PRD is published as a GitHub issue. This is what agents, shape-spec, and pr-handoff-to-codex reference.

**Shape-Spec Orchestrates Execution**
After the PRD is published, `/agent-os:shape-spec` is triggered with a comprehensive prompt that handles planning, parallelization, agent selection, and quality control.

**Opus 4.6 Everything**
All agents run at Opus 4.6. No exceptions. No cost-saving downgrades.

**One-Shot Delivery**
The plan should be as one-shot as possible. Clarifying questions and pre-reqs come first, then execution runs to completion.

**Creative Tool Usage**
Agents should leverage CLI tools, MCP servers, `/brand-guidelines`, and all available resources. Always check what's available before starting work.

## Separation of Concerns

| Phase | Responsibility | Focus |
|-------|---------------|-------|
| **PRD (this skill)** | *What* to build | Feature design, requirements, acceptance criteria, technical architecture |
| **Shape-Spec (triggered after)** | *How* to build it | Agent orchestration, scope-specific engineering standards, parallelization, quality gates |

The PRD should read like a technical architect's vision for the ideal feature. It defines requirements at a technical level without prescribing platform-specific implementation patterns — that's shape-spec's job.

## Workflow Overview (7 Steps)

1. **Check State** — Detect existing PRDs, check for GH issues
2. **Discovery** — Gather requirements interactively
3. **Generate PRD** — Comprehensive, zero-compromise technical requirements
4. **Validate Quality** — Automated checks including no-deferral enforcement
5. **Publish GitHub Issue** — Full PRD as issue body via `gh issue create`
6. **Detect Scope** — Auto-detect iOS / Backend / GCP-Infra from PRD + repo, confirm with user
7. **Trigger Shape-Spec** — Baseline execution prompt + scope-specific engineering sections

---

## Detailed Implementation

### Step 1: Check State

**FIRST ACTION** when skill activates:

```
1. Check for existing PRD-related GH issues:
   - Run: gh issue list --label "PRD" --state open --limit 10
   - If found: Show existing issues and ask user what to do

2. Check for local PRD files:
   - Glob: .taskmaster/docs/*.md, docs/plans/*prd*, agent-os/specs/*/plan.md
   - If found: Show existing PRDs and offer options

3. If existing PRD found, use AskUserQuestion:
   Options:
   a. "Use existing PRD" — Skip to Step 5 (validate) then Step 6 (publish)
   b. "Update existing PRD" — Load, modify, re-validate
   c. "Create new PRD" — Full workflow from Step 2
   d. "Review existing PRD" — Show summary, exit
```

---

### Step 2: Discovery (Requirements Gathering)

Ask questions interactively using AskUserQuestion. One question at a time.

**Essential Questions (5):**
1. What problem does this solve? (user pain point, business impact)
2. Who is the target user/audience?
3. What is the proposed solution or feature?
4. What are the key success metrics? (how we measure success)
5. What constraints exist? (technical, resources, dependencies)

**Technical Context (4):**
6. Is this for an existing codebase or greenfield?
7. What tech stack? (if known — auto-detect from repo if possible)
8. Any integration requirements? (third-party services, internal systems)
9. Performance/scale requirements? (users, data volume, latency)

**Scope & Complexity (2):**
10. What's the estimated complexity? (simple feature, typical project, complex system)
11. Anything else I should know? (edge cases, constraints, prior art)

**Smart Defaults:**
- If user provides minimal answers, use best guesses and document assumptions
- Default to comprehensive detail
- Assume engineer audience unless specified
- Auto-detect tech stack from repo files when possible
- **NEVER ask about timeline expectations as a way to reduce scope** — everything is must-deliver

---

### Step 3: Generate PRD

Generate a comprehensive PRD focused on the *what* — the ideal feature at a technical architecture level. The PRD defines requirements, acceptance criteria, and technical design. It does NOT prescribe platform-specific implementation patterns (that's shape-spec's job).

**PRD Structure (10 sections):**

```markdown
# {Feature Name} — Product Requirements Document

## 1. Executive Summary
[2-3 sentences: what, why, for whom]

## 2. Problem Statement
[User pain point + business impact. Specific, measurable.]

## 3. Goals & Success Metrics
[SMART metrics. Every goal has a measurable target.]
- Goal 1: [metric] — Target: [number]
- Goal 2: [metric] — Target: [number]

## 4. User Stories
[Each with acceptance criteria. Minimum 3 criteria per story.]
- As a [user], I want [action] so that [benefit]
  - AC1: [testable criterion]
  - AC2: [testable criterion]
  - AC3: [testable criterion]

## 5. Functional Requirements
[Numbered, testable, prioritized. ALL are must-deliver.]
- REQ-001: [requirement] — Priority: Must
- REQ-002: [requirement] — Priority: Must
[Note: No "Should" or "Could" priorities. Everything here is Must.]

## 6. Non-Functional Requirements
[Specific targets, not vague.]
- Performance: API response < 200ms p95
- Availability: 99.9% uptime
- Security: [specific requirements]

## 7. Technical Considerations
[Architecture decisions, integration points, constraints]

## 8. Implementation Phases
[Phases for sequencing only — NOT for deferring scope.]
- Phase 1: [what and why first]
- Phase 2: [what and why second]
[Every phase is committed. No phase is optional.]

## 9. Risks & Mitigations
[Known risks with concrete mitigation strategies]

## 10. Acceptance Criteria
[How we know the entire feature is done]
- [ ] All REQ-XXX requirements implemented and tested
- [ ] Performance targets met
- [ ] Security review passed
- [ ] PR passes /pr-handoff-to-codex review
```

**CRITICAL RULES for PRD generation:**

1. **No "Out of Scope" section.** If it's not in the PRD, it doesn't exist. If it matters, it's a requirement.
2. **No "Nice to Have" or "Could" priorities.** Everything is Must.
3. **No "Future Work" or "Post-Launch" deferrals.** Phases sequence work; they don't defer it.
4. **No weasel words.** Not "should be fast" but "< 200ms p95." Not "good UX" but "[specific metric]."
5. **Every requirement is testable.** If you can't write a test for it, rewrite it until you can.

**Output:** Write PRD to `.taskmaster/docs/prd-{feature-slug}.md`

---

### Step 4: Validate Quality (14 Automated Checks)

**Required Elements (5 checks):**
1. Executive summary exists (2-3 sentences)
2. Problem statement includes user AND business impact
3. All goals have SMART metrics
4. User stories have acceptance criteria (minimum 3 per story)
5. Final acceptance criteria section exists

**Functional Requirements (3 checks):**
6. All functional requirements are testable (not vague)
7. All requirements are Must priority (no Should/Could)
8. Requirements are numbered (REQ-001, REQ-002, etc.)

**Technical Quality (3 checks):**
9. Technical considerations address architecture
10. Non-functional requirements include specific numeric targets
11. Risks have concrete mitigations (not "TBD")

**Zero-Deferral Enforcement (3 checks):**
12. No "Out of Scope" section exists
13. No phrases: "nice to have", "stretch goal", "future work", "post-launch", "if time allows", "v2", "later phase"
14. No "Could" or "Should" priority levels — everything is "Must"

**If validation fails on deferral checks:** Auto-fix by promoting deferred items to requirements or removing them entirely. Ask user to confirm.

**Validation Output:**
```
PRD Quality Validation: 14/14 PASSED
  All required elements present
  All requirements are must-deliver
  Zero deferred items detected
  Quality Score: 70/70 (EXCELLENT)
```

---

### Step 5: Publish GitHub Issue

Create a GitHub issue with the full PRD as the issue body.

```bash
gh issue create \
  --title "{Feature Name} — PRD" \
  --label "PRD" \
  --body "$(cat .taskmaster/docs/prd-{feature-slug}.md)"
```

**Capture the issue URL** — this is passed to shape-spec.

**Output:**
```
Published PRD as GitHub issue: https://github.com/{owner}/{repo}/issues/{N}
```

---

### Step 6: Detect Scope (for Shape-Spec prompt assembly)

Now that the PRD is published, detect which engineering scope sections to include in the shape-spec prompt. This does NOT affect the PRD — it determines which implementation standards shape-spec will enforce.

Auto-detect from PRD content + repo structure, then confirm with user.

**Detection Logic:**

```
Scan PRD content + repo structure for scope indicators:

iOS indicators:
  - Keywords: SwiftUI, UIKit, Swift, iOS, Xcode, simulator, @Observable, CoreData
  - Files: *.swift, <YOUR_APP>/, *.xcodeproj, *.xcworkspace

Backend indicators:
  - Keywords: API, endpoint, controller, .NET, Cloud Run, PostgreSQL, Redis
  - Files: *.cs, *.csproj, Infrastructure/, Controllers/

GCP/Infra indicators:
  - Keywords: Terraform, Cloud Run, Cloud SQL, deployment, CI/CD, Docker
  - Files: *.tf, cloudbuild.yaml, Dockerfile*, .github/workflows/
```

**Confirm with AskUserQuestion:**

```
The PRD is published. Now I need to determine which engineering scope sections
to include in the shape-spec execution prompt.

Based on the PRD content, I detected:

  [x] iOS (Swift/SwiftUI) — [detected indicators]
  [x] Backend (.NET/Cloud Run) — [detected indicators]
  [ ] GCP/Infrastructure — [none detected]

Is this correct? (confirm / adjust)
```

Store confirmed scope as `SCOPE_IOS`, `SCOPE_BACKEND`, `SCOPE_GCP_INFRA`.

---

### Step 7: Trigger Shape-Spec

Build and trigger the `/agent-os:shape-spec` prompt with scope-aware sections. These sections tell shape-spec *how* to implement the PRD — the platform-specific engineering standards, build commands, and quality gates.

**The prompt is assembled from:**
1. **Baseline system prompt** (ALWAYS included)
2. **Scope-specific sections** (included based on Step 3 detection)
3. **Issue URL** (from Step 6)

#### Baseline System Prompt (ALWAYS INCLUDED)

```
/agent-os:shape-spec We have a PRD at {ISSUE_URL}.

Create a plan and series of tasks. Identify the proper agents to use for parallelization,
including overseeing agents for quality control, checking, and verification. If an agent
doesn't exist to your liking, create one.

## Execution Requirements

- ALL AGENTS MUST RUN AT OPUS 4.6. No exceptions. No cost-saving downgrades.
- NO TASKS OR DELIVERABLES ARE OPTIONAL. EVER. Everything in the PRD is a must-deliver.
- The plan should be as one-shot as possible. You may ask/direct the user for clarifying
  questions and/or pre-reqs to set up in the first stage. After that, execution runs to
  completion without stopping.
- The final PR MUST run '/pr-handoff-to-codex' as final validation before acceptance.
  This does NOT limit expectations of your oversight or quality expected of the delivering
  agents — it is an additional validation gate.

## Creative Resource Usage

- You and the agents should be creative with tool usage. Use CLI tools and MCP servers
  whenever possible — always check what's available first (there's lots of great stuff).
- Take advantage of <YOUR_WEBSITE_URL> resources including '/brand-guidelines' for any UI/visual work.
- Use the Agent tool for parallelization of independent tasks.
- Use '/security-scan' for security-relevant changes.
- Use '/perf-check' for performance-critical components.

## Quality Standards

- Every agent is responsible for verifying their own work before marking complete.
- The oversight agent reviews all work against the PRD requirements.
- Tests must be written alongside implementation, not after.
- All builds must pass before any task is marked complete.
```

#### iOS Scope Section (included when SCOPE_IOS = true)

```
## iOS Requirements

- Swift 6 / SwiftUI with @Observable pattern (iOS 17+)
- Follow existing patterns in <YOUR_APP>/<YOUR_APP>/Core/Services/ and <YOUR_APP>/<YOUR_APP>/Features/
- ViewModels use @Observable macro with @ObservationIgnored for dependencies
- Build verification: cd <YOUR_APP> && xcodebuild -project <YOUR_APP>.xcodeproj -scheme "<YOUR_APP> Dev" \
    -destination 'platform=iOS Simulator,name=iPhone 17 Pro Max,OS=26.2' build
- Test verification: cd <YOUR_APP> && xcodebuild -project <YOUR_APP>.xcodeproj -scheme "<YOUR_APP> Dev" \
    -destination 'platform=iOS Simulator,name=iPhone 17 Pro Max,OS=26.2' test
- Design system compliance: Use '/ios-design' for any new UI components
- Use '/brand-guidelines' for colors, typography, and visual identity
- Follow CLAUDE.md patterns for SwiftUI Map, lazy service init, audio pipeline, etc.
- All new views must work on iPhone and iPad screen sizes
- Accessibility: VoiceOver labels on all interactive elements
```

#### Backend Scope Section (included when SCOPE_BACKEND = true)

```
## Backend Requirements (.NET 8 / Cloud Run)

- Follow existing patterns in Infrastructure/<YOUR_API_PROJECT>/Controllers/ and Services/
- All endpoints must use Firebase Bearer token authentication
- JSON responses use camelCase, dates use ISO 8601
- EF Core entities map to snake_case PostgreSQL columns
- JSONB columns use JsonDocument with proper serialization
- New endpoints registered with proper route attributes
- DI registrations added in GCPStartup.cs
- Database queries MUST use .Select() projection — never load full entities with ContentVector
- Config-driven: no hardcoded AI model names, prompts, generation params, or magic numbers
- Build verification: cd Infrastructure/<YOUR_API_PROJECT> && dotnet build <YOUR_API_PROJECT>.GCP.csproj
- Test verification: cd Infrastructure/<YOUR_API_PROJECT>.Tests && dotnet test --filter "FullyQualifiedName!~Integration"
- Test endpoints with curl after implementation
- Error handling: all async calls have try/catch with meaningful error messages
- No security vulnerabilities (SQL injection, XSS, hardcoded secrets)
```

#### GCP/Infrastructure Scope Section (included when SCOPE_GCP_INFRA = true)

```
## GCP / Infrastructure Requirements

- Multi-environment awareness: dev (<YOUR_GCP_PROJECT_DEV>), staging (<YOUR_GCP_PROJECT_STAGING>), prod (<YOUR_GCP_PROJECT_PROD>)
- Cloud Run service name is '<YOUR_SERVICE_NAME>' in ALL environments — distinction comes from project isolation
- Always use Dockerfile.gcp (not Dockerfile). Build context is Infrastructure/<YOUR_API_PROJECT>/
- Terraform modules in Infrastructure/terraform/ — use existing module patterns
- State buckets: gs://<YOUR_TF_STATE_BUCKET>-{env} (versioning enabled)
- GitHub Actions CI/CD: WIF keyless auth (never store GCP credentials in secrets)
- Deploy by digest: promote images via crane copy by OCI digest, not by tag
- Cloud Logging for debugging: use structured logging with proper severity levels
- Secret Manager for all secrets — never hardcode, never commit
- Terraform plan before apply: cd Infrastructure/terraform/environments/dev && terraform plan
- Docker build test: docker build -f Infrastructure/<YOUR_API_PROJECT>/Dockerfile.gcp -t <YOUR_SERVICE_NAME>:local Infrastructure/<YOUR_API_PROJECT>
- Service account permissions: verify required IAM roles before deploying
- Cloud SQL Proxy for local dev database access
- Redis/Memorystore: verify cache TTLs and invalidation patterns
```

#### Testing Section (ALWAYS INCLUDED, expanded when test-heavy)

```
## Testing Requirements

- Tests written alongside implementation, not after
- iOS tests: XCTest in <YOUR_APP>/Tests/, mirror feature names
- Backend tests: dotnet test in Infrastructure/<YOUR_API_PROJECT>.Tests/
- Minimum coverage: all new public APIs and critical paths
- Edge cases covered: null, empty, boundary values, error conditions
- No test pollution: each test is independent
- Integration tests separated from unit tests (filter with --filter "FullyQualifiedName!~Integration")
- Performance tests for any latency-sensitive paths (API < 200ms p95, DB queries < 50ms)
```

#### Performance Section (ALWAYS INCLUDED)

```
## Performance Targets

- API response time: < 200ms p95
- PostgreSQL queries: < 50ms
- iOS launch time: < 2s
- Memory usage: < 150MB
- Use '/perf-check' to validate performance-critical components
```

---

## Prompt Assembly

The final prompt is assembled by concatenating:

1. Baseline system prompt
2. iOS section (if SCOPE_IOS)
3. Backend section (if SCOPE_BACKEND)
4. GCP/Infra section (if SCOPE_GCP_INFRA)
5. Testing section (always)
6. Performance section (always)

**Trigger the skill:**

```
Use Skill tool: skill="agent-os:shape-spec", args="{assembled prompt}"
```

**Output to user:**

```
PRD published: {ISSUE_URL}
Triggering /agent-os:shape-spec with scope-aware orchestration prompt...

Scope detected:
  [x] iOS (Swift/SwiftUI)
  [x] Backend (.NET/Cloud Run)
  [ ] GCP/Infrastructure
  [x] Testing
  [x] Performance

Baseline enforced:
  - All agents at Opus 4.6
  - Zero optional deliverables
  - One-shot execution
  - /pr-handoff-to-codex final validation
  - Creative CLI/MCP tool usage
  - /brand-guidelines awareness
```

---

## Tips for Best Results

**Provide Context Upfront:**
- More detail in discovery leads to a better PRD
- Share constraints, dependencies, assumptions
- Mention existing systems to integrate with

**Be Specific About Success:**
- Quantify goals (not "improve UX" but "increase NPS from 45 to 60")
- Define what "done" looks like
- Specify how you'll measure success

**Trust the Pipeline:**
- PRD captures what to build (no compromises)
- GitHub issue makes it referenceable and trackable
- shape-spec handles how to build it (agents, parallelization, quality)
- pr-handoff-to-codex validates before merge

**Everything Is Important:**
- If you're tempted to defer something, either make it a requirement or remove it entirely
- Phases sequence work, they don't deprioritize it
- "We'll add that later" is not a valid plan — either build it now or don't build it

---

**Remember**: This skill generates the PRD and hands off to shape-spec for execution planning. The skill's job is done once shape-spec is triggered. shape-spec handles agent orchestration, parallelization, and the full build pipeline through to /pr-handoff-to-codex.
