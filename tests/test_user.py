import sys
def test_import():
    sys.path.insert(0, ".")
    import scratchattach as sa

    user = sa.get_user("ScratchAttachV2")

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

    new_scratcher = sa.get_user("-NewScratcher-")
    assert new_scratcher.is_new_scratcher()
    assert new_scratcher.rank() == sa.Rank.NEW_SCRATCHER
    assert not new_scratcher.scratchteam

    ceebee = sa.get_user("ceebee")
    assert not ceebee.is_new_scratcher()
    assert ceebee.scratchteam
    assert ceebee.rank() == sa.Rank.SCRATCH_TEAM

    kaj = sa.get_user("kaj")
    assert not kaj.does_exist()
    # If you request for a user that never existed using sa.get_user, you will get an error. So we construct a new user
    # here like so:
    assert not sa.User(username="_").does_exist()

    # status, bio
    # If the following is not the case, then a miracle has occurred
    griffpatch = sa.get_user("griffpatch")
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