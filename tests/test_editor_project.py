import sys


def test_import():
    sys.path.insert(0, ".")
    import scratchattach as sa

    proj = sa.get_project(104)
    body = proj.body()
