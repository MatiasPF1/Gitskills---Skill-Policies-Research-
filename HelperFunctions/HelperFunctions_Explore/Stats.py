import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = Path(__file__).parent.parent.parent / "SQL_Lite_Source" / "agent_skills_sample.db"
con = sqlite3.connect(DB_PATH)

NUMERIC_TYPES = ("INTEGER", "REAL", "FLOAT", "DOUBLE", "NUMERIC")


def column_stats(table, col):
    s = pd.read_sql(f'SELECT "{col}" FROM "{table}"', con)[col].convert_dtypes()
    return {
        "column": col,
        "count": int(s.count()),
        "nulls": int(s.isna().sum()),
        "min": s.min().item(),
        "max": s.max().item(),
        "median": float(s.median()),
        "average": round(float(s.mean()), 2),
    }


def table_stats(table):
    cols = [col for _, col, decl, *_ in con.execute(f'PRAGMA table_info("{table}")') if decl.upper() in NUMERIC_TYPES]
    return pd.DataFrame(column_stats(table, col) for col in cols)
