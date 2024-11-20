"""Other Scratch API-related functions"""

import json
import warnings

from ..utils import commons
from ..utils.exceptions import BadRequest
from ..utils.requests import Requests as requests
from ..utils.supportedlangs import Languages


# --- Front page ---

def get_news(*, limit=10, offset=0):
    return commons.api_iterative("https://api.scratch.mit.edu/news", limit=limit, offset=offset)


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
    return requests.post("https://api.scratch.mit.edu/accounts/checkpassword/", json={"password": password}).json()[
        "msg"]


# --- April fools endpoints ---

def aprilfools_get_counter() -> int:
    return requests.get("https://api.scratch.mit.edu/surprise").json()["surprise"]


def aprilfools_increment_counter() -> int:
    return requests.post("https://api.scratch.mit.edu/surprise").json()["surprise"]


# --- Resources ---
def get_resource_urls():
    return requests.get("https://resources.scratch.mit.edu/localized-urls.json").json()


# --- Misc ---
# I'm not sure what to label this as
def scratch_team_members() -> dict:
    # Unfortunately, the only place to find this is a js file, not a json file, which is annoying
    text = requests.get("https://scratch.mit.edu/js/credits.bundle.js").text
    text = "[{\"userName\"" + text.split("JSON.parse('[{\"userName\"")[1]
    text = text.split("\"}]')")[0] + "\"}]"

    return json.loads(text)


def translate(language: str | Languages, text: str = "hello"):
    lang = language
    if isinstance(language, str):
        if language.lower() in Languages.all_of("code", str.lower):
            lang = Languages.find(language.lower(), "code", apply_func=str.lower)

        elif language.lower() in Languages.all_of("name", str.lower):
            lang = Languages.find(language.lower(), apply_func=str.lower)

    elif isinstance(language, Languages):
        lang = language.value
    else:
        # The code will work so long as the language has a 'code' attribute, however, this is bad practice.
        warnings.warn(f"{language} is not {str} or {Languages}, but {type(language)}.")

    if lang is None:
        raise ValueError(f"{language} is not a supported translate language")

    print(lang.__dict__)
    response_json = requests.get(
        f"https://translate-service.scratch.mit.edu/translate?language={lang.code}&text={text}").json()

    if "result" in response_json:
        return response_json["result"]
    else:
        raise BadRequest(f"Language '{language}' does not seem to be valid.\nResponse: {response_json}")


def text2speech(text: str = "hello", gender: str = "female", language: str = "en-US"):
    """
    Sends a request to Scratch's TTS synthesis service.
    Returns:
        - The TTS audio (mp3) as bytes
        - The playback rate (e.g. for giant it would be 0.84)
    """
    if gender == "female" or gender == "alto":
        gender = ("female", 1)
    elif gender == "male" or gender == "tenor":
        gender = ("male", 1)
    elif gender == "squeak":
        gender = ("female", 1.19)
    elif gender == "giant":
        gender = ("male", .84)
    elif gender == "kitten":
        gender = ("female", 1.41)
        split = text.split(' ')
        text = ''
        for token in split:
            if token.strip() != '':
                text += "meow "
    else:
        gender = ("female", 1)

    og_lang = language
    if isinstance(language, Languages):
        language = language.value.tts_locale

    if language is None:
        raise ValueError(f"Language '{og_lang}' is not a supported tts language")

    if language.lower() not in Languages.all_of("tts_locale", str.lower):
        if language.lower() in Languages.all_of("name", str.lower):
            language = Languages.find(language.lower(), apply_func=str.lower).tts_locale

    lang = Languages.find(language, "tts_locale")
    if lang is None or language is None:
        raise ValueError(f"Language '{og_lang}' is not a supported tts language")

    response = requests.get(f"https://synthesis-service.scratch.mit.edu/synth"
                            f"?locale={lang.tts_locale}&gender={gender[0]}&text={text}")
    return response.content, gender[1]
