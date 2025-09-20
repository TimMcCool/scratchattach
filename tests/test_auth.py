import sys
import os

def test_import():
  sys.path.insert(0, ".")

  assert "FERNET_KEY" in os.environ
  assert len(os.environ["FERNET_KEY"]) == 32
