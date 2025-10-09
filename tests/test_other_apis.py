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

    print(sa.total_site_stats())

if __name__ == "__main__":
    test_activity()
