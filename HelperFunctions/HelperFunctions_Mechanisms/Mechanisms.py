import sqlite3
from pathlib import Path

import pandas as pd

from HelperFunctions.HelperFunctions_Adoption.Adoption import SKILL_FILE


ROOT = Path(__file__).parent.parent.parent
DB_PATH = ROOT / "SQL_Lite_Source" / "agent_skills_sample.db"
con = sqlite3.connect(DB_PATH)

# How many skills are kept per mechanism: the ones whose text holds the most different keywords
TOP = 15

# Keywords that hint at a human-control mechanism in a skill text, one set per mechanism
# All lowercase --> compare against the lowercased skill text

# Scope boundary: what the agent must leave alone
SCOPE_BOUNDARY = {
    "do not modify", "don't modify", "never modify",
    "do not edit", "don't edit", "never edit",
    "do not change", "don't change", "never change",
    "do not touch", "don't touch", "never touch",
    "never delete", "never remove", "never overwrite",
    "never commit", "never push",
    "only modify", "read-only", "out of scope", "off-limits", "must not",
}

# Clarification trigger: when the agent should ask instead of guessing
CLARIFICATION_TRIGGER = {
    "ask the user", "ask the developer",
    "clarify", "clarifying question", "clarification",
    "ambiguous", "if unclear", "if unsure", "if not sure",
    "do not assume", "don't assume", "do not guess", "don't guess",
    "askuserquestion",
}

# Approval gate: when the agent must wait for a human yes
APPROVAL_GATE = {
    "wait for confirmation", "wait for approval",
    "explicit confirmation", "explicit approval", "explicit permission",
    "confirm with", "confirm before", "before proceeding",
    "user approval", "ask for permission",
    "do not proceed until", "don't proceed until",
    "do not proceed without", "don't proceed without",
    "sign-off", "human-in-the-loop",
}

# Planning transparency: the agent shows its plan before acting
PLANNING_TRANSPARENCY = {
    "present a plan", "show a plan", "propose a plan", "outline a plan",
    "plan mode",
    "before implementing", "before making changes", "before writing code",
    "explain what", "explain why", "summarize the changes",
}

# Validation requirement: the agent must check its work before finishing
VALIDATION_REQUIREMENT = {
    "run the tests", "tests pass",
    "run lint", "run the linter", "typecheck",
    "verify that",
    "before claiming", "before declaring", "before marking",
    "do not claim", "don't claim",
    "evidence", "definition of done",
}


# Escalation / rollback rule: the agent stops or undoes instead of pushing on
ESCALATION_ROLLBACK = {
    "stop and ask", "stop and report",
    "escalate", "rollback", "roll back",
    "do not proceed", "don't proceed", "do not continue", "don't continue",
    "if stuck", "if blocked",
    "report to the user", "workaround", "abort",
}


# Every keyword from all six mechanisms in one set
KEYWORDS = (
    SCOPE_BOUNDARY | CLARIFICATION_TRIGGER | APPROVAL_GATE
    | PLANNING_TRANSPARENCY | VALIDATION_REQUIREMENT | ESCALATION_ROLLBACK
)


'''
Saves the TOP skills holding the most keywords into Mechanisms/Mechanisms_<mechanism>/Found as <file_sha>.md
Returns the saved skills with their keyword count, highest first
'''
def save_found(keywords, mechanism):
    found = ROOT / "Mechanisms" / f"Mechanisms_{mechanism}" / "Found"
    
    #1-Count how many different keywords every distinct skill text holds --> [(4, "00a1...", "---\nname: ..."), ...]
    rows = [
        (sum(keyword in content.lower() for keyword in keywords), file_sha, content)
        for file_sha, content in con.execute(f"SELECT file_sha, content FROM artifacts WHERE dedup_primary = 1 AND {SKILL_FILE}")
    ]
    
    #2-Keep the TOP with the most keywords (ties broken by file_sha) and save each one
    top = sorted(rows, key=lambda row: (-row[0], row[1]))[:TOP]
    for _, file_sha, content in top:
        (found / f"{file_sha}.md").write_text(content, encoding="utf-8")
    return pd.DataFrame([(file_sha, hits) for hits, file_sha, _ in top], columns=["file_sha", "keywords"])
