import sys


def test_search():
    sys.path.insert(0, ".")
    import scratchattach as sa
    from util import session
    sess = session()

    print(sess.search_projects())
    print(sess.explore_projects())
    print(sess.search_studios())
    print(sess.explore_studios())

if __name__ == "__main__":
    test_search()
