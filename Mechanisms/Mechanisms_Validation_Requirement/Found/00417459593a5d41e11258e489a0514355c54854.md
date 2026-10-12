---

name: testing-quality
description: Defines testing and quality standards for the reptile knowledge platform. Use this skill for unit tests, integration tests, end-to-end tests, test strategy, quality gates, linting, static analysis, coverage, CI workflows, fixtures, test data, regression prevention, and definition-of-done validation.
when_to_use: Use whenever a task creates, changes, reviews, debugs, or validates tests, CI pipelines, linting, static analysis, coverage, quality gates, test environments, regression suites, or completion criteria.
argument-hint: "[testing-or-quality-task]"
disable-model-invocation: false
user-invocable: true
model: inherit
effort: high
paths:

* "apps/api/**/*_test.go"
* "apps/web/**/*.{test,spec}.{ts,tsx,js,jsx}"
* "test/**"
* ".github/workflows/**"
* ".golangci*.{yaml,yml}"
* "apps/web/eslint.config.*"
* "apps/web/vitest.config.*"
* "apps/web/playwright.config.*"
* "Makefile"
* "scripts/validate*"
* "scripts/test*"
* "docs/development/testing.md"
* "docs/runbooks/**"

---

# Testing and Quality

## Objective

Define and enforce testing, validation, and quality standards for the reptile knowledge platform.

Use this skill to guide:

* unit testing;
* integration testing;
* end-to-end testing;
* test strategy;
* test data;
* fixtures;
* test isolation;
* coverage;
* regression prevention;
* linting;
* static analysis;
* dependency validation;
* CI workflows;
* quality gates;
* release confidence;
* definition of done.

The current task is:

```text
$ARGUMENTS
```

If no arguments were provided, infer the task from the current conversation.

---

## Mandatory Context

Before changing tests or quality configuration:

1. Read `${CLAUDE_PROJECT_DIR}/CLAUDE.md`.
2. Read the relevant backend, frontend, database, authentication, security, local-development, and Terraform skills.
3. Inspect existing tests.
4. Inspect CI workflows.
5. Inspect lint and static-analysis configuration.
6. Inspect Makefile and validation scripts.
7. Identify the current project phase.
8. Identify the behavior being protected.
9. Identify the risk of regression.
10. Identify which test level is appropriate.
11. Preserve existing test conventions unless they are clearly harmful.
12. Confirm which commands can actually be executed.

Do not add tests without understanding the behavior they are intended to protect.

Do not confuse a high test count with high confidence.

---

## Core Principles

Testing must be:

* behavior-oriented;
* proportional to risk;
* deterministic;
* isolated;
* readable;
* maintainable;
* fast enough for its purpose;
* representative of real usage;
* integrated into development workflow;
* useful for regression prevention.

Prefer the lowest-cost test that provides sufficient confidence.

Do not test implementation details when observable behavior is more valuable.

Do not duplicate the same behavior across many test layers without a reason.

---

## Quality Strategy

The project should combine:

* compilation;
* type checking;
* formatting;
* linting;
* unit tests;
* integration tests;
* end-to-end tests;
* migration validation;
* infrastructure validation;
* dependency scanning;
* security scanning;
* documentation consistency checks where practical.

No single tool is sufficient.

A green unit-test suite does not prove that:

* migrations apply;
* services integrate;
* authentication works;
* Docker starts;
* Terraform is valid;
* frontend and backend contracts match.

---

## Test Pyramid

Use a pragmatic test pyramid.

### Unit Tests

Many, fast, focused tests.

Use for:

* domain invariants;
* value objects;
* pure utilities;
* validation;
* state transitions;
* authorization policies;
* serialization helpers.

### Integration Tests

Fewer, higher-confidence tests.

Use for:

* PostgreSQL repositories;
* migrations;
* Redis behavior;
* LocalStack storage;
* Keycloak integration;
* HTTP handlers with real infrastructure dependencies;
* application wiring.

### End-to-End Tests

Few, critical user journeys.

Use for:

* public species browsing;
* article reading;
* search and filters;
* login;
* administrative article creation;
* publishing;
* media upload.

Do not turn every possible path into an E2E test.

---

## Risk-Based Testing

Determine test depth based on:

* business impact;
* security impact;
* data integrity;
* frequency of change;
* integration complexity;
* reversibility;
* user visibility;
* production blast radius.

High-risk examples:

* authentication;
* authorization;
* publishing;
* role assignment;
* migrations;
* media upload;
* destructive actions;
* scheduled jobs.

Low-risk examples:

* static decorative text;
* simple visual spacing;
* non-interactive presentational components.

Do not spend the same testing effort on every change.

---

## Definition of Test Scope

Before writing tests, define:

* behavior under test;
* preconditions;
* action;
* expected outcome;
* failure behavior;
* data dependencies;
* external dependencies;
* cleanup strategy.

Avoid tests whose purpose cannot be described in one or two sentences.

---

## Naming Tests

Test names should describe behavior.

Go example:

```go
func TestArticlePublishRejectsDraftWithoutContent(t *testing.T)
```

Frontend example:

```ts
it("shows a validation message when the scientific name is missing", async () => {
  // ...
});
```

Avoid vague names:

```text
test works
should pass
test article
renders correctly
```

---

## Arrange, Act, Assert

Prefer a clear structure:

```text
Arrange
Act
Assert
```

Comments are optional when the phases are already obvious.

Do not hide the action or assertion behind excessive helper layers.

---

## Unit Tests

Unit tests should:

* run quickly;
* avoid network;
* avoid Docker;
* avoid external services;
* use deterministic time;
* use deterministic IDs when necessary;
* test meaningful behavior;
* cover edge cases.

Good candidates:

* slug validation;
* editorial transitions;
* measurement ranges;
* permission checks;
* article block validation;
* redirect safety;
* API error mapping utilities.

Do not use integration infrastructure in unit tests.

---

## Domain Tests

Domain tests should verify:

* invariants;
* valid transitions;
* invalid transitions;
* boundary values;
* missing required state;
* conflict behavior;
* explicit uncertainty rules.

Example:

```go
func TestPublishArticle(t *testing.T) {
	tests := []struct {
		name    string
		status  EditorialStatus
		content []ContentBlock
		wantErr error
	}{
		{
			name:    "publishes article in review with content",
			status:  StatusInReview,
			content: validContent(),
			wantErr: nil,
		},
		{
			name:    "rejects empty article",
			status:  StatusInReview,
			content: nil,
			wantErr: ErrArticleContentRequired,
		},
	}
}
```

Do not test only struct field assignment.

---

## Application Tests

Application tests should verify:

* use-case orchestration;
* repository interaction;
* authorization;
* transaction behavior;
* event emission;
* expected error mapping.

Use fakes when they improve clarity.

Do not require PostgreSQL for every application test.

Use integration tests when repository behavior itself is under test.

---

## Test Doubles

Choose deliberately.

### Fake

A working simplified implementation.

Example:

```go
type InMemoryArticleRepository struct {
	articles map[ArticleID]*Article
}
```

### Stub

Returns predefined values.

### Spy

Records calls for later assertions.

### Mock

Verifies expected interactions.

Prefer fakes and simple stubs.

Do not generate mocks for every interface automatically.

Do not over-specify internal call order unless order is part of behavior.

---

## Time in Tests

Inject a clock when time affects behavior.

Avoid:

```go
time.Sleep(...)
```

for ordinary unit synchronization.

Prefer:

```go
fixedClock := NewFixedClock(time.Date(...))
```

For asynchronous tests, use bounded polling or synchronization primitives.

Do not make tests depend on the actual current date.

---

## IDs in Tests

Use deterministic IDs when the value matters.

Example:

```text
00000000-0000-0000-0000-000000000101
```

Use random IDs when uniqueness matters but the value does not.

Do not make assertions against unpredictable IDs unless the test captures the generated value.

---

## Table-Driven Tests

Use table-driven tests for validation and state matrices.

Good uses:

* slug cases;
* permission matrices;
* editorial transitions;
* measurement validation;
* error mapping;
* claim parsing.

Avoid extremely large tables containing unrelated behaviors.

Split tests when failure diagnosis becomes unclear.

---

## Parallel Tests

Use `t.Parallel()` only when tests are isolated.

Do not parallelize tests that share:

* database state;
* global configuration;
* ports;
* mutable package state;
* fixed external resources.

Parallel execution must not introduce flakiness.

---

## Go Test Requirements

Expected commands:

