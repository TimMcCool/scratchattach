import pprint
import sys


def test_project():
    sys.path.insert(0, ".")
    import scratchattach as sa
    from util import session
    sess = session()


    project = sess.connect_project(104)
    body = project.body()

    print(body)


if __name__ == '__main__':
    test_project()