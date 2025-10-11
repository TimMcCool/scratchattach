"""
Basic connections to the scratch.sqlite file
"""
import sqlite3
import sys
import os

from pathlib import Path

from typing_extensions import LiteralString


def _gen_appdata_folder() -> Path:
    name = "scratchattach"
    match sys.platform:
        case "win32":
            return Path(os.getenv('APPDATA')) / name
        case "linux":
            return Path.home() / f".{name}"
        case plat:
            raise NotImplementedError(f"No 'appdata' folder implemented for {plat}")

_path = _gen_appdata_folder()
_path.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(_path / "cli.sqlite")
cursor = conn.cursor()

# Init any tables
def add_col(table: LiteralString, column: LiteralString, _type: LiteralString):
    try:
        # strangely, using `?` here doesn't seem to work. Make sure to use LiteralStrings, not str
        return cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {_type}")
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e).lower():
            raise

# NOTE: IF YOU WANT TO ADD EXTRA KEYS TO A TABLE RETROACTIVELY, USE add_col
# note: avoide using select * with tuple unpacking/indexing, because if fields are added, things will break.
conn.execute("BEGIN")
cursor.executescript("""
    CREATE TABLE IF NOT EXISTS SESSIONS (
        ID TEXT NOT NULL,
        USERNAME TEXT NOT NULL PRIMARY KEY
    );
        
    CREATE TABLE IF NOT EXISTS GROUPS (
        NAME TEXT NOT NULL PRIMARY KEY,
        DESCRIPTION TEXT
        -- If you want to add users to a group, you add to the next table
    );
    
    CREATE TABLE IF NOT EXISTS GROUP_USERS (
        GROUP_NAME TEXT NOT NULL,
        USERNAME TEXT NOT NULL
    );
    
    -- stores info like current group, last project/studio, etc
    CREATE TABLE IF NOT EXISTS CURRENT (
        GROUP_NAME TEXT NOT NULL
    );
""")
add_col("SESSIONS", "PASSWORD", "TEXT")


conn.commit()
