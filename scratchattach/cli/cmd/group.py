from scratchattach.cli import db
from scratchattach.cli.context import console, format_esc

from rich.console import escape
from rich.table import Table

def group():
    db.cursor.execute(
        "SELECT NAME, DESCRIPTION FROM GROUPS WHERE NAME IN (SELECT * FROM CURRENT WHERE GROUP_NAME IS NOT NULL)")
    result = db.cursor.fetchone()
    if result is None:
        print("No group selected!!")
        return

    name, description = result

    db.cursor.execute("SELECT USERNAME FROM GROUP_USERS WHERE GROUP_NAME = ?", (name,))
    usernames = [name for (name,) in db.cursor.fetchall()]

    table = Table(title="Current Group")
    table.add_column(escape(name))
    table.add_column('Usernames')

    table.add_row(escape(description),
                  '\n'.join(f"{i}. {u}" for i, u in enumerate(usernames)))

    console.print(table)
