import sqlite3
from pathlib import Path

import pandas as pd


pd.set_option("display.max_rows", None)

DB_PATH = Path(__file__).parent.parent.parent / "SQL_Lite_Source" / "agent_skills_sample.db"
con = sqlite3.connect(DB_PATH)

# Star buckets: (label, lowest star count in the bucket), smallest first
STAR_BUCKETS = [("0", 0), ("1-9", 1), ("10-99", 10), ("100-999", 100), ("1000+", 1000)]

# Repos that hold a real agent skill: an exact SKILL.md, or a look-alike (skill.md / Skill.md / SKILL.MD)
# that still looks like a skill --> valid name/description front matter, or sits in a skills folder.
# Drops look-alikes that are ordinary notes (e.g. D&D rules, course notes)
SKILL_FILE = "(filename = 'SKILL.md' OR frontmatter_valid = 1 OR location_class IN ('canonical', 'skills-dir'))"
SKILL_REPOS = f"SELECT repo_full_name FROM artifacts WHERE {SKILL_FILE}"


'''
Reads one column of repos; skills_only=True keeps only repos in SKILL_REPOS
'''
def repo_column(col, skills_only):
    sql = f'SELECT "{col}" FROM repos'
    if skills_only:
        sql += f" WHERE full_name IN ({SKILL_REPOS})"
    return con.execute(sql)


'''
Adds a percentage column: each count as a % of all repos (rounded to 2 decimals)
'''
def add_percentage(df):
    df["percentage"] = (df["count"] / df["count"].sum() * 100).round(2)
    return df


'''
RQ 1a - Count repos per primary programming language (one repo = one vote)
'''
def language_counts(skills_only=True):
    #1-Count every repo into a dictionary --> {"Python": 3862, "TypeScript": 2706, ...}
    counts = {}
    for (language,) in repo_column("language", skills_only):
        language = language or "Unknown"  # None (metadata missing) and "" (no language detected)
        counts[language] = counts.get(language, 0) + 1

    #2-Dictionary --> key/value DataFrame, most popular first
    return add_percentage(pd.DataFrame(counts.items(), columns=["language", "count"]).sort_values(
        "count", ascending=False, ignore_index=True
    ))


'''
RQ 1a - Count repos per star bucket (popularity)
'''
def star_counts(skills_only=True):
    #1-Start every bucket at 0 so empty buckets still show --> {"0": 0, "1-9": 0, ..., "Unknown": 0}
    counts = {label: 0 for label, _ in STAR_BUCKETS}
    counts["Unknown"] = 0
    #2-Put each repo in the highest bucket its stars reach
    for (stars,) in repo_column("stars", skills_only):
        if stars is None:  # metadata missing
            label = "Unknown"
        else:
            label = next(label for label, low in reversed(STAR_BUCKETS) if stars >= low)
        counts[label] += 1
    #3-Dictionary --> key/value DataFrame, kept in bucket order
    return add_percentage(pd.DataFrame(counts.items(), columns=["stars", "count"]))

'''
RQ 1a - Count repos per creation year (age)
'''
def created_year_counts(skills_only=True):
    #1-Count every repo by the year it was created --> {"2026": 9755, "2025": 1250, ...}
    counts = {}
    for (created_at,) in repo_column("created_at", skills_only):
        year = created_at[:4] if created_at else "Unknown"  # "2026-07-20T09:51:07Z" --> "2026"
        counts[year] = counts.get(year, 0) + 1

    #2-Dictionary --> key/value DataFrame, oldest year first ("Unknown" sorts last)
    return add_percentage(pd.DataFrame(sorted(counts.items()), columns=["repo_created_year", "count"]))


'''
RQ 1a - Count repos per month of their last push (activity)
'''
def pushed_month_counts(skills_only=True):
    #1-Count every repo by the month it was last pushed --> {"2026-07": 4829, "2026-06": 2357, ...}
    counts = {}
    for (pushed_at,) in repo_column("pushed_at", skills_only):
        month = pushed_at[:7] if pushed_at else "Unknown"  # "2026-07-21T08:41:38Z" --> "2026-07"
        counts[month] = counts.get(month, 0) + 1

    #2-Dictionary --> key/value DataFrame, newest month first, "Unknown" last
    unknown = counts.pop("Unknown", 0)
    rows = sorted(counts.items(), reverse=True) + [("Unknown", unknown)]
    return add_percentage(pd.DataFrame(rows, columns=["last_pushed_month", "count"]))


'''
RQ 1a - Count repos per month of their first skill commit (speed of spread)
Only repos in the commit-history sample have a date
'''
def adoption_month_counts(skills_only=True):
    #1-Earliest skill commit per repo
    where = f"AND {SKILL_FILE}" if skills_only else ""
    sql = f"SELECT MIN(first_commit_at) FROM artifacts WHERE first_commit_at IS NOT NULL {where} GROUP BY repo_full_name"

    #2-Count repos by that month --> {"2025-10": 10, "2025-11": 14, ...}
    counts = {}
    for (first_commit_at,) in con.execute(sql):
        month = first_commit_at[:7]  # "2026-05-17T11:01:44Z" --> "2026-05"
        counts[month] = counts.get(month, 0) + 1

    #3-Dictionary --> key/value DataFrame, oldest month first
    return add_percentage(pd.DataFrame(sorted(counts.items()), columns=["first_skill_month", "count"]))


