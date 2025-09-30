import sys
from datetime import datetime, timedelta, timezone
import warnings



def test_activity():
    sys.path.insert(0, ".")
    import scratchattach as sa
    from scratchattach.utils import exceptions
    import util
    if not util.credentials_available():
        warnings.warn("Skipped test_activity because there were no credentials available.")
        return
    sess = util.session()

    # we cannot do assertions, but we can probe for any errors.
    messages = sess.messages()
    for msg in messages:
        print(msg, end=' ')

        try:
            target = msg.target()
        except exceptions.CommentNotFound:
            target = None
            raise

        print(target)


if __name__ == "__main__":
    test_activity()
