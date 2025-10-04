from scratchattach.cli import db


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

    print(f"{name}\n"
          f"{description}\n"
          f"{usernames}")
