"""
Basic connections to the scratch.sqlite file
"""
import sqlite3
import sys
import os

from pathlib import Path

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
conn.execute("BEGIN")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS SESSIONS (
        ID TEXT NOT NULL,
        USERNAME TEXT NOT NULL PRIMARY KEY,
        PASSWORD TEXT NOT NULL -- TODO: consider if this is needed
    )
""")
conn.commit()
