import pprint
import sys
import warnings

def test_project():
    sys.path.insert(0, ".")
    import scratchattach as sa
    import util
    if not util.credentials_available():
        warnings.warn("Skipped test_project because there were no credentials available.")
        return
    sess = util.session()


    project = sess.connect_project(104)
    body = project.body()
    body.to_json()  # do nothing with the data, just make sure it works.



if __name__ == '__main__':
    test_project()