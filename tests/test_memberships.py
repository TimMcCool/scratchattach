import scratchattach as sa
import warnings

warnings.filterwarnings("ignore", category=sa.UserAuthenticationWarning)


def test_memberships():    
    # NOTE: these are subject to change
    member_users = [
        sa.get_user("-KittyMax-"),
        sa.get_user("scratchteam"),
        sa.get_user("peekir"),
        sa.get_user("StardreamT2"),
    ]
    nomember_users = [
        sa.get_user("scratchattachv2"),
        sa.get_user("GoatyJules"),
        sa.get_user("SkittlesTheBunny"),
        sa.get_user("Boss_1s")
    ]

    assert all(getattr(user, "is_member", False) for user in member_users)
    assert all(not getattr(user, "is_member", True) for user in nomember_users)
    
    assert any(getattr(user, "has_ears", False) for user in member_users)
    assert all(not getattr(user, "has_ears", True) for user in nomember_users)

    assert any(user.has_badge() for user in member_users)
    assert all(not user.has_badge() for user in nomember_users)


if __name__ == "__main__":
    test_memberships()
