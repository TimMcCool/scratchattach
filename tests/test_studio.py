import sys
from datetime import datetime, timezone
import warnings

def test_studio():
    sys.path.insert(0, ".")
    import scratchattach as sa
    from util import session, credentials_available
    if not credentials_available():
        warnings.warn("Skipped test_studio because there were no credentials available.")
        return
    sess = session()

    studio = sess.connect_studio(34253687)
    assert studio.get_exact_project_count() == 1251

    studio = sess.connect_studio(50809872)

    assert studio.title == "Sample studio"
    assert studio.description == "Sample text"
    assert studio.host_id == 58743127
    assert studio.open_to_all is False
    assert studio.comments_allowed is False
    assert studio.image_url == 'https://cdn2.scratch.mit.edu/get_image/gallery/50809872_170x100.png'
    assert (datetime.fromisoformat(studio.created) ==
            datetime(2025, 8, 26, 15, 3, 5, tzinfo=timezone.utc))
    assert studio.follower_count > 0
    assert 0 < studio.manager_count <= 2
    assert studio.project_count == 2

    # (un)follow

    comment = studio.comments()[0]
    assert comment.content == "Sample"
    assert comment.id == 302129887
    assert comment.author_name == "faretek1"
    assert comment.replies()[0].content == "text"

    # comment replies, comment by id, post comment, delete comment, report comment, set thumb, reply comment
    projs = studio.projects()
    assert len(projs) == 2
    assert projs[0].title == "Sample remix"
    assert projs[1].title == "Sample project #1"

    role = studio.your_role()
    assert role["manager"]
    assert role["following"]

    curator_names = [curator.name for curator in studio.managers()]
    assert "ScratchAttachV2" in curator_names

    assert not studio.curators()

    # invite/promote/remove curators transfer ownership / leave / add project / remove proj

    host = studio.host()
    assert host.name in ("faretek1", "ScratchAttachV2")

    # set fields, desc, title, open projects, close projects, turn on/off/toggle commenting
    assert studio.activity()[0].type == "addprojecttostudio"
    # accept invite/your role

    # If we run out of 'add everything!' studios, clearly something has gone wrong.
    assert sa.search_studios(query="add everything!")
    assert sa.explore_studios(query="*")


if __name__ == '__main__':
    test_studio()
