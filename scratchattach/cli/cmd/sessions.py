from scratchattach.cli.context import ctx, console

@ctx.sessionable
def sessions():
    console.print(ctx.session)
