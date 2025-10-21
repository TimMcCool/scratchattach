import pprint
import sys
from pathlib import Path


def test_project():
    return
    sys.path.insert(0, ".")
    import scratchattach as sa

    path = Path(__file__).parent.parent / "intro for kelmare (yoda tour) (p2).sb3"

    if path.exists():
        print(f"loading cached {path}")
        body = sa.editor.Project.from_sb3(path.open("rb"))
    else:
        print(f"Could not find {path}")
        project = sa.get_project(1074489898)
        body = project.body()

    body.obfuscate()

    # body.save_json("obfuscated")
    body.export("obfuscated.sb3")


if __name__ == '__main__':
    test_project()
