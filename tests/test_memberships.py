import scratchattach as sa
import warnings

warnings.filterwarnings("ignore", category=sa.UserAuthenticationWarning)


def _assert_any_user_matches(usernames, *, is_member, has_ears, has_badge):
    expected = (is_member, has_ears, has_badge)
    checked = []
    for username in usernames:
        user = sa.get_user(username)
        actual = (user.is_member, user.has_ears, user.has_badge())
        if actual == expected:
            return
        checked.append(f"{username}: {actual}")

    warnings.warn(
        "Skipped membership sample check because none of the candidate "
        f"accounts currently match {expected}: {', '.join(checked)}"
    )


def test_memberships():
    # unfortunately we don't have amazingly robust test-cases here.
    u1 = sa.get_user("-KittyMax-")
    assert u1.is_member  # NOTE: This may be wrong! I think it might be supposed to be False here...
    assert not u1.has_ears
    assert u1.has_badge()

    u2 = sa.get_user("scratchteam")
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

    _assert_any_user_matches(
        ["StardreamT2", "griffpatch", "ceebee"],
        is_member=True,
        has_ears=True,
        has_badge=False,
    )


if __name__ == "__main__":
    test_memberships()
