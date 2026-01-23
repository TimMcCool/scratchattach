import scratchattach as sa
import warnings

warnings.filterwarnings("ignore", category=sa.UserAuthenticationWarning)


def test_memberships():
    # unfortunately we don't have amazingly robust test-cases here.
    u1 = sa.get_user("-KittyMax-")
    assert u1.is_member
    assert u1.has_ears
    assert u1.has_badge()

    u2 = sa.get_user("ceebee")
    assert u2.is_member
    assert u2.has_ears
    assert u2.has_badge()

    u3 = sa.get_user("scratchattachv2")
    assert not u3.is_member
    assert not u3.has_ears
    assert not u3.has_badge()

    u4 = sa.get_user("peekir")
    assert u4.is_member
    assert u4.has_ears
    assert u4.has_badge()

    u5 = sa.get_user("StardreamT2")
    assert u5.is_member
    assert u5.has_ears
    assert not u5.has_badge()


if __name__ == "__main__":
    test_memberships()
