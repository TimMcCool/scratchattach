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

def new():
    console.rule(f"New group {escape(ctx.args.group_name)}")
    if ctx.db_group_exists(ctx.args.group_name):
        raise ValueError(f"Group {escape(ctx.args.group_name)} already exists")

    db.conn.execute("BEGIN")
    db.cursor.execute("INSERT INTO GROUPS (NAME, DESCRIPTION) "
                      "VALUES (?, ?)", (ctx.args.group_name, input("Description: ")))
    db.conn.commit()
    accounts = input("Add accounts (split by space): ").split()
    for account in accounts:
        ctx.db_add_to_group(ctx.args.group_name, account)

    _group(ctx.args.group_name)

def _group(group_name: str):
    """
    Display information about a group
    """
    db.cursor.execute(
        "SELECT NAME, DESCRIPTION FROM GROUPS WHERE NAME = ?", (group_name,))
    result = db.cursor.fetchone()
    if result is None:
        print("No group selected!!")
        return

    name, description = result

    db.cursor.execute("SELECT USERNAME FROM GROUP_USERS WHERE GROUP_NAME = ?", (name,))
    usernames = [name for (name,) in db.cursor.fetchall()]

    table = Table(title=escape(group_name))
    table.add_column(escape(name))
    table.add_column('Usernames')

    table.add_row(escape(description),
                  '\n'.join(f"{i}. {u}" for i, u in enumerate(usernames)))

    console.print(table)

def switch():
    console.rule(f"Switching to {escape(ctx.args.group_name)}")
    if not ctx.db_group_exists(ctx.args.group_name):
        raise ValueError(f"Group {escape(ctx.args.group_name)} does not exist")

    ctx.current_group_name = ctx.args.group_name
    _group(ctx.current_group_name)

def group():
    match ctx.args.group_command:
        case "list":
            _list()
        case "new":
            new()
        case "switch":
            switch()
        case None:
            _group(ctx.current_group_name)
