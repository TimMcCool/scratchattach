import scratchattach as sa


def test_editor_project():
    proj = sa.get_project(104)
    body = proj.body()
