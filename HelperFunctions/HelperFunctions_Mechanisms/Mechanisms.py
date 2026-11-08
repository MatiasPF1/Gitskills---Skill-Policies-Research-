import json
import sqlite3
from pathlib import Path

import pandas as pd

from HelperFunctions.HelperFunctions_Adoption.Adoption import SKILL_FILE
from HelperFunctions.HelperFunctions_Mechanisms.Architectural_Engineer import is_software


ROOT = Path(__file__).parent.parent.parent
DB_PATH = ROOT / "SQL_Lite_Source" / "agent_skills_sample.db"
con = sqlite3.connect(DB_PATH)

# How many skills are kept per mechanism: the software skills whose text holds the most different keywords
TOP = 100

# Fewest different keywords of a mechanism a skill needs to be saved under it: one keyword alone is weak evidence
MINIMUM_KEYWORDS = 2

# Keywords that hint at a human-control mechanism in a skill text, one set per mechanism
# For a given software task, when should an agent act, ask, or escalate to a human?
# All lowercase --> compare against the lowercased skill text
# The order is the run order: a skill saved by an earlier mechanism is skipped by the later ones
MECHANISMS = {
    # Ask: the agent requests clarification
    "Ask": {
        "ask the user", "ask the developer",
        "clarify", "clarifying question", "clarification",
        "ambiguous", "if unclear", "if unsure", "if not sure",
        "do not assume", "don't assume", "do not guess", "don't guess",
        "askuserquestion",
    },
    # Act: the agent continues autonomously
    "Act": {
        "autonomously", "fully autonomous",
        "do not ask", "don't ask", "never ask", "no need to ask",
        "do not stop", "don't stop", "do not pause", "don't pause",
        "do not wait for", "don't wait for",
        "keep going", "continue until",
        "proceed directly", "proceed immediately", "proceed automatically",
        "without prompting", "without stopping", "without waiting", "without human intervention",
        "no confirmation needed", "use your judgment", "sensible default",
    },
    # Escalate: the agent requires explicit approval before a consequential step
    "Escalate": {
        "wait for confirmation", "wait for approval",
        "explicit confirmation", "explicit approval", "explicit permission",
        "confirm with", "confirm before", "before proceeding",
        "user approval", "ask for permission",
        "do not proceed until", "don't proceed until",
        "do not proceed without", "don't proceed without",
        "sign-off", "human-in-the-loop",
    },
}


# Every keyword from all mechanisms in one set
KEYWORDS = set().union(*MECHANISMS.values())


'''
Saves the TOP software skills (is_software) holding the most keywords into Mechanisms/Mechanisms_<mechanism>/Found as <file_sha>.md
plus Found/index.json, which records where each saved skill comes from (repo, path, owner, first commit author)
Skips skills whose name (skill folder) is already in taken, so forks of one skill and skills saved by another mechanism are not repeated
Adds the saved names to taken
Returns the saved skills with their keyword count, highest first
'''
def save_found(keywords, mechanism, taken):
    found = ROOT / "Mechanisms" / f"Mechanisms_{mechanism}" / "Found"
    found.mkdir(parents=True, exist_ok=True)
    for old in found.glob("*.md"):
        old.unlink()

    #1-Count how many different keywords every distinct software skill text holds, skipping skills under MINIMUM_KEYWORDS -->[(4, "00a1...", "---name: ...", "org/repo", ".claude/skills/x/SKILL.md", "d083..."), ...]
    sql = f"SELECT file_sha, content, repo_full_name, path, first_commit_author FROM artifacts WHERE dedup_primary = 1 AND {SKILL_FILE}"
    rows = [
        (sum(keyword in content.lower() for keyword in keywords), file_sha, content, repo, path, author)
        for file_sha, content, repo, path, author in con.execute(sql)
        if is_software(content.lower())
    ]
    rows = [row for row in rows if row[0] >= MINIMUM_KEYWORDS]

    #2-Go down the ranking (ties broken by file_sha) and keep the TOP skills whose name is not taken yet
    # name = skill folder --> ".claude/skills/skill-creator/SKILL.md" --> "skill-creator" (the repo when SKILL.md sits at the root)
    top = []
    for row in sorted(rows, key=lambda row: (-row[0], row[1])):
        name = Path(row[4]).parent.name or row[3]
        if name in taken:
            continue
        taken.add(name)
        top.append(row)
        if len(top) == TOP:
            break
    for _, file_sha, content, _, _, _ in top:
        (found / f"{file_sha}.md").write_text(content, encoding="utf-8")

    #3-Index of the saved skills --> [{"file_sha": "00a1...", "keywords": 6, "repo": "org/repo", "owner": "org", ...}, ...]
    # commit_author is an anonymized code, and None when the file is outside the commit-history sample
    index = [
        {"file_sha": file_sha, "keywords": hits, "repo": repo, "path": path, "owner": repo.split("/")[0], "commit_author": author}
        for hits, file_sha, _, repo, path, author in top
    ]
    (found / "index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")
    return pd.DataFrame(index)
