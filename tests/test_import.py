import sys
def test_import():
  sys.path.insert(0, ".")
  sys.path.insert(0, "..")
  import scratchattach
test_import()