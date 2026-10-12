# skill: workflow/verification
# triggers: verify, verification, check, done, complete, finished, ship, deploy, does it work, confirm, validate, test it

## Iron Law
**NEVER claim a task is complete without running fresh verification.**
"Should work" is not evidence. Exit code 0 is.
Violating the letter of this rule is violating the spirit of it.

## Verification Is FORBIDDEN to Skip When
```
FORBIDDEN to skip:
  ✗ After any code change before claiming it's done
  ✗ After a deploy before declaring success
  ✗ After a migration before marking it complete
  ✗ After a bug fix before closing the issue

OK to skip:
  ✓ Documentation-only changes (verify formatting, not behavior)
  ✓ Config comments/whitespace
  ✓ Changes to dead code paths explicitly marked deprecated
```

## Verification Checklist by Change Type

### Code Change
```bash
# 1. Tests pass
npm test                    # or: pytest, go test ./..., cargo test

# 2. No type errors
npx tsc --noEmit            # or: mypy src/, pyright

# 3. Linting clean
npm run lint                # or: ruff check ., golangci-lint run

# 4. The specific behavior works
curl -X POST http://localhost:3000/api/thing \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
# → Observe actual response, not "should work"
```

### Deploy
```bash
# 1. Deployment completed
kubectl rollout status deployment/app --timeout=5m

# 2. Smoke test the actual endpoint
curl -f https://app.example.com/health
echo "Status: $?"

# 3. Check for new errors in logs (look 2 min after deploy)
kubectl logs -f deploy/app --tail=50 --since=2m | grep -i error

# 4. Check metrics (no spike in 5xx)
# → Open Grafana / check CloudWatch alarms
```

### Migration
```sql
-- 1. Schema matches expected
\d table_name   -- psql
SELECT column_name, data_type FROM information_schema.columns WHERE table_name='...';

-- 2. Row counts reasonable
SELECT COUNT(*) FROM affected_table;

-- 3. Sample data looks correct
SELECT * FROM affected_table LIMIT 5;

-- 4. Application reads/writes correctly
-- Run integration test or manual smoke test
```

### Infrastructure (Terraform)
```bash
# 1. Plan shows exactly what you expected
terraform plan -var-file=env/${ENV}.tfvars

# 2. Resources exist
aws eks describe-cluster --name my-cluster
aws rds describe-db-instances --db-instance-identifier my-db

# 3. Application still reachable
curl -f https://app.example.com/health
```

## Completion Statement Format
When reporting a task as done, include:
```
✓ [What was done]
✓ Verified: [exact command run] → [exact output observed]
✓ No regressions: [test suite result]
```

Never say:
```
✗ "Done! It should be working now."
✗ "Looks good to me."
✗ "I think this fixes it."
✗ "Let me know if it works."
```

## Red Flags — STOP
- "I'm confident this works" → Run the test anyway.
- "The logic is clearly correct" → Logic errors don't care about your confidence.
- "The tests would catch this" → Run the tests, then say they catch it.
- "I'll verify after merging" → Verify before merging.
- "The CI will check it" → CI runs later; verify locally first.

**All of these mean: run the verification step right now.**

## Gotchas

1. **Cached results give false confidence.** If you run a test right after the previous run, you might be seeing cached output. Force a fresh run: `npm test -- --clearCache`, `pytest --cache-clear`.

2. **Testing the wrong endpoint/environment.** Verify against the same environment that was changed. Verifying dev after a prod deploy is not verification.

3. **Green tests, broken feature.** Tests can pass and the feature can still be broken if the test doesn't actually cover the path you changed. Read the test, not just the result.

4. **Smoke test timing.** After K8s rollout, wait 15-30 seconds before hitting health endpoints — pods need to initialize.

5. **`exit 0` vs. correct behavior.** A script that exits 0 but produces wrong output has passed verification theater, not verification. Check actual output values.

## Related Skills
- **workflow/debugging**: When verification reveals a failure, switch to this skill
- **workflow/planning**: Your plan's verification section defines what you run here
- **devops/cicd**: CI/CD pipelines are automated verification — design them to match this checklist
- **dev/testing**: Write tests whose passing = meaningful verification for this feature
