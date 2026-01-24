from datetime import datetime, timedelta, timezone
import scratchattach as sa
from scratchattach.utils import exceptions
import util


def test_teacher_activity():
    if not (sess := util.teacher_session()):
        return

    # we cannot do assertions, but we can probe for any errors.
    cls = sess.mystuff_classes()[0]

    messages = [cls.activity(page=page) for page in range(1, 3)]
    for page in messages:
        for msg in page:
            _ = str(msg)

            try:
                target = msg.target()
            except exceptions.CommentNotFound:
                target = None

            _ = target


if __name__ == "__main__":
    test_teacher_activity()
