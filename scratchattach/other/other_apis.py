"""Other Scratch API-related functions"""

from ..utils import commons
from ..utils.requests import Requests as requests
import json

# --- Front page ---

def get_news(*, limit=10, offset=0) -> list:
    return commons.api_iterative("https://api.scratch.mit.edu/news", limit = limit, offset = offset)

def featured_data() -> dict[str,list[dict]]:
    return requests.get("https://api.scratch.mit.edu/proxy/featured").json()

def featured_projects() -> list[dict]:
    return featured_data()["community_featured_projects"]

def featured_studios() -> list[dict]:
    return featured_data()["community_featured_studios"]

def top_loved() -> list[dict]:
    return featured_data()["community_most_loved_projects"]

def top_remixed() -> list[dict]:
    return featured_data()["community_most_remixed_projects"]

def newest_projects() -> list[dict]:
    return featured_data()["community_newest_projects"]

def curated_projects() -> list[dict]:
    return featured_data()["curator_top_projects"]

def design_studio_projects() -> list[dict]:
    return featured_data()["scratch_design_studio"]

# --- Statistics ---

def _maping(data) -> dict[int,int]:
    return_data = {}
    for value in data:
        return_data[value["x"]] = value["y"]
    return return_data

def total_site_stats() -> dict:
    data = requests.get("https://scratch.mit.edu/statistics/data/daily/").json()
    data.pop("_TS")
    return data

def monthly_site_traffic() -> dict:
    data = requests.get("https://scratch.mit.edu/statistics/data/monthly-ga/").json()
    data.pop("_TS")
    return data

def country_counts() -> dict[str,int]:
    return requests.get("https://scratch.mit.edu/statistics/data/monthly/").json()["country_distribution"]

def age_distribution() -> dict[int,int]:
    data = requests.get("https://scratch.mit.edu/statistics/data/monthly/").json()["age_distribution_data"][0]["values"]
    return _maping(data)

def monthly_comment_activity() -> dict[str,dict[int,int]]:
    data = requests.get("https://scratch.mit.edu/statistics/data/monthly/").json()["comment_data"]
    return_data = {}
    return_data[data[0]["key"]] = _maping(data[0]["values"]) #project - "Project Comments"
    return_data[data[1]["key"]] = _maping(data[1]["values"]) #studio - "Studio Comments"
    return_data[data[2]["key"]] = _maping(data[2]["values"]) #user - "Profile Comments"
    return return_data

def monthly_project_shares() -> dict[str,dict[int,int]]:
    data =  requests.get("https://scratch.mit.edu/statistics/data/monthly/").json()["project_data"]
    return_data = {}
    return_data[data[0]["key"]] = _maping(data[0]["values"]) #project - "New Projects"
    return_data[data[1]["key"]] = _maping(data[1]["values"]) #remix - "Remix Projects"
    return return_data


def monthly_active_users() -> dict[str,dict[int,int]]:
    data = requests.get("https://scratch.mit.edu/statistics/data/monthly/").json()["active_user_data"]
    return_data = {}
    return_data[data[0]["key"]] = _maping(data[0]["values"]) #project - "Project Creators"
    return_data[data[1]["key"]] = _maping(data[1]["values"]) #comment - "Comment Creators"
    return return_data

def monthly_activity_trends() -> dict[str,dict[int,int]]:
    data = requests.get("https://scratch.mit.edu/statistics/data/monthly/").json()["activity_data"]
    return_data = {}
    return_data[data[0]["key"]] = _maping(data[0]["values"]) #project - "New Projects"
    return_data[data[1]["key"]] = _maping(data[1]["values"]) #user - "New Users"
    return_data[data[2]["key"]] = _maping(data[2]["values"]) #comment - "New Comments"
    return return_data

# --- CSRF Token Generation API ---

def get_csrf_token() -> str:
    """
    Generates a scratchcsrftoken using Scratch's API.

    Returns:
        str: The generated scratchcsrftoken
    """
    return requests.get(
        "https://scratch.mit.edu/csrf_token/"
    ).headers["set-cookie"].split(";")[3][len(" Path=/, scratchcsrftoken="):]

# --- Various other api.scratch.mit.edu API endpoints ---

def get_health() -> dict:
    return requests.get("https://api.scratch.mit.edu/health").json()

def get_total_project_count() -> int:
    return requests.get("https://api.scratch.mit.edu/projects/count/all").json()["count"]

def check_username(username) -> bool:
    return requests.get(f"https://api.scratch.mit.edu/accounts/checkusername/{username}").json()["msg"] == "valid username"

def check_password(password) -> bool:
    return requests.post("https://api.scratch.mit.edu/accounts/checkpassword/", json={"password":password}).json()["msg"] == "valid password"

# --- April fools endpoints ---

def aprilfools_get_counter() -> int:
    return requests.get("https://api.scratch.mit.edu/surprise").json()["surprise"]

def aprilfools_increment_counter() -> int:
    return requests.post("https://api.scratch.mit.edu/surprise").json()["surprise"]

# --- Resources ---
def get_resource_urls() -> dict:
    return requests.get("https://resources.scratch.mit.edu/localized-urls.json").json()

# --- Misc ---
# I'm not sure what to label this as
def scratch_team_members() -> dict:
    # Unfortunately, the only place to find this is a js file, not a json file, which is annoying
    text = requests.get("https://scratch.mit.edu/js/credits.bundle.js").text
    text = "[{\"userName\"" + text.split("JSON.parse('[{\"userName\"")[1]
    text = text.split("\"}]')")[0] + "\"}]"

    return json.loads(text)
