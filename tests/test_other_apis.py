import pprint
import sys
from datetime import datetime, timedelta, timezone
import warnings


def test_activity():
    sys.path.insert(0, ".")
    import scratchattach as sa
    from scratchattach.utils import exceptions
    import util

    news = sa.get_news()
    found_wiki_wednesday = False
    for newsitem in news:
        if newsitem["headline"] == "Wiki Wednesday!":
            found_wiki_wednesday = True
    if not found_wiki_wednesday:
        warnings.warn(f"Did not find wiki wednesday! News dict: {news}")

    featured_projects = sa.featured_projects()
    featured_studios = sa.featured_studios()
    top_loved = sa.top_loved()
    top_remixed = sa.top_remixed()
    newest_projects = sa.newest_projects()
    curated_projects = sa.curated_projects()
    design_studio_projects = sa.design_studio_projects()

    def test_featured_data(name, data: list[dict[str, str | int]]):
        if not data:
            warnings.warn(f"Did not find {name}! {data}")

    test_featured_data("featured featured_projects", featured_projects)
    test_featured_data("featured featured_studios", featured_studios)
    test_featured_data("featured top_loved", top_loved)
    test_featured_data("featured top_remixed", top_remixed)
    test_featured_data("featured newest_projects", newest_projects)
    test_featured_data("featured curated_projects", curated_projects)
    test_featured_data("featured design_studio_projects", design_studio_projects)

    stats = sa.total_site_stats()
    assert stats["PROJECT_COUNT"] >= 164307034
    assert stats["USER_COUNT"] >= 135078559
    assert stats["STUDIO_COMMENT_COUNT"] >= 259801679
    assert stats["PROFILE_COMMENT_COUNT"] >= 330786513
    assert stats["STUDIO_COUNT"] >= 34866300
    assert stats["COMMENT_COUNT"] >= 989937824
    assert stats["PROJECT_COMMENT_COUNT"] >= 399349632

    site_traffic = sa.monthly_site_traffic()
    assert int(site_traffic["pageviews"]) > 10000
    assert int(site_traffic["users"]) > 10000
    assert int(site_traffic["sessions"]) > 10000

    country_counts = sa.country_counts()
    for name, count in country_counts.items():
        assert count > 0, f"country_counts[{name!r}] = {count}"


if __name__ == "__main__":
    test_activity()
