# v2 ready

from .cloud.cloud import *
from .site.user import *
from .site.session import *
from .site.project import *
from .site.studio import *
from .eventhandlers.cloud_requests import *
from .site.forum import *
from .utils.encoder import *
from .utils import commons
from .site.comment import *
from .eventhandlers.message_events import MessageEvents

def get_news(*, limit=10, offset=0):
    return commons.api_iterative("https://api.scratch.mit.edu/news", limit = limit, offset = offset)
            
def featured_projects():
    return requests.get("https://api.scratch.mit.edu/proxy/featured").json()["community_featured_projects"]

def featured_studios():
    return requests.get("https://api.scratch.mit.edu/proxy/featured").json()["community_featured_studios"]

def top_loved():
    return requests.get("https://api.scratch.mit.edu/proxy/featured").json()["community_most_loved_projects"]

def top_remixed():
    return requests.get("https://api.scratch.mit.edu/proxy/featured").json()["community_most_remixed_projects"]

def newest_projects():
    return requests.get("https://api.scratch.mit.edu/proxy/featured").json()["community_newest_projects"]

def curated_projects():
    return requests.get("https://api.scratch.mit.edu/proxy/featured").json()["curator_top_projects"]

def design_studio_projects():
    return requests.get("https://api.scratch.mit.edu/proxy/featured").json()["scratch_design_studio"]

def search_posts(*, query, order="newest", page=0):
    print("Warning: This method is deprecated because ScratchDB is down indefinitely.")
    try:
        data = requests.get(f"https://scratchdb.lefty.one/v3/forum/search?q={query}&o={order}&page={page}").json()["posts"]
        return_data = []
        for o in data:
            a = forum.ForumPost(id = o["id"])
            a._update_from_dict(o)
            return_data.append(a)
        return return_data
    except Exception:
        return []

def total_site_stats():
    data = requests.get("https://scratch.mit.edu/statistics/data/daily/").json()
    data.pop("_TS")
    return data

def monthly_site_traffic():
    data = requests.get("https://scratch.mit.edu/statistics/data/monthly-ga/").json()
    data.pop("_TS")
    return data

def country_counts():
    return requests.get("https://scratch.mit.edu/statistics/data/monthly/").json()["country_distribution"]

def age_distribution():
    data = requests.get("https://scratch.mit.edu/statistics/data/monthly/").json()["age_distribution_data"][0]["values"]
    return_data = {}
    for value in data:
        return_data[value["x"]] = value["y"]
    return return_data

def get_health():
    return requests.get("https://api.scratch.mit.edu/health").json()

def get_csrf_token():
    """
    Generates a scratchcsrftoken using Scratch's API.

    Returns:
        str: The generated scratchcsrftoken
    """
    return requests.get(
        "https://scratch.mit.edu/csrf_token/"
    ).headers["set-cookie"].split(";")[3][len(" Path=/, scratchcsrftoken="):]