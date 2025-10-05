from scratchattach.cli import db
from scratchattach.cli.context import console, format_esc, ctx

from rich.console import escape
from rich.table import Table

def _list():
    table = Table(title="All groups")
    table.add_column("Name")
    table.add_column("Description")
    table.add_column("Usernames")

    db.cursor.execute("SELECT NAME, DESCRIPTION FROM GROUPS")
    for name, description in db.cursor.fetchall():
        db.cursor.execute("SELECT USERNAME FROM GROUP_USERS WHERE GROUP_NAME=?", (name,))
        usernames = db.cursor.fetchall()

        table.add_row(escape(name), escape(description),
                      '\n'.join(f"{i}. {u}" for i, (u,) in enumerate(usernames)))

    console.print(table)

def group():
    match ctx.args.group_command:
        case "list":
            _list()
            return

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
