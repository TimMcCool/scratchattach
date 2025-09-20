import sys
from datetime import datetime, timedelta, timezone


def test_activity():
    sys.path.insert(0, ".")
    import scratchattach as sa
    import util
    sess = util.session()

    messages = sess.messages()
    for msg in messages:
        print(msg)

if __name__ == "__main__":
    test_activity()
