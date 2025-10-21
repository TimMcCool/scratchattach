import pprint
import sys
import warnings

def test_user():
    sys.path.insert(0, ".")
    import scratchattach as sa
    from util import session, credentials_available
    if not credentials_available():
        warnings.warn("Skipped test_studio because there were no credentials available.")
        return
    sess = session()

    user = sess.connect_user("faretek1")
    #assert "mochipiyo" in user.unfollower_usernames()

    user = sess.connect_user("ScratchAttachV2")

    assert user.id == 147905216
    assert user.username == "ScratchAttachV2"
    assert user.name == "ScratchAttachV2"
    assert "Literally a 'test'" in user.about_me
    assert "Changes here must be careful" in user.wiwo
    assert user.country == "Germany"
    assert not user.is_new_scratcher()
    assert user.rank() == sa.Rank.SCRATCHER
    assert not user.scratchteam
    assert user.join_date == '2024-12-09T19:58:44.000Z'
    assert user.classroom is None
    assert user.does_exist()

    new_scratcher = sess.connect_user("-NewScratcher-")
    assert new_scratcher.is_new_scratcher()
    assert new_scratcher.rank() == sa.Rank.NEW_SCRATCHER
    assert not new_scratcher.scratchteam

    ceebee = sess.connect_user("ceebee")
    assert not ceebee.is_new_scratcher()
    assert ceebee.scratchteam
    assert ceebee.rank() == sa.Rank.SCRATCH_TEAM

    kaj = sess.connect_user("kaj")
    assert not kaj.does_exist()
    # If you request for a user that never existed using sa.get_user, you will get an error. So we construct a new user
    # here like so:
    assert not sa.User(username="_").does_exist()

    # status, bio
    # If the following is not the case, then a miracle has occurred
    griffpatch = sess.connect_user("griffpatch")
    assert griffpatch.message_count() > 100

    assert user.featured_data() is None
    assert ceebee.featured_data()

    assert griffpatch.follower_count() > 100000
    assert user.following_count() > 5
    assert kaj.followers(limit=1)[0].name == "DarkLava"
    assert kaj.follower_names(limit=1)[0] == "DarkLava"
    assert user.following(offset=user.following_count() - 1, limit=1)[0].name == "TimMcCool"
    assert user.is_following("TimMcCool")
    assert kaj.is_followed_by("DarkLava")
    assert griffpatch.project_count() > 15
    user_studio_count = user.studio_count()
    assert user_studio_count > 0
    assert user.studios_following_count() > 1
    assert user.studios(limit=1, offset=user_studio_count-1)[0].title == "Sample studio"
    user_project_count = user.project_count()
    assert user_project_count > 1
    assert user.projects(limit=1, offset=user_project_count - 2)[0].title == "Sample project #1"
    loves_count = user.loves_count()
    assert loves_count > 0
    assert (user.loves(limit=1, offset=loves_count - 1)[0].title ==
            "⚙️ scratchattach 2.0 ⚙️ Scratch API Wrapper for Python")
    favorites_count = user.favorites_count()
    assert favorites_count > 0
    assert (user.favorites(limit=1, offset=favorites_count - 1)[0].title ==
            "⚙️ scratchattach 2.0 ⚙️ Scratch API Wrapper for Python")
    # toggle commenting
    # viewed projects
    # set pfp, bio, wiwo, set featured, forum_signature
    # post comment, reply comment

    # if this fails, then RIP griffpatch :(
    assert griffpatch.activity()
    assert griffpatch.activity_html()
    # (un)follow, delete comment, report comment,
    comment = user.comments()[0]
    assert int(comment.id) == 387076703
    assert comment.content == "Sample comment"
    # comment by id, message_events, verificator

    status_data = user.ocular_status()
    assert status_data["status"] == "Sample status"
    assert status_data["color"] == "#855cd6"

if __name__ == '__main__':
    test_user()