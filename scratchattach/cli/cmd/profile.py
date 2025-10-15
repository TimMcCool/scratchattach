from scratchattach.cli.context import ctx, console

@ctx.sessionable
def profile():
    console.rule()
    user = ctx.session.connect_linked_user()
    console.print(user)
