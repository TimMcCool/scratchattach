import sys

def test_import():
  sys.path.insert(0, ".")
  from scratchattach import editor
  proj = editor.Project.from_id(104)
