import pprint
from pathlib import Path
import scratchattach as sa


def test_project():

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


if __name__ == "__main__":
    test_project()
