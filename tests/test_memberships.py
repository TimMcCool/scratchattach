import scratchattach as sa
from scratchattach import get_user, is_member, has_ears, has_badge
import warnings

warnings.filterwarnings("ignore", category=sa.UserAuthenticationWarning)


def test_memberships():
    # unfortunately we don't have amazingly robust test-cases here.
    
    # these are subject to change, we need to find long term members for this
    member_users = [
        get_user("-KittyMax-"),
        get_user("scratchteam"),
        get_user("peekir"),
        get_user("StardreamT2"),
    ]
    nomember_users = [
        get_user("scratchattachv2"),
        get_user("GoatyJules"),
        get_user("SkittlesTheBunny"),
        get_user("Boss_1s") # not sure if it works since im banned
    ]

    assert all(getattr(user, "is_member", False) for user in member_users)
    assert all(not getattr(user, "is_member", True) for user in nomember_users)
    
    assert any(getattr(user, "has_ears", False) for user in member_users)
    assert all(not getattr(user, "has_ears", True) for user in nomember_users)

    assert any(user.has_badge() for user in member_users)
    assert all(not user.has_badge() for user in nomember_users)

    # keeping old test in case

    #u1 = sa.get_user("-KittyMax-")
    #assert u1.is_member  # NOTE: This may be wrong! I think it might be supposed to be False here...
    #assert not u1.has_ears
    #assert u1.has_badge()

    #u2 = sa.get_user("scratchteam")
    #assert u2.is_member
    #assert u2.has_ears
    #assert u2.has_badge()

    #u3 = sa.get_user("scratchattachv2")
    #assert not u3.is_member
    #assert not u3.has_ears
    #assert not u3.has_badge()

    #u4 = sa.get_user("peekir")
    #assert u4.is_member
    #assert u4.has_ears
    #assert u4.has_badge()

    #u5 = sa.get_user("StardreamT2")
    #assert u5.is_member
    #assert u5.has_ears
    #assert not u5.has_badge()


if __name__ == "__main__":
    test_memberships()
