import warnings
import util


def test_session():
    if not util.credentials_available():
        warnings.warn("Skipped test_auth because there were no credentials available.")
        return
    sess = util.session()
    shared, unshared, studios = sess.mystuff_counts()
    assert shared >= 3
    assert unshared >= 2
    assert studios >= 1


if __name__ == "__main__":
    test_session()
