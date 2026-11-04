import warnings
from util import session, credentials_available, allow_before
import scratchattach as sa
from datetime import datetime
from scratchattach.site.project import Project


def test_project_share_disables_response_json_error_handling(monkeypatch):
    # Regression for #609: a shared response with a non-JSON body must not trip
    # the response checker, so share() should run the PUT with error_handling
    # disabled and restore it afterwards.
    class FakeSession:
        username = "ScratchAttachV2"

        def get_headers(self):
            return {"x-token": "token"}

        def get_cookies(self):
            return {"scratchsessionsid": "session"}

    flag_during = []

    def fake_put(*args, **kwargs):
        flag_during.append(sa.utils.requests.requests.error_handling)

    monkeypatch.setattr(sa.utils.requests.requests, "put", fake_put)
    Project(id=123, author_name="ScratchAttachV2", _session=FakeSession()).share()

    assert flag_during == [False]  # disabled during the PUT
    assert sa.utils.requests.requests.error_handling is True  # restored after


def test_project():
    if not credentials_available():
        warnings.warn("Skipped test_project because there were no credentials available.")
        return
    sess = session()

    # project = sess.connect_project(104)
    # tree = project.remix_tree_pretty()
    # assert len(tree) > 1000 # there is a lot of chars. Just assert that sth is generated

    # unshared project
    project = sess.connect_project(1315253799)
    assert project
    assert project.title == "Unshared with comments"
    assert project.author_name == "ScratchAttachV2"
    assert project.embed_url == "https://scratch.mit.edu/projects/1315253799/embed"
    assert not project.is_shared()
    assert project.author().id == 147905216
    comment = project.comments()[0]
    assert comment.author_name == "faretek"
    assert comment.content == "Second sample comment"
    assert comment.id == 544358507
    reply = comment.replies()[0]
    assert reply.content == "sample reply"
    assert reply.commentee_id == 143593913
    assert reply.author_name == "ScratchAttachV2"

    project = sess.connect_project(1209355136)
    assert project
    assert project.title == "Sample project #1"
    assert project.author_name == "ScratchAttachV2"
    assert project.embed_url == "https://scratch.mit.edu/projects/1209355136/embed"
    assert project.is_shared()
    # create_remix
    # load_description
    # download
    # get_json
    # body
    # raw_json
    # raw_json_or_empty
    # creator_agent
    assert project.author().id == 147905216
    # studios
    # TODO: move this to a separate comment tester
    comment = project.comments()[0]
    # comment_by_id
    # comment_replies
    # comment by id
    # (un)love
    # (un)favorite
    # pos_view
    # set_fields
    # turn on/off/toggle commenting
    # (un)share
    # set thumb
    # delete comment
    # report comment
    # post/reply comment
    # set body/json/upload json from
    # set title/instruction/notes
    # visibility

    assert comment.id == 489648029

    remix = project.remixes()[0]
    assert remix.id == 1209582809
    assert remix.title == "Sample remix"
    assert remix.author_name == "ScratchAttachV2"
    assert remix.embed_url == "https://scratch.mit.edu/projects/1209582809/embed"

    # assert sess.connect_project(414601586).moderation_status() == "notsafe"
    # assert sess.connect_project(1207314193).moderation_status() == "safe"
    # assert sess.connect_project(
    # 1233).moderation_status() == "notreviewed"  # if this becomes reviewed, please update this
    # ^^ also this project is an infinite remix loop!

    assert sa.explore_projects() or allow_before(datetime(2026, 4, 1))
    # ^ Remove when fixed and change datetime next time this fails.
    assert sa.search_projects(query="scratchattach")


if __name__ == "__main__":
    test_project()