```bash
go test ./...
go test -race ./...
go vet ./...
golangci-lint run
go build ./...
```

Use the race detector when:

* concurrency changes;
* shared state exists;
* caches are introduced;
* workers are tested;
* goroutines are used.

Do not require the race detector for every fast local inner loop if it materially slows development, but include it in CI or targeted validation.

---

## Handler Tests

Use `httptest`.

Handler tests should verify:

* status code;
* headers;
* content type;
* response body;
* validation errors;
* malformed JSON;
* authentication;
* forbidden access;
* not found;
* success.

Do not require a full running HTTP server for focused handler tests.

Example:

```go
request := httptest.NewRequest(http.MethodGet, "/api/v1/species/example", nil)
response := httptest.NewRecorder()

handler.ServeHTTP(response, request)

if response.Code != http.StatusOK {
	t.Fatalf("expected 200, got %d", response.Code)
}
```

---

## Repository Integration Tests

Repository tests should use real PostgreSQL.

Test:

* inserts;
* updates;
* reads;
* joins;
* pagination;
* filters;
* constraints;
* conflict mapping;
* null handling;
* transactions;
* row mapping.

Do not mock SQL generated by `sqlc` when validating persistence behavior.

---

## Database Isolation

Integration tests must not depend on developer data.

Possible strategies:

* one database per suite;
* one schema per suite;
* transaction rollback per test;
* Testcontainers;
* dedicated Compose test database.

Choose one consistent approach.

Do not let tests point to production or shared development databases.

---

## Migration Tests

At minimum, test:

```text
empty database -> latest schema
```

When compatibility matters, also test:

```text
previous schema -> latest schema
```

Verify:

* migration applies;
* expected tables exist;
* constraints work;
* indexes exist where required;
* rollback works when safe.

Do not treat SQL parsing as sufficient migration validation.

---

## Seed Tests

Test that seed execution:

* succeeds;
* is deterministic;
* respects foreign keys;
* does not create duplicates when designed to be idempotent;
* creates expected representative data.

Do not make all tests depend on seed data.

Use dedicated fixtures for test-specific behavior.

---

## Frontend Unit Tests

Use for:

* Zod schemas;
* data mapping;
* query-key creation;
* URL-state parsing;
* pure formatting;
* safe redirect validation;
* content block parsing.

Do not render React components to test pure functions.

---

## Component Tests

Use Testing Library.

Test behavior such as:

* renders expected content;
* responds to keyboard and mouse;
* shows loading;
* shows empty state;
* shows error state;
* submits forms;
* maps server errors;
* hides or disables unauthorized actions;
* restores focus.

Do not test internal state variables.

Do not query by implementation-specific CSS classes.

---

## Testing Library Query Priority

Prefer:

1. `getByRole`;
2. `getByLabelText`;
3. `getByText`;
4. `getByPlaceholderText`;
5. `getByTestId` only when necessary.

Example:

```ts
screen.getByRole("button", { name: "Publish article" });
```

Do not add test IDs to every element by default.

---

## User Interactions

Use `userEvent` for realistic interactions.

Prefer:

```ts
await user.click(button);
await user.type(input, "Boa constrictor");
```

over low-level event dispatch when not needed.

Do not skip async handling around real user interactions.

---

## Frontend API Mocking

Use request-level mocking when adopted, such as MSW.

Mock:

* realistic response bodies;
* status codes;
* latency when useful;
* validation errors;
* unauthenticated responses;
* forbidden responses;
* not found;
* server failure.

Do not mock TanStack Query itself.

Do not mock every feature hook.

---

## Snapshot Tests

Use snapshots sparingly.

Appropriate uses:

* stable structured serialization;
* small schema outputs;
* generated public contract fragments.

Avoid large component snapshots.

Large snapshots are difficult to review and often approve accidental changes.

Prefer explicit assertions.

---

## Accessibility Tests

Automated accessibility checks may use appropriate tools.

Test:

* labels;
* roles;
* focus behavior;
* dialog semantics;
* heading hierarchy;
* accessible names;
* error announcements.

Automated checks do not replace manual keyboard and screen-reader review.

Do not claim accessibility compliance based only on an automated scan.

---

## Visual Regression

Visual regression may be introduced when the design system stabilizes.

Useful for:

* public article layout;
* species detail page;
* navigation;
* admin editor states;
* responsive breakpoints.

Do not introduce visual snapshots before the UI is stable enough to make maintenance worthwhile.

Do not use visual tests as the only accessibility or behavior verification.

---

## End-to-End Testing

Use Playwright for critical user journeys.

A good E2E test should:

* use the application as a user would;
* avoid internal implementation knowledge;
* use stable accessible selectors;
* isolate its data;
* clean up when necessary;
* avoid unnecessary dependency on execution order.

Do not make E2E tests depend on another test having run first.

---

## Initial E2E Candidates

Phase 1:

* open home page;
* search for species;
* open species detail;
* open article detail;
* use filters.

Phase 2:

* login;
* access profile;
* logout;
* forbidden admin access for member.

Phase 3:

* editor creates draft;
* editor updates article;
* administrator publishes;
* public article becomes visible.

Do not implement Phase 3 E2E tests during Phase 0.

---

## E2E Test Data

Use dedicated test users and deterministic content.

Potential users:

```text
member@example.test
editor@example.test
admin@example.test
```

Use local-only domains.

Do not use real personal email addresses.

Do not use shared mutable records without reset or namespacing.

---

## E2E Authentication

Possible strategies:

* login through Keycloak UI;
* pre-authenticated storage state;
* token seeding through local provider;
* API-assisted session setup.

At least one test should validate the real login flow.

Most authenticated tests may reuse a safe pre-authenticated state for speed.

Do not bypass all authentication in E2E tests if authentication is a critical feature.

---

## E2E Reliability

Avoid:

* arbitrary sleeps;
* selectors based on styling;
* dependence on animation timing;
* shared mutable test data;
* implicit ordering;
* real external services.

Use:

* locator assertions;
* automatic waiting;
* explicit application state;
* deterministic local dependencies.

Do not use:

```ts
await page.waitForTimeout(5000);
```

as a normal synchronization method.

---

## Contract Testing

The backend OpenAPI contract and frontend client must remain synchronized.

Possible approaches:

* generate frontend types from OpenAPI;
* validate API responses against schema in tests;
* run specification linting;
* compare generated artifacts.

Do not maintain manually duplicated incompatible contracts.

Do not add complex consumer-driven contract infrastructure before needed.

---

## OpenAPI Validation

Validate:

* syntax;
* required fields;
* operation IDs;
* response definitions;
* authentication schemes;
* examples when present.

Potential tools may be introduced according to repository conventions.

Do not declare an endpoint complete if OpenAPI is stale.

---

## Content Schema Tests

Structured article content requires explicit schema tests.

Test:

* supported blocks;
* unsupported blocks;
* invalid versions;
* unsafe links;
* missing media IDs;
* invalid heading levels;
* payload limits;
* unknown fields;
* serialization round-trip.

Frontend and backend should use equivalent fixtures where practical.

Do not rely only on TypeScript validation.

---

## Authentication Tests

Test:

* missing token;
* malformed token;
* invalid signature;
* expired token;
* wrong issuer;
* wrong audience;
* valid token;
* disabled user;
* missing permission;
* valid permission;
* ownership rules.

Do not test only successful authentication.

Forbidden paths are essential.

---

## Authorization Matrix Tests

Use a documented matrix.

Example:

| Actor         | Create article | Update draft | Publish article | Manage users |
| ------------- | -------------: | -----------: | --------------: | -----------: |
| Visitor       |             No |           No |              No |           No |
| Member        |             No |           No |              No |           No |
| Editor        |            Yes |          Yes |              No |           No |
| Administrator |            Yes |          Yes |             Yes |          Yes |

Create tests that protect important cells.

Do not rely on role names alone if permissions are the real source of truth.

---

## Media Tests

Test:

* valid image upload;
* oversized upload;
* unsupported MIME type;
* mismatched extension;
* missing metadata;
* unauthorized upload;
* missing object;
* cleanup after failed metadata save;
* safe storage key generation.

Do not require real S3 in unit tests.

Use LocalStack integration tests where S3 behavior matters.

---

## LocalStack Tests

Use integration tests for supported AWS-like behavior.

Test:

* bucket exists;
* upload works;
* object retrieval works;
* queue behavior when used;
* configured endpoints.

Do not assume LocalStack proves IAM or all AWS edge cases.

