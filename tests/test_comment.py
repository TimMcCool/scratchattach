from datetime import datetime, timedelta, timezone
import warnings
import scratchattach as sa
import util


def test_comment():
    if not util.credentials_available():
        warnings.warn(
            "Skipped test_comment because there were no credentials available."
        )
        return
    sess = util.session()

    user = sess.connect_linked_user()
    proj = sess.connect_project(1108326850)
    studio = sess.connect_studio(50809872)

    comment = user.comments(limit=1)[0]

    assert comment.id == "387076703"
    assert comment.source == sa.CommentSource.USER_PROFILE
    assert comment.source_id == "ScratchAttachV2"
    assert comment.parent_id is None
    assert comment.content == "Sample comment"
    assert datetime.fromisoformat(comment.datetime_created) - datetime(
        2025, 8, 25, tzinfo=timezone.utc
    ) < timedelta(days=1)
    assert comment.reply_count == 0
    assert comment.text == "Sample comment"

    comment = proj.comments(limit=1)[0]

    assert comment.id == 494890468
    assert comment.source == sa.CommentSource.PROJECT
    assert comment.source_id == 1108326850
    assert comment.parent_id is None
    assert comment.content == ("&lt;&amp;;&apos;!\n" "newline\n" "testing escaping")
    assert datetime.fromisoformat(comment.datetime_created) - datetime(
        2025, 9, 20, tzinfo=timezone.utc
    ) < timedelta(days=1)
    assert comment.reply_count == 0
    assert comment.text == ("<&;'!\n" "newline\n" "testing escaping")

    comment = studio.comments(limit=1)[0]

    assert comment.id == 302129887
    assert comment.source == sa.CommentSource.STUDIO
    assert comment.source_id == 50809872
    assert comment.parent_id is None
    assert comment.content == "Sample"
    assert datetime.fromisoformat(comment.datetime_created) - datetime(
        2025, 8, 26, tzinfo=timezone.utc
    ) < timedelta(days=1)
    assert comment.reply_count == 1
    assert not comment.written_by_scratchteam
    assert comment.text == "Sample"

    comment = comment.replies(limit=1)[0]

    assert comment.id == 302129910
    assert comment.source == sa.CommentSource.STUDIO
    assert comment.source_id == 50809872
    assert comment.parent_id == 302129887
    assert comment.commentee_id == 58743127
    assert comment.content == "text"
    assert datetime.fromisoformat(comment.datetime_created) - datetime(
        2025, 8, 26, tzinfo=timezone.utc
    ) < timedelta(days=1)
    assert comment.reply_count == 0
    assert not comment.written_by_scratchteam
    assert comment.text == "text"


if __name__ == "__main__":
    test_comment()
