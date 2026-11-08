import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).parent.parent.parent

# Keywords that hint a skill is about software architecture or software engineering, one set per area
# Used by Mechanisms.save_found to rank only software skills, and by save_software to record the counts
# All lowercase --> compare against the lowercased skill text
# Broad words (architecture, requirements, pipeline, deploy, release, debug) are left out, see keywords_proposal.md
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


# Fewest different keywords of a set a skill needs to be kept: Architecture words are specific, Engineering words need a second one
MINIMUM = {"Architecture": 1, "Engineering": 2}


'''
Counts the different keywords of every SOFTWARE set in a lowercased skill text --> {"Architecture": 0, "Engineering": 3}
'''
def software_hits(text):
    return {area: sum(keyword in text for keyword in keywords) for area, keywords in SOFTWARE.items()}


'''
True when a lowercased skill text reaches the MINIMUM of at least one SOFTWARE set --> {"Architecture": 0, "Engineering": 3} --> True
'''
def is_software(text):
    hits = software_hits(text)
    return any(hits[area] >= MINIMUM[area] for area in SOFTWARE)


'''
Keeps the skills one mechanism saved (Mechanisms_<mechanism>/Found) that hold at least MINIMUM keywords of one SOFTWARE set
Saves them into Mechanisms/SWE_SKILLS/<mechanism> as <file_sha>.md
plus index.json, which records where the skill comes from and its keyword counts
Returns the kept skills, most architecture + engineering keywords first
'''
def save_software(mechanism):
    source = ROOT / "Mechanisms" / f"Mechanisms_{mechanism}" / "Found"
    swe = ROOT / "Mechanisms" / "SWE_SKILLS" / mechanism
    swe.mkdir(parents=True, exist_ok=True)
    for old in swe.glob("*.md"):
        old.unlink()

    #1-Count the different keywords of every set in each saved skill and keep it when one set reaches its MINIMUM --> {"Architecture": 0, "Engineering": 3} --> kept
    kept = []
    for row in json.loads((source / "index.json").read_text(encoding="utf-8")):
        content = (source / f"{row['file_sha']}.md").read_text(encoding="utf-8")
        hits = software_hits(content.lower())
        if any(hits[area] >= MINIMUM[area] for area in SOFTWARE):
            kept.append((row, content, hits))

    #2-Save each kept skill, most software keywords first (ties broken by file_sha)
    kept = sorted(kept, key=lambda skill: (-sum(skill[2].values()), skill[0]["file_sha"]))
    for row, content, _ in kept:
        (swe / f"{row['file_sha']}.md").write_text(content, encoding="utf-8")

    #3-Index of the kept skills --> [{"mechanism": "Ask", "file_sha": "00a1...", "mechanism_keywords": 6, "architecture": 2, "engineering": 0, "repo": "org/repo", ...}, ...]
    # commit_author is an anonymized code, and None when the file is outside the commit-history sample
    index = [
        {
            "mechanism": mechanism, "file_sha": row["file_sha"], "mechanism_keywords": row["keywords"],
            "architecture": hits["Architecture"], "engineering": hits["Engineering"],
            "repo": row["repo"], "path": row["path"], "owner": row["owner"], "commit_author": row["commit_author"],
        }
        for row, _, hits in kept
    ]
    (swe / "index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")
    return pd.DataFrame(index)
