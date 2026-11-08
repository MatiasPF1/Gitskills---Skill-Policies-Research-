# Skills_Architecture_Engineer — keyword proposal

**Goal:** from the skills found by the mechanism step (Ask → Act → Escalate), keep only those whose task is software engineering or software architecture.

**Matching:** same rule as `Mechanisms.py`, which checks whether each keyword appears anywhere in the lowercased skill text and counts distinct keywords.

All counts below come from `agent_skills_sample.db` (12,882 distinct skills, `dedup_primary = 1`), checked on 2026-11-02.

---

## 1. Proposed keywords

Two sets, kept in a dict like `MECHANISMS`.

- **Engineering** keywords are grouped by SE activity (SWEBOK knowledge areas), so a later step can tell *which* activity a skill covers.
- **Architecture** keywords are about structure and design decisions, not about writing code.

```python
SOFTWARE = {
    # Architecture: structure of the system and the design decisions behind it
    "Architecture": {
        "software architecture", "software design", "system design", "architectural",
        "architecture decision record", "design doc", "design pattern",
        "microservice", "monolith", "event-driven", "domain-driven", "bounded context",
        "hexagonal", "clean architecture", "layered architecture",
        "c4 model", "component diagram", "sequence diagram",
        "api design", "api contract",
        "coupling", "cohesion", "separation of concerns", "dependency injection", "solid principle",
        "scalability", "non-functional", "quality attribute",
    },
    # Engineering: the activities of building and keeping software
    "Engineering": {
        # Requirements
        "user story", "user stories", "acceptance criteria", "functional requirement",
        # Construction
        "implementation plan", "refactor", "code smell", "clean code", "code style",
        "linter", "linting", "type check", "static analysis",
        # Testing
        "unit test", "integration test", "end-to-end test", "e2e test", "test suite",
        "test coverage", "test-driven", "tdd", "regression test", "failing test",
        # Review and quality
        "code review", "pull request", "review the diff", "code quality", "technical debt", "tech debt",
        # Release and configuration
        "ci/cd", "continuous integration", "semantic versioning", "changelog", "rollback",
        "database migration", "schema migration",
        # Maintenance
        "root cause", "bug fix", "stack trace", "legacy code", "backward compatib",
    },
}
```

**Proposed rule:** a skill counts as software engineering/architecture if it holds **≥ 1 Architecture keyword or ≥ 2 Engineering keywords**.

- **Architecture: 1 is enough.** These terms are specific; a single "bounded context" or "api contract" already places the skill.
- **Engineering: needs 2.** One "pull request" or "rollback" can appear in a skill about something else. Two different activities make it an engineering skill.

## 2. Words left out on purpose

These were tested and dropped because they are too broad or match inside other words.

| Word | Skills hit | Why dropped |
|---|---|---|
| `architecture` | 2,341 | Used for any "project architecture" overview, including non-software (e.g. agent or prompt architecture) |
| `requirements` | 2,504 | "Requirements: Python 3.10", tool prerequisites |
| `pipeline` | 1,696 | Data, ML and content pipelines |
| `deploy` / `deployment` | 1,739 / 1,093 | Too broad, and hosting/marketing skills use them |
| `release` | 1,311 | Press releases, music, generic "release notes" |
| `debug` | 1,663 | Generic ("debug mode", "debug logging") |
| `specification` / `use case` | 624 / 768 | Generic English |
| `trade-off` / `tradeoff` | 349 / 301 | Any decision-making skill (product, business) |
| `adr` | 705 | Matches inside words ("quadrant", "Madrid"); only 238 as a whole word. `architecture decision record` is used instead |
| `lint` | 972 | Matches inside words; `linter` and `linting` are used instead |
| `prd` | 249 | Product docs; more product than engineering |

## 3. Where it goes in the pipeline

There are two options. The numbers decide between them.

### Option A: filter *after* the mechanism step (as first planned)

Run the rule on the 90 skills already in `Mechanisms_<m>/Found`:

| Mechanism | Found | Arch ≥ 1 | Eng ≥ 2 | **Kept (Arch ≥ 1 or Eng ≥ 2)** |
|---|---|---|---|---|
| Ask | 30 | 13 | 14 | **20** |
| Act | 30 | 14 | 15 | **18** |
| Escalate | 30 | 7 | 12 | **14** |
| Total | 90 | | | **52** |

It is simple, but it leaves different, smaller groups per mechanism (14–20).

### Option B: filter *the candidates* before the TOP 30 (recommended)

First keep only the software skills (2,912 of 12,882 meet the rule). Then run Ask → Act → Escalate on that pool exactly as now. Each mechanism still gets 30 skills, all of them software engineering/architecture.

There are enough candidates:

| Mechanism | Software skills with ≥ 2 mechanism keywords | with ≥ 3 |
|---|---|---|
| Ask | 414 | 177 |
| Act | 71 | 26 |
| Escalate | 137 | 38 |

Act is the tightest pool, but 71 is still above 30.

**Recommendation: Option B.** The groups stay the same size (30 / 30 / 30), the no-overlap rule still holds, and "software skills that act / ask / escalate" is a cleaner population to describe in the paper than "the 90, minus some".

In code it is one extra condition in `save_found` step #1: skip a row unless it meets the rule above.

**Implemented: Option B, with TOP = 100.** `Mechanisms.save_found` ranks only skills that pass `is_software` (in `Architectural_Engineer.py`). `save_software` then copies them with their counts into `Mechanisms/SWE_SKILLS/<mechanism>`. Run everything with `python Mechanisms/initializer.py`.

## 4. Open points

- **Plurals and prefixes:** matching is by substring, so `refactor` also catches "refactoring" and `backward compatib` catches "compatible / compatibility". For the same reason, keywords are written in their shortest form (`solid principle` also matches "SOLID principles"). Word-boundary regex would miss these forms.
- **Keep the activity grouping?** If the engineering activity is reported later (e.g. "most Escalate skills are about release"), `Engineering` can be split into its six sub-sets, using the same comments as keys.
- **Validation:** before freezing the list, read ~20 kept and ~20 dropped skills and check that the rule agrees with a human label.
