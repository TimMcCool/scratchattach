import pprint
import warnings
import util
import scratchattach as sa


def test_project():
    if not util.credentials_available():
        warnings.warn(
            "Skipped test_project because there were no credentials available."
        )
        return
    sess = util.session()

    project = sess.connect_project(104)
    body = project.body()
    body.to_json()  # do nothing with the data, just make sure it works.


if __name__ == "__main__":
    test_project()

