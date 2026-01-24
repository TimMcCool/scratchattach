import warnings
import scratchattach as sa
from util import session, credentials_available


def test_search():
    if not credentials_available():
        warnings.warn(
            "Skipped test_search because there were no credentials available."
        )
        return
    sess = session()

    print(sess.search_projects())
    print(sess.explore_projects())
    print(sess.search_studios())
    print(sess.explore_studios())


if __name__ == "__main__":
    test_search()
