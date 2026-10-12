import sqlite3
from pathlib import Path

import pandas as pd

from HelperFunctions.HelperFunctions_Adoption.Adoption import SKILL_FILE


DB_PATH = Path(__file__).parent.parent.parent / "SQL_Lite_Source" / "agent_skills_sample.db"
con = sqlite3.connect(DB_PATH)

# Representatives: the one file per distinct content that was enriched (text, front matter, folder)
REPRESENTATIVE = "dedup_primary = 1"

# Copy buckets: (label, lowest number of files sharing one content), smallest first
COPY_BUCKETS = [("1", 1), ("2", 2), ("3-5", 3), ("6-10", 6), ("11-50", 11), ("51+", 51)]

# location_class values --> readable labels ("canonical" is the dataset's name for Claude Code's own skill folder)
LOCATION_LABELS = {"canonical": ".claude/skills", "skills-dir": "other skills folder", "other": "no skills folder"}

# frontmatter_valid values --> readable labels
FRONTMATTER_LABELS = {1: "valid", 0: "invalid", None: "Unknown"}


'''
Adds a percentage column: each count as a % of all files (rounded to 2 decimals)
'''
def add_percentage(df):
    df["percentage"] = (df["count"] / df["count"].sum() * 100).round(2)
    return df


'''
Counts files per value of one column into a dictionary --> {"SKILL.md": 29408, "skill.md": 349, ...}
where: optional SQL filter on artifacts
'''
def value_counts(col, where=None):
    sql = f'SELECT "{col}" FROM artifacts'
    if where:
        sql += f" WHERE {where}"
    counts = {}
    for (value,) in con.execute(sql):
        counts[value] = counts.get(value, 0) + 1
    return counts


'''
Inclusion set - Count files per exact basename (SKILL.md vs case variants)
'''
def filename_counts():
    #1-Count every file by its exact basename --> {"SKILL.md": 29408, "skill.md": 349, ...}
    counts = value_counts("filename")

    #2-Dictionary --> key/value DataFrame, most common first
    return add_percentage(pd.DataFrame(counts.items(), columns=["filename", "count"]).sort_values(
        "count", ascending=False, ignore_index=True
    ))


'''
RQ 2a - Count files per location class (.claude/skills / other skills folder / no skills folder)
'''
def location_class_counts():
    #1-Count every file by where it sits in the repo --> {"skills-dir": 14882, "other": 12539, ...}
    counts = value_counts("location_class")

    #2-Raw class --> readable label ("canonical" --> ".claude/skills")
    counts = {LOCATION_LABELS.get(location, location): n for location, n in counts.items()}

    #3-Dictionary --> key/value DataFrame, most common first
    return add_percentage(pd.DataFrame(counts.items(), columns=["location_class", "count"]).sort_values(
        "count", ascending=False, ignore_index=True
    ))


'''
Inclusion set - Count representatives per front-matter validity
Only representatives were parsed, so copies are left out
'''
def frontmatter_counts():
    #1-Count every representative by its front-matter flag --> {1: 11305, 0: 1711}
    counts = value_counts("frontmatter_valid", REPRESENTATIVE)

    #2-Flag --> label, kept in label order so empty labels still show
    rows = [(label, counts.get(flag, 0)) for flag, label in FRONTMATTER_LABELS.items()]
    return add_percentage(pd.DataFrame(rows, columns=["frontmatter", "count"]))


'''
Inclusion set - Count files kept or dropped by the SKILL_FILE rule, split by exact basename
unknown: look-alike copies outside a skills folder whose front matter was never parsed, so the rule cannot judge them
(a WHERE on SKILL_FILE leaves these out, same as dropped)
'''
def skill_file_counts():
    #1-Count every file by (basename, passes the rule) --> {("skill.md", 1): 138, ("skill.md", 0): 117, ("skill.md", None): 94, ...}
    sql = f"SELECT filename, {SKILL_FILE} FROM artifacts"
    counts = {}
    for filename, kept in con.execute(sql):
        counts[(filename, kept)] = counts.get((filename, kept), 0) + 1

    #2-Dictionary --> one row per basename with kept / dropped / unknown columns, most common first
    filenames = sorted({filename for filename, _ in counts}, key=lambda f: -sum(n for (name, _), n in counts.items() if name == f))
    rows = [(f, counts.get((f, 1), 0), counts.get((f, 0), 0), counts.get((f, None), 0)) for f in filenames]
    return pd.DataFrame(rows, columns=["filename", "kept", "dropped", "unknown"])


'''
RQ 3a - Count distinct contents per copy bucket (how many files share the same file_sha)
files: how many files those contents add up to, so the share of all files held by each bucket shows
Copies outside the sample are not seen, so reuse is understated
'''
def copy_counts():
    #1-Start every bucket at 0 so empty buckets still show --> {"1": [0, 0], "2": [0, 0], ...} as [contents, files]
    counts = {label: [0, 0] for label, _ in COPY_BUCKETS}

    #2-Put each content in the highest bucket its number of files reaches
    for (copies,) in con.execute("SELECT COUNT(*) FROM artifacts GROUP BY file_sha"):
        label = next(label for label, low in reversed(COPY_BUCKETS) if copies >= low)
        counts[label][0] += 1
        counts[label][1] += copies

    #3-Dictionary --> DataFrame, kept in bucket order
    df = add_percentage(pd.DataFrame([(label, n, files) for label, (n, files) in counts.items()], columns=["copies", "count", "files"]))
    df["files_percentage"] = (df["files"] / df["files"].sum() * 100).round(2)
    return df[["copies", "count", "percentage", "files", "files_percentage"]]


'''
RQ 3a - The most copied contents: skill name, number of files and repos holding it, and where the representative sits
'''
def top_copied(n=10):
    #1-Count files and repos per content, most copied first
    sql = f"""
        SELECT file_sha, COUNT(*) AS files, COUNT(DISTINCT repo_full_name) AS repos
        FROM artifacts GROUP BY file_sha ORDER BY files DESC, file_sha LIMIT {int(n)}
    """
    rows = []
    for file_sha, files, repos in con.execute(sql).fetchall():
        #2-Name and location come from the representative, the only copy that was parsed
        name, repo, path = con.execute(
            f"SELECT name, repo_full_name, path FROM artifacts WHERE file_sha = ? AND {REPRESENTATIVE}", (file_sha,)
        ).fetchone()
        rows.append((name, files, repos, repo, path))

    return pd.DataFrame(rows, columns=["name", "files", "repos", "representative_repo", "representative_path"])