Document gaps requiring future real-AWS validation.

---

## Terraform Tests

Required checks:

```bash
terraform fmt -check -recursive
terraform init -backend=false
terraform validate
tflint
```

Optional when configured:

```bash
checkov -d .
trivy config .
```

Use native Terraform tests when meaningful.

Do not run real AWS apply as part of normal pull-request validation.

---

## Docker Validation

Validate:

```bash
docker compose config
docker compose build
docker compose up -d
docker compose ps
```

Check health endpoints.

For clean-environment confidence, periodically validate from removed project volumes.

Do not rely only on already-running stale containers.

---

## Static Analysis

### Go

Use:

* `go vet`;
* `golangci-lint`;
* race detector when relevant;
* vulnerability scanning when configured.

### TypeScript

Use:

* TypeScript strict mode;
* ESLint;
* build validation;
* dependency audit or scanner according to project policy.

### Terraform

Use:

* `terraform validate`;
* TFLint;
* infrastructure security scanning.

### Shell

Use ShellCheck when scripts become significant.

Do not add static-analysis tools without configuring and maintaining them.

---

## Formatting

Formatting should be automated.

Expected tools:

```text
gofmt
Prettier or selected frontend formatter
terraform fmt
```

Choose one frontend formatting strategy.

Do not create conflicting formatter and lint rules.

Formatting failures should be easy to fix.

---

## Linting

Lint rules should:

* identify real defects;
* support maintainability;
* avoid excessive noise;
* be documented when non-obvious;
* be consistent locally and in CI.

Do not enable every strict rule without evaluating impact.

Do not disable lint globally to resolve one localized issue.

Use narrow exceptions with explanations.

---

## golangci-lint

Configure a curated set of linters.

Potential categories:

* correctness;
* error handling;
* complexity;
* style;
* security-related checks.

Do not enable every available linter blindly.

Pin the tool version in CI and local tooling where practical.

Do not allow local and CI versions to diverge silently.

---

## ESLint

Use ESLint with TypeScript and React support.

Rules should protect:

* unsafe types;
* hook usage;
* inaccessible patterns;
* unused code;
* import consistency;
* promise handling where configured.

Do not use ESLint as a replacement for TypeScript.

Do not silence errors with broad disable comments.

---

## Coverage

Coverage is a diagnostic, not the goal.

Use coverage to identify:

* untested critical branches;
* untested domain rules;
* missing failure paths;
* low-confidence modules.

Do not optimize solely for a percentage.

High coverage can still miss important behavior.

---

## Coverage Thresholds

If thresholds are introduced, apply them thoughtfully.

Possible strategy:

* overall minimum;
* higher expectations for domain logic;
* no strict threshold for generated code;
* exclusions for trivial wiring.

Do not set a high arbitrary threshold that encourages meaningless tests.

Do not reduce thresholds silently.

---

## Mutation Testing

Mutation testing may be introduced later for critical domain rules.

Useful areas:

* editorial transitions;
* authorization policies;
* validation;
* scoring or gamification rules.

Do not add mutation testing during the initial foundation unless there is capacity to maintain it.

---

## Flaky Tests

A flaky test is a defect.

When a test flakes:

1. reproduce;
2. identify shared state, timing, or dependency issue;
3. fix the root cause;
4. quarantine only as a temporary documented measure;
5. create follow-up ownership.

Do not add retries as the first solution.

Do not ignore intermittent failures.

---

## Test Retries

Retries may be acceptable for selected E2E tests due to environment instability.

They must not hide deterministic application defects.

Track retry frequency.

Do not retry unit tests by default.

---

## Test Performance

Maintain fast feedback.

Potential groups:

```text
unit
integration
e2e
security
infrastructure
```

Recommended workflow:

* fast tests on every local change;
* integration in CI;
* E2E for affected critical flows;
* full suite before release.

Do not require the full slow suite for every tiny local edit if a faster targeted loop exists.

---

## Test Selection

Run the narrowest useful test during implementation.

Examples:

```bash
go test ./internal/articles/...
npm test -- SpeciesCard
```

Before completion, run the broader relevant suite.

Do not report a feature as complete after only one narrow test if cross-cutting behavior changed.

---

## Fixtures

Fixtures should be:

* small;
* explicit;
* realistic;
* deterministic;
* reusable only when semantics match;
* free from sensitive data.

Avoid giant all-purpose fixtures.

Prefer builders with sensible defaults.

Example:

```go
article := NewArticleFixture(
	WithStatus(StatusInReview),
	WithContent(validContent()),
)
```

Do not hide important setup in deeply magical fixture helpers.

---

## Test Builders

Builders are useful when objects have many required fields.

They should:

* expose meaningful overrides;
* create valid defaults;
* make invalid states explicit;
* remain local to relevant test packages when possible.

Do not use builders to bypass domain constructors.

---

## Golden Files

Golden files may be useful for:

* generated Markdown;
* structured serialization;
* OpenAPI fragments;
* report outputs.

Use them only when differences are easy to review.

Provide an explicit update command.

Do not auto-update golden files in CI.

---

## Test Cleanup

Tests must clean up:

* temporary files;
* database records or schemas;
* LocalStack objects;
* browser state;
* server processes;
* containers they created.

Use test cleanup hooks.

Do not leave resources that affect later tests.

---

## CI Principles

CI must:

* use the same core commands as local development;
* fail clearly;
* avoid hidden mutation;
* use pinned tool versions;
* cache safely;
* upload useful artifacts;
* avoid secrets in logs;
* run only necessary jobs for changed areas where practical;
* remain reproducible.

Do not maintain separate undocumented quality logic only in CI.

---

## Recommended CI Jobs

Potential jobs:

```text
backend-quality
frontend-quality
database-integration
e2e
terraform-quality
security-scan
```

Phase 0 may start with:

```text
backend-quality
frontend-quality
terraform-quality
```

Add integration and E2E jobs as the features exist.

Do not create empty or permanently skipped jobs.

---

## Backend CI

Typical steps:

```text
checkout
setup Go
restore cache
download modules
format check
go vet
golangci-lint
unit tests
build
```

Integration tests may run in a separate job with PostgreSQL.

Do not depend on a manually configured runner database.

---

## Frontend CI

Typical steps:

```text
checkout
setup Node
install from lockfile
typecheck
lint
unit and component tests
build
```

Use:

```bash
npm ci
```

when npm is selected.

Do not use non-deterministic installation commands in CI.

---

## E2E CI

E2E CI may require:

* built application;
* Compose stack;
* seeded database;
* Keycloak setup;
* Playwright browsers;
* health checks;
* logs and screenshots on failure.

Do not start E2E tests before dependencies are ready.

Do not use arbitrary long sleeps.

---

## Terraform CI

Typical steps:

```text
terraform fmt -check
terraform init -backend=false
terraform validate
tflint
security scan
```

Real environment plans may run only with trusted branches and constrained credentials.

Do not allow untrusted pull requests to gain production access.

---

## CI Artifacts

On failure, upload useful artifacts:

* test reports;
* coverage;
* Playwright screenshots;
* traces;
* service logs;
* migration logs;
* Terraform plan text when safe.

Do not upload secrets, raw tokens, or sensitive state.

---

## CI Caching

Cache:

* Go module cache;
* npm cache;
* Playwright browsers when appropriate;
* Terraform provider plugins according to CI strategy.

Cache keys must include lockfiles or version indicators.

Do not cache mutable application outputs that can make tests stale.

---

## Branch Protection

Future repository settings should require:

* pull request review;
* passing quality checks;
* up-to-date branch when appropriate;
* restricted direct pushes to main;
* restricted deployment workflows.

This may be documented even if not managed by code.

Do not assume branch protection exists.

---

## Quality Gates

A change should not merge when:

* code does not compile;
* type checking fails;
* lint fails;
* relevant tests fail;
* migrations fail;
* Terraform validation fails;
* critical security scan fails;
* OpenAPI is inconsistent;
* generated artifacts are stale;
* required documentation is missing.

Do not bypass gates without a documented exception.

---

## Security Scanning

Potential tools:

* `govulncheck`;
* dependency scanning;
* Trivy;
* Checkov;
* secret scanning;
* container scanning.

Introduce tools deliberately.

Do not add several overlapping scanners without ownership.

Findings should have:

* severity;
* context;
* disposition;
* remediation or accepted-risk record.

Do not ignore scans permanently.

---

## Secret Scanning

Enable secret detection in CI when practical.

Never place real secrets in fixtures or examples.

