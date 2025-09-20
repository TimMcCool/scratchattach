import sys
from datetime import datetime, timedelta, timezone



def test_teacher_activity():
    sys.path.insert(0, ".")
    import scratchattach as sa
    from scratchattach.utils import exceptions
    import util
    sess = util.teacher_session()

    # we cannot do assertions, but we can probe for any errors.
    messages = sess.mystuff_classes()[0].activity()
    for msg in messages:
        print(msg, end=' ')

        try:
            target = msg.target()
        except exceptions.CommentNotFound:
            target = None

        print(target)


if __name__ == "__main__":
    test_teacher_activity()
