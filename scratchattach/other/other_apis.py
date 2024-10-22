"""Other Scratch API-related functions"""

from ..utils import commons
from ..utils.requests import Requests as requests

# --- Front page ---

def get_news(*, limit=10, offset=0):
    return commons.api_iterative("https://api.scratch.mit.edu/news", limit = limit, offset = offset)

def featured_data():
    return requests.get("https://api.scratch.mit.edu/proxy/featured").json()

def featured_projects():
    return featured_data()["community_featured_projects"]

def featured_studios():
    return featured_data()["community_featured_studios"]

def top_loved():
    return featured_data()["community_most_loved_projects"]

def top_remixed():
    return featured_data()["community_most_remixed_projects"]

def newest_projects():
    return featured_data()["community_newest_projects"]

def curated_projects():
    return featured_data()["curator_top_projects"]

def design_studio_projects():
    return featured_data()["scratch_design_studio"]

# --- Statistics ---

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

def monthly_comment_activity():
    return requests.get("https://scratch.mit.edu/statistics/data/monthly/").json()["comment_data"]

def monthly_project_shares():
    return requests.get("https://scratch.mit.edu/statistics/data/monthly/").json()["project_data"]

def monthly_active_users():
    return requests.get("https://scratch.mit.edu/statistics/data/monthly/").json()["active_user_data"]

def monthly_activity_trends():
    return requests.get("https://scratch.mit.edu/statistics/data/monthly/").json()["activity_data"]

# --- CSRF Token Generation API ---

def get_csrf_token():
    """
    Generates a scratchcsrftoken using Scratch's API.

    Returns:
        str: The generated scratchcsrftoken
    """
    return requests.get(
        "https://scratch.mit.edu/csrf_token/"
    ).headers["set-cookie"].split(";")[3][len(" Path=/, scratchcsrftoken="):]

# --- Various other api.scratch.mit.edu API endpoints ---

def get_health():
    return requests.get("https://api.scratch.mit.edu/health").json()

def get_total_project_count() -> int:
    return requests.get("https://api.scratch.mit.edu/projects/count/all").json()["count"]

def check_username(username):
    return requests.get(f"https://api.scratch.mit.edu/accounts/checkusername/{username}").json()["msg"]

def check_password(password):
    return requests.post("https://api.scratch.mit.edu/accounts/checkpassword/", json={"password":password}).json()["msg"]

# --- April fools endpoints ---

def aprilfools_get_counter() -> int:
    return requests.get("https://api.scratch.mit.edu/surprise")["surprise"]

def aprilfools_increment_counter() -> int:
    return requests.post("https://api.scratch.mit.edu/surprise")["surprise"]