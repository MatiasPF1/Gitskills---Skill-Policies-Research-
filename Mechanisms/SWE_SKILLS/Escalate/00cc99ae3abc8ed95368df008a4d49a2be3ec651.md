---
name: diagnose-errors
description: Diagnose production errors from Sentry and Better Stack. Use when the user asks to check errors, diagnose issues, triage alerts, or investigate production problems.
---

# Diagnose Errors Skill

Fetch, triage, and diagnose production errors from Sentry and Better Stack. Classifies errors as mundane (with silencing recommendations) or genuine (with root cause analysis on a worktree).

## Service Configuration

### Sentry
- **Organization**: `rhys-murray-g3`
- **Region URL**: `https://us.sentry.io`
- **Primary project**: `wedding-rsvp`

### Better Stack
- **Production logs**: Source ID `528852` ("FlyIO Production")
- **Staging logs**: Source ID `613405` ("FlyIO Staging")

## Instructions

When the user asks to diagnose errors:

### 1. Determine scope

- If the user specifies a source (e.g. "check Sentry", "check Better Stack logs"), use only that source
- If the user provides a specific issue URL or ID, fetch that directly
- If the user specifies a time window (e.g. "last week", "since Monday"), use that
- **Default**: Check both Sentry and Better Stack for errors from the **last 24 hours**

### 2. Fetch errors

**From Sentry:**
- Use `search_issues` to find unresolved issues within the time window (always pass `regionUrl: 'https://us.sentry.io'`, use `query: "is:unresolved lastSeen:>YYYY-MM-DDT00:00:00"` with the appropriate cutoff)
- For a specific issue, use `get_sentry_resource` to get full details including stacktrace
- Use `search_issue_events` to understand frequency and patterns

**From Better Stack:**

Better Stack errors are stored as **log entries** (not in the exceptions/error-tracking layer). Query the logs source filtering by `level = 'error'` or `level = 'fatal'`.

Use `telemetry_query` with these patterns:

```sql
-- Grouped error summary (last 24 hours)
SELECT
  _pattern,
  JSONExtract(raw, 'level', 'Nullable(String)') AS log_level,
  any(JSONExtract(raw, 'message', 'Nullable(String)')) AS example_message,
  count(*) AS occurrences,
  max(dt) AS last_seen,
  min(dt) AS first_seen
FROM s3Cluster(primary, t221312_flyio_production_s3)
WHERE _row_type = 1
  AND dt BETWEEN now() - INTERVAL 24 HOUR AND now()
  AND JSONExtract(raw, 'level', 'Nullable(String)') IN ('error', 'fatal', 'ERROR', 'FATAL')
GROUP BY _pattern, log_level
ORDER BY occurrences DESC
LIMIT 20
```

Key rules:
- Source ID: `528852`, table: `t221312.flyio_production`
- Use `s3Cluster(primary, t221312_flyio_production_s3)` with `_row_type = 1` for historical logs (>30 min old)
- Use `remote(t221312_flyio_production_logs)` for recent logs (<30 min old)
- All fields are inside the `raw` JSON column — use `JSONExtract(raw, ..., 'Nullable(String)')` 
- The `level` field values are lowercase: `'error'`, `'fatal'`
- The `_pattern` column groups similar log messages (dynamic values stripped)
- Always use `Nullable()` types in `JSONExtract` to avoid query failures
- Always include `LIMIT`

For individual occurrences of a specific pattern:
```sql
SELECT
  dt,
  JSONExtract(raw, 'level', 'Nullable(String)') AS log_level,
  JSONExtract(raw, 'message', 'Nullable(String)') AS message,
  JSONExtract(raw, 'context', 'http', 'path', 'Nullable(String)') AS request_path,
  JSONExtract(raw, 'context', 'http', 'method', 'Nullable(String)') AS request_method
FROM s3Cluster(primary, t221312_flyio_production_s3)
WHERE _row_type = 1
  AND dt BETWEEN now() - INTERVAL 24 HOUR AND now()
  AND _pattern = '<pattern_hash>'
ORDER BY dt DESC
LIMIT 50
```

### 3. Triage each error

Read the `resources/known-mundane-errors.md` file for the current list of known mundane error patterns.

For each error, classify it as **mundane** or **genuine**:

**Mundane indicators:**
- Matches a pattern in the known mundane errors list
- Bot/crawler traffic (user agents containing bot, spider, crawler, etc.)
- Client-side errors from unsupported browsers
- Expected rate-limiting or timeout errors
- Errors from health check endpoints
- ActionController::RoutingError for favicon.ico, robots.txt, .env, wp-admin, etc.
- Net::ReadTimeout from external services during expected maintenance windows

**Genuine indicators:**
- Affects real user flows (RSVP submission, login, communication sending)
- New error type not seen before
- Increasing frequency
- Involves data integrity (nil where not expected, missing associations)
- Background job failures that affect delivery (SMS, email)

### 4. Present findings

Format the output as:

```
# Error Diagnosis Report

## Summary
[X errors found: Y mundane, Z genuine]

## Mundane Errors (can be silenced)

### [Error Title]
- **Source**: Sentry / Better Stack
- **Frequency**: [count] in [timeframe]
- **Why it's mundane**: [explanation]
- **How to silence**:
  - [Specific silencing recommendation — see section below]

## Genuine Errors (need investigation)

### [Error Title]
- **Source**: Sentry / Better Stack
- **Frequency**: [count] in [timeframe]
- **Impact**: [what user flow is affected]
- **Stacktrace summary**: [key frames]
- **Preliminary assessment**: [what likely caused this]
```

### 5. Silencing recommendations

For mundane errors, recommend the most appropriate silencing method:

**Sentry silencing options:**
- **Ignore in Sentry**: For errors you never want to see — use `mcp__claude_ai_Sentry__get_sentry_resource` to link to the issue, instruct user to ignore/delete
- **Inbound filter**: For entire classes of errors (e.g. bot traffic) — recommend adding to Sentry project inbound filters
- **before_send filter**: For app-level filtering — suggest code for `config/initializers/sentry.rb`:
  ```ruby
  config.before_send = lambda do |event, hint|
    # Return nil to drop the event
    return nil if event.exception&.values&.any? { |e| e.type == "SomeError" }
    event
  end
  ```

**Better Stack silencing options:**
- **Drop filter**: Recommend creating a drop filter in Better Stack source settings for the pattern
- **Alert rule adjustment**: If it's triggering alerts but is expected, recommend adjusting the alert condition

### 6. Genuine error investigation

**STOP HERE and present findings to the user before proceeding.**

Wait for user confirmation on which genuine errors to investigate. Once confirmed:

- Enter a worktree for investigation
- Use Sentry's `analyze_issue_with_seer` for AI-powered root cause analysis if available
- Read the relevant source files identified in the stacktrace
- Identify the root cause
- Propose a fix (but do not implement without user approval)
- Plan the fix including test coverage

## Examples

**User**: "Check for errors"
**Action**: Query both Sentry and Better Stack for recent unresolved errors, triage all of them

**User**: "Diagnose WEDDING-RSVP-42"
**Action**: Fetch that specific Sentry issue, get full details, classify and investigate

**User**: "Any errors in Better Stack?"
**Action**: Query Better Stack production source only for recent errors

**User**: "Check staging errors"
**Action**: Use Better Stack staging source (613405) and Sentry with environment filter

## Notes

- Always present the triage before diving into investigation
- The user should confirm which genuine errors to investigate before you start a worktree
- When silencing, prefer the least invasive option (Sentry ignore > inbound filter > code filter)
- Update `resources/known-mundane-errors.md` when new mundane patterns are identified
- For Better Stack queries, always call `telemetry_get_errors_query_instructions_tool` first to get the correct schema before writing SQL
