---
name: specify
description: "Use when the user invokes $spec-kit:specify or /spec-kit:specify, or asks to create a brownfield-aware feature specification from a natural language description."
argument-hint: "<feature description>"
allowed-tools: [Read, Write, Bash, Glob, Grep]
disable-model-invocation: true
---

# Spec Kit Specify

This is a user-invoked Spec Kit workflow. Treat user text after the invocation as the workflow input.

## Plugin Root

Use the spec-kit plugin root when running bundled scripts. In Claude Code, `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin root. If that variable is unavailable, resolve the plugin root as the directory two levels above this `SKILL.md`.

The text after `/spec-kit:specify` is the feature description. Do not ask the
user to repeat it unless it is empty.

User input:

$ARGUMENTS

If the input is empty, respond with: "Please provide a feature description.
Example: `/spec-kit:specify build a REST API for managing photo albums`"

## Purpose

Create a concise but executable feature spec that delivers most of Spec Kit's
benefit with less ceremony. The spec must work well for existing repositories:
it should describe the user-visible change and validation needs without
inventing a new architecture.

## Preflight

1. Inspect the current repo before creating the spec:
   - Git status and current branch, if this is a git repo
   - `README.md`, `AGENTS.md`, package/tooling files, and existing tests
   - Existing `.specify/memory/project-context.md` and constitution, if present
2. Run the bundled context detector if available:
   ```bash
   bash "${CLAUDE_PLUGIN_ROOT}/scripts/detect-project-context.sh" --write
   ```
   If the plugin root is not exposed by the runtime, locate the bundled script
   in the installed `spec-kit/scripts/` directory and run that absolute path.
3. Do not initialize git. Do not switch branches unless this command is being
   used to start a new feature branch. If the user explicitly asks to stay on
   the current branch, run the create script with `--no-branch`.

## Execution Flow

1. Create the feature directory by running the bundled script exactly once from
   the project root:
   ```bash
   bash "${CLAUDE_PLUGIN_ROOT}/scripts/create-feature.sh" $ARGUMENTS
   ```
   If using current-branch mode:
   ```bash
   bash "${CLAUDE_PLUGIN_ROOT}/scripts/create-feature.sh" --no-branch $ARGUMENTS
   ```
   Parse JSON for `BRANCH_NAME`, `SPEC_FILE`, `FEATURE_NUM`, and `FEATURE_DIR`.
   All subsequent file paths must be absolute. In current-branch or non-git
   mode, tell the user to set `SPECIFY_FEATURE=<BRANCH_NAME>` for follow-up
   commands unless they export it in the current shell/session.

2. Load:
   - `.specify/memory/constitution.md`, if present
   - `.specify/memory/project-context.md`, if present
   - Relevant repo docs/config discovered in preflight

3. Extract from the feature description:
   - Actors and user goals
   - User-visible behavior
   - Data/entities involved
   - Integrations, permissions, and safety constraints
   - Explicit out-of-scope items, if stated

4. Write `SPEC_FILE` with this structure:

```markdown
# Feature Specification: [FEATURE NAME]

**Feature Branch**: `[BRANCH_NAME]`
**Created**: [today's date]
**Status**: Draft
**Repo Fit**: [one sentence naming the existing area/pattern this feature should fit]

## Overview
[1-2 paragraph summary of what this feature does and why it matters]

## User Scenarios & Acceptance Criteria

### Primary User Story
[Main user journey in plain language]

### Acceptance Scenarios
1. **Given** [initial state], **When** [action], **Then** [expected outcome]
2. **Given** [initial state], **When** [action], **Then** [expected outcome]

### Edge Cases
- [Boundary or error case]
- [Failure or permission case]

## Requirements

### Functional Requirements
- **FR-001**: System MUST [specific testable capability]
- **FR-002**: System MUST [specific testable capability]

### Non-Functional Requirements
- **NFR-001**: [Performance, reliability, observability, security, or UX criterion if material]

### Key Entities
- **[Entity]**: [What it represents, key attributes, relationships]

## Scope
- **In Scope**: [included behavior]
- **Out of Scope**: [excluded behavior]

## Review Checklist
- [ ] Requirements are testable and unambiguous
- [ ] Success criteria are measurable
- [ ] Scope is clearly bounded
- [ ] Existing repo patterns are named or uncertainty is marked
- [ ] No implementation details beyond constraints already present in the repo
- [ ] Material unknowns are marked with `[NEEDS CLARIFICATION: specific question]`
```

5. Quality rules:
   - Focus on WHAT and WHY; include HOW only when the repo already imposes a
     constraint that must be respected.
   - Do not guess. Mark material assumptions with `[NEEDS CLARIFICATION]`.
   - Ask clarifying questions later only when the answer would change
     architecture, data model, task split, tests, safety, UX, or operations.
   - Prefer fewer, higher-quality requirements over broad wish lists.

6. Report:
   - Branch/current feature name and spec file path
   - Requirement count and clarification marker count
   - Whether project context was written
   - Next workflow step: `/spec-kit:clarify` only if material markers remain,
     otherwise `/spec-kit:plan`