If a secret is committed:

1. rotate it;
2. remove it from history when necessary;
3. invalidate exposed credentials;
4. document the incident.

Deleting the file alone is insufficient.

---

## Container Scanning

Scan production-oriented images.

Evaluate:

* OS packages;
* language dependencies;
* base-image age;
* running user;
* embedded secrets.

Do not block development on every low-severity base-image finding without a triage policy.

Do not ignore critical known vulnerabilities.

---

## Dependency Updates

Automated dependency updates may be introduced later.

Requirements:

* grouped updates when helpful;
* tests run;
* major versions reviewed;
* security updates prioritized;
* release notes checked.

Do not auto-merge major dependency updates without validation.

---

## Regression Tests

Every bug fix should add a regression test when practical.

The test should fail before the fix and pass after it.

Do not add a test that only reproduces implementation details.

Document when a regression test is impossible or disproportionately expensive.

---

## Bug Reproduction

Before fixing a bug:

1. capture expected behavior;
2. reproduce failure;
3. add or identify failing test;
4. implement fix;
5. confirm regression test passes;
6. run related suite.

Do not claim a bug is fixed only because code looks correct.

---

## Non-Functional Testing

Future phases may require:

* performance;
* load;
* resilience;
* security;
* accessibility;
* backup restore;
* disaster recovery.

Do not introduce all non-functional test types in Phase 0.

Add them when operational risk justifies them.

---

## Performance Testing

Useful targets may include:

* species listing;
* article rendering;
* search;
* admin save;
* media upload.

Define:

* workload;
* latency target;
* throughput;
* dataset size;
* environment.

Do not benchmark an empty local database and claim production capacity.

---

## Load Testing

Use load tests only after representative endpoints and deployment architecture exist.

Do not run destructive load tests against shared environments without authorization.

Document rate limits and expected behavior.

---

## Resilience Testing

Future resilience tests may cover:

* PostgreSQL unavailable;
* Redis unavailable;
* LocalStack or S3 unavailable;
* Keycloak unavailable;
* worker retry;
* queue failure.

The application should fail safely and expose meaningful readiness.

Do not create chaos testing before basic integration reliability exists.

---

## Accessibility Quality Gate

Frontend changes should evaluate:

* semantic markup;
* keyboard flow;
* focus;
* labels;
* contrast;
* reduced motion;
* error announcements.

Automated accessibility checks may be part of component or E2E tests.

Do not claim WCAG conformance without a broader audit.

---

## Documentation Tests

Documentation may be validated for:

* broken internal links;
* invalid code examples;
* missing referenced files;
* outdated commands.

Do not create a complex documentation pipeline before the documentation volume warrants it.

At minimum, commands in README should match real Makefile targets.

---

## Generated Code Validation

When generated artifacts exist:

* regenerate in CI;
* compare working tree;
* fail if stale.

Potential artifacts:

* sqlc output;
* OpenAPI types;
* generated documentation.

Do not manually edit generated files.

Do not allow CI and local generation tools to use different versions.

---

## Makefile Quality Commands

Expected targets may include:

```text
format
lint
test
test-unit
test-integration
test-e2e
validate
generate
coverage
```

Only include targets with real implementations.

`make validate` should be non-destructive.

`make test` should have a documented scope.

Do not hide failures with chained commands that continue after errors.

---

## Suggested Validation Matrix

| Area      | Format               | Lint/static               | Unit           | Integration           | Build         | Other           |
| --------- | -------------------- | ------------------------- | -------------- | --------------------- | ------------- | --------------- |
| Backend   | gofmt                | go vet, golangci-lint     | go test        | PostgreSQL/LocalStack | go build      | race, vuln scan |
| Frontend  | formatter            | ESLint, typecheck         | Vitest         | MSW/page integration  | Vite build    | accessibility   |
| Database  | SQL style if adopted | migration lint if adopted | N/A            | migrations/repos      | sqlc generate | rollback        |
| Terraform | terraform fmt        | validate, TFLint          | terraform test | LocalStack plan/apply | N/A           | Checkov/Trivy   |
| Docker    | N/A                  | Dockerfile scan           | N/A            | Compose startup       | image build   | health checks   |

Use this as guidance, not an inflexible requirement.

---

## Required Phase 0 Quality Baseline

Phase 0 should establish:

