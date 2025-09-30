import sys
import os
import warnings

def test_auth():
    sys.path.insert(0, ".")
    import util
    if not util.credentials_available():
        warnings.warn("Skipped test_auth because there were no credentials available.")
        return
    sess = util.session()

    assert "FERNET_KEY" in os.environ
    assert len(os.environ["FERNET_KEY"]) == 32
    assert sess.username == "ScratchAttachV2"
