import re
import sqlite3
from collections import Counter
from pathlib import Path
import pandas as pd


pd.set_option("display.max_colwidth", None)

# Get Path 
DB_PATH = Path(__file__).parent.parent.parent / "SQL_Lite_Source" / "agent_skills_sample.db"

#Connects to Database
con = sqlite3.connect(DB_PATH)

# Shapes a text value can have (first full match wins)
TEXT_TYPES = {
    "empty": r"",
    "timestamp": r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})",
    "sha1": r"[0-9a-f]{40}",
    "hash16": r"[0-9a-f]{16}",
    "number": r"-?\d+(\.\d+)?",
    "bot": r".+\[bot\]",
    "path": r"[^\s:]*/[^\s:]*",
    "filename": r"[^\s/:]+\.[A-Za-z]\w*",
}


def value_type(v):
    if v is None:
        return "null"
    if not isinstance(v, str):
        return type(v).__name__
    if "\n" in v:
        return "multiline"
    return next((t for t, rx in TEXT_TYPES.items() if re.fullmatch(rx, v)), "text")

'''
Query Database For all rows 
'''
def column_types(table, col):
    #1-Query Database for each collumn, Read every row
    counts = Counter(value_type(v) for (v,) in con.execute(f'SELECT "{col}" FROM "{table}"'))\
    
    #2-Turns Count into a readable String : EX --> "int (11,804), null (37)"
    return ", ".join(f"{t} ({n:,})" for t, n in counts.most_common())

'''
Structure Pandas Tables for the Queried stuff for Visualization 
'''
def table_types(table):
    return pd.DataFrame(
        {"column": col, "types found": column_types(table, col)}
        for _, col, *_ in con.execute(f'PRAGMA table_info("{table}")')
    )
