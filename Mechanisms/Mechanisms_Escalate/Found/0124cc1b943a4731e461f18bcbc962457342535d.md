---
name: commit-code
description: Validate and package a finished change into a clean commit by following repo-local validation, generation, release-note, and approval rules. Use when the user explicitly asks to prepare or create a commit.
---

# Commit Code

Use this skill when a change is complete and needs to be prepared for commit in a safe, reviewable way.

This skill covers commit preparation and commit creation. It does not imply permission to push, tag, or publish a release.

## When to Use

- the user explicitly asks to prepare/create a commit
- packaging a finished change for delivery
- running repo-local validation + release-note rules
- applying approval rules before commit

## Core Rules

- do not create a commit unless the user or repo-local process explicitly allows that specific commit action
- do not push commits, create tags, or publish releases unless the user or repo-local process explicitly allows that specific action
- do not commit broken builds or knowingly failing verification
- do not hand-edit generated files unless the repo explicitly expects that
- remove local-only artifacts before committing
- follow the repo's source of truth for generated code, version metadata, and deployment configuration
- keep commits scoped to the intended change

## Suggested Process

### 1. Review What Changed

Check:

- which files changed
- whether the diff matches the intended scope
- whether unrelated local edits should stay out of the commit
- whether generated files changed intentionally

### 2. Clean Local-Only Artifacts

Remove or unstage files that should not ship, such as:

- build outputs
- temporary logs
- local config overrides
- editor or OS artifacts

If the repo expects certain generated files to be committed, keep them only when they match the source changes.

### 3. Regenerate What The Repo Requires

Run only the generators that apply to this change, for example:

- API or schema generation
- dependency injection generation
- client or SDK generation
- code formatting or scaffolding steps

Use the repo's official commands instead of guessing.

### 4. Validate

Run the normal quality gates for the repo, such as:

- tests
- lint or static analysis
- build
- targeted checks for migrations, contracts, or packaging

If you intentionally skip a check, capture the reason explicitly.

### 5. Update User-Visible Metadata

Update what the repo expects, when applicable:

- changelog
- release notes
- migration notes
- README or operational docs

Do not include internal workflow wording in commit text or other user-visible artifacts.

### 6. Prepare The Commit Message

The commit message should:

- follow repo-local conventions first
- describe the actual change, not the process around it
- stay free of internal workflow labels or AI/agent wording
- stay scoped to the files being committed

If the repo uses structured commit formats, follow that format. Otherwise prefer a short, descriptive subject.

Examples:

- `add order history endpoint`
- `fix duplicate payment callback handling`
- `split pricing validation into separate module`

### 7. Commit

Before committing, confirm:

- validation is complete
- staged files are intentional
- user approval exists for the commit action

Then create the commit using the repo's normal workflow.

### 8. Handle Push Or Publish Separately

After the commit exists, treat these as separate gated actions:

- pushing a branch or commit
- creating a tag
- opening or publishing a release
- updating remote release metadata

Do not assume commit approval also covers any of these actions.

## Multi-Repo Or Shared Module Changes

When a change spans more than one repo or module:

1. identify the dependency order
2. validate and land the upstream change first when required
3. update downstream consumers to the correct version or revision
4. revalidate after the dependency update
5. keep each commit scoped to one repo or module boundary

## Deployment Or Release Config Changes

If deployment or release configuration changed:

- commit the source-of-truth config, not just a live runtime patch
- avoid release metadata edits that CI or the platform is supposed to own
- capture any rollout dependency or manual follow-up clearly

## Checklist

- [ ] diff matches intended scope
- [ ] local-only artifacts removed
- [ ] required generation completed
- [ ] validation completed
- [ ] user-visible metadata updated when needed
- [ ] commit message follows repo conventions
- [ ] explicit approval exists for the commit action
- [ ] explicit approval exists for any push, tag, or release action

## Adaptation Notes

- not every repo uses structured commit types
- not every repo commits generated files
- validation may be full-repo or target-specific depending on the codebase
- release notes, version files, or deployment manifests may live in another repo

## Related Skills

- **review-code**: Check risky changes before committing
- **write-tests**: Add or update validation before delivery
- **review-service**: Confirm release readiness for broad changes
- **setup-deployment**: Validate deployment source-of-truth changes
- **manage-secrets**: Keep sensitive values out of committed artifacts
\n### 2026: AI Commits and Security

- **Commit signing enforcement:** GPG or SSH key signing provides identity verification and prevents commit impersonation. `git config commit.gpgsign true` enables signing globally. DCO (`Signed-off-by: Name <email>`) provides IP provenance for open-source projects and some regulated orgs. Check the repo CONTRIBUTING.md for which is required.
- **`git-blame-ignore-revs` for AI/bulk commits:** When an AI agent performs bulk reformatting or AI-assisted refactoring, add the resulting commit hash to the `.git-blame-ignore-revs` file so `git blame` continues to point to the human authors of business logic. This avoids polluting blame history.
- **Semantic Release awareness:** Conventional Commits feed automated release tools (Semantic Release, Release Please) that bump SemVer and generate changelogs automatically. Warn that fully automated releases can produce low-quality changelogs — consider using Changesets for human-curated bundling in monorepos.\n