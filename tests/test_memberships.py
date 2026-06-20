import warnings
from datetime import datetime
import scratchattach as sa
from util import allow_before

warnings.filterwarnings("ignore", category=sa.UserAuthenticationWarning)


def test_memberships():    
    if allow_before(datetime(2026, 6, 28)):
        return
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

    assert all(user.is_member for user in member_users)
    assert all(not user.is_member for user in nomember_users)
    
    assert any(user.has_ears for user in member_users)
    assert all(not user.has_ears for user in nomember_users)

    assert any(user.has_badge() for user in member_users)
    assert all(not user.has_badge() for user in nomember_users)


if __name__ == "__main__":
    test_memberships()
