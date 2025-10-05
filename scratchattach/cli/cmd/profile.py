from scratchattach.cli.context import ctx, console

@ctx.sessionable
def profile():
    user = ctx.session.connect_linked_user()
    console.print(user)