### Backend

* at least one health-handler test;
* Go formatting;
* `go vet`;
* lint configuration;
* build validation.

### Frontend

* at least one application-shell test;
* TypeScript checking;
* ESLint;
* frontend build.

### Infrastructure

* Docker Compose config validation;
* Terraform format and validate;
* pinned tool or image versions.

### CI

* backend quality workflow;
* frontend quality workflow;
* infrastructure quality workflow.

### Documentation

* commands documented;
* known limitations reported.

Do not require full E2E coverage during Phase 0.

---

## Completion Validation

Before declaring a task complete:

1. identify changed areas;
2. run targeted tests during implementation;
3. run broader relevant tests;
4. run formatting;
5. run lint/static analysis;
6. run build;
7. validate migrations if changed;
8. validate Docker if changed;
9. validate Terraform if changed;
10. inspect uncommitted generated changes;
11. confirm acceptance criteria;
12. report commands actually executed.

Do not use “should pass” as evidence.

---

## Validation Reporting

Report:

* exact command;
* whether it passed;
* whether it was skipped;
* reason for skipping;
* remaining risk.

Example:

```text
go test ./... — passed
npm run build — passed
make test:e2e — not executed because the Keycloak container was unavailable
```

Do not claim hidden or assumed success.

---

## Quality Exceptions

A temporary exception must include:

* exact failed or skipped check;
* reason;
* risk;
* owner;
* follow-up action;
* expiry or review point when appropriate.

Do not normalize permanent exceptions.

Do not disable a quality gate without documenting why.

---

## Documentation Requirements

When testing or quality behavior changes, evaluate updates to:

```text
README.md
docs/development/testing.md
docs/development/local-setup.md
docs/runbooks/
docs/architecture/
.github/workflows/
Makefile
```

Document:

* test levels;
* required services;
* commands;
* coverage approach;
* CI jobs;
* failure artifacts;
* local troubleshooting;
* known limitations.

Do not leave test execution knowledge only inside CI YAML.

---

## Implementation Workflow

When using this skill:

1. identify the behavior and risk;
2. choose the appropriate test level;
3. inspect existing test utilities;
4. define isolation strategy;
5. create the smallest valuable test;
6. avoid duplicating coverage;
7. update quality configuration if needed;
8. run targeted validation;
9. run broader relevant validation;
10. update CI when the local command should become a gate;
11. update documentation;
12. report remaining gaps.

---

## Expected Deliverables

Depending on the task, deliverables may include:

* unit tests;
* integration tests;
* E2E tests;
* fixtures;
* test builders;
* CI workflows;
* lint configuration;
* type-check configuration;
* coverage configuration;
* security scans;
* Makefile targets;
* validation scripts;
* testing documentation;
* quality-gate updates.

Do not add unrelated tools or duplicate quality systems.

---

## Definition of Done

A testing or quality task is complete only when:

* the protected behavior is clear;
* the chosen test level is appropriate;
* tests are deterministic;
* tests are isolated;
* failure messages are useful;
* relevant positive and negative paths are covered;
* lint and static checks are configured appropriately;
* CI uses reproducible commands;
* required gates pass;
* skipped validations are reported;
* documentation is updated;
* no flaky behavior is knowingly ignored;
* no success is falsely claimed.

---

## Prohibited Practices

Do not:

* test only implementation details;
* create tests only to increase coverage;
* remove failing tests to make CI pass;
* disable lint globally for local issues;
* use arbitrary sleeps as synchronization;
* share mutable test state without isolation;
* depend on test execution order;
* point tests at production or shared databases;
* use real credentials or personal data in tests;
* mock the system under test completely;
* use giant snapshots as primary assertions;
* retry unit tests to hide flakiness;
* claim E2E confidence without running E2E tests;
* claim accessibility compliance from one automated tool;
* create CI commands that differ silently from local commands;
* add scanners without ownership;
* declare completion without executing relevant quality gates.

---

## Completion Report

After completing a testing or quality task, report:

```markdown
## Quality scope

## Risk assessment

## Test levels added or changed

## Fixtures and isolation

## Static analysis and linting

## CI changes

## Coverage and regression protection

## Validation performed

## Skipped checks and remaining risk

## Documentation updates

## Limitations
```

Keep the report factual and based on actual work performed.
