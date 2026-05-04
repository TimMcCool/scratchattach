import warnings
import util


def test_session():
    if not util.credentials_available():
        warnings.warn("Skipped test_session because there were no credentials available.")
        return
    sess = util.session()
    shared, unshared, studios = sess.mystuff_counts()
    assert shared >= 3
    assert unshared >= 2
    assert studios >= 1

    sess = util.teacher_session()
    if not sess:
        warnings.warn("Skipped test_session (teacher) because there was no teacher account available")
        return

    open_count, closed_count = sess.mystuff_classes_counts()
    assert open_count >= 2
    assert closed_count >= 1


if __name__ == "__main__":
    test_session()
