"""Other Scratch API-related functions"""
from __future__ import annotations

import json
from dataclasses import dataclass, field

from scratchattach.utils import commons
from scratchattach.utils.enums import Languages, Language, TTSVoices, TTSVoice
from scratchattach.utils.exceptions import BadRequest, InvalidLanguage, InvalidTTSGender
from scratchattach.utils.requests import requests
from typing import Optional, TypedDict


# --- Front page ---

def get_news(*, limit=10, offset=0):
    return commons.api_iterative("https://api.scratch.mit.edu/news", limit=limit, offset=offset)


def featured_data() -> dict[str, list[dict[str, str | int]]]:
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

class TotalSiteStats(TypedDict):
    PROJECT_COUNT: int
    USER_COUNT: int
    STUDIO_COMMENT_COUNT: int
    PROFILE_COMMENT_COUNT: int
    STUDIO_COUNT: int
    COMMENT_COUNT: int
    PROJECT_COMMENT_COUNT: int


def total_site_stats() -> TotalSiteStats:
    data = requests.get("https://scratch.mit.edu/statistics/data/daily/").json()
    data.pop("_TS")
    return data


class MonthlySiteTraffic(TypedDict):
    pageviews: str
    users: str
    sessions: str


def monthly_site_traffic() -> MonthlySiteTraffic:
    data = requests.get("https://scratch.mit.edu/statistics/data/monthly-ga/").json()
    data.pop("_TS")
    return data


type CountryCounts = TypedDict("CountryCounts", {
    '0': int,  # not sure what 0 is. maybe it's the 'other' category
    'AT': int,
    'Afghanistan': int,
    'Aland Islands': int,
    'Albania': int,
    'Algeria': int,
    'American Samoa': int,
    'Andorra': int,
    'Angola': int,
    'Anguilla': int,
    'Antigua and Barbuda': int,
    'Argentina': int,
    'Armenia': int,
    'Aruba': int,
    'Australia': int,
    'Austria': int,
    'Azerbaijan': int,
    'Bahamas': int,
    'Bahrain': int,
    'Bangladesh': int,
    'Barbados': int,
    'Belarus': int,
    'Belgium': int,
    'Belize': int,
    'Benin': int,
    'Bermuda': int,
    'Bhutan': int,
    'Bolivia': int,
    'Bonaire, Sint Eustatius and Saba': int,
    'Bosnia and Herzegovina': int,
    'Botswana': int,
    'Bouvet Island': int,
    'Brazil': int,
    'British Indian Ocean Territory': int,
    'Brunei': int,
    'Brunei Darussalam': int,
    'Bulgaria': int,
    'Burkina Faso': int,
    'Burundi': int,
    'CA': int,
    'Cambodia': int,
    'Cameroon': int,
    'Canada': int,
    'Cape Verde': int,
    'Cayman Islands': int,
    'Central African Republic': int,
    'Chad': int,
    'Chile': int,
    'China': int,
    'Christmas Island': int,
    'Cocos (Keeling) Islands': int,
    'Colombia': int,
    'Comoros': int,
    'Congo': int,
    'Congo, Dem. Rep. of The': int,
    'Congo, The Democratic Republic of The': int,
    'Cook Islands': int,
    'Costa Rica': int,
    "Cote D'ivoire": int,
    'Croatia': int,
    'Cuba': int,
    'Curacao': int,
    'Cyprus': int,
    'Czech Republic': int,
    'Denmark': int,
    'Djibouti': int,
    'Dominica': int,
    'Dominican Republic': int,
    'Ecuador': int,
    'Egypt': int,
    'El Salvador': int,
    'England': int,
    'Equatorial Guinea': int,
    'Eritrea': int,
    'Estonia': int,
    'Ethiopia': int,
    'Falkland Islands (Malvinas)': int,
    'Faroe Islands': int,
    'Fiji': int,
    'Finland': int,
    'France': int,
    'French Guiana': int,
    'French Polynesia': int,
    'French Southern Territories': int,
    'GB': int,
    'GG': int,
    'Gabon': int,
    'Gambia': int,
    'Georgia': int,
    'Germany': int,
    'Ghana': int,
    'Gibraltar': int,
    'Greece': int,
    'Greenland': int,
    'Grenada': int,
    'Guadeloupe': int,
    'Guam': int,
    'Guatemala': int,
    'Guernsey': int,
    'Guinea': int,
    'Guinea-Bissau': int,
    'Guyana': int,
    'Haiti': int,
    'Heard Island and Mcdonald Islands': int,
    'Holy See (Vatican City State)': int,
    'Honduras': int,
    'Hong Kong': int,
    'Hungary': int,
    'IT': int,
    'Iceland': int,
    'India': int,
    'Indonesia': int,
    'Iran': int,
    'Iran, Islamic Republic of': int,
    'Iraq': int,
    'Ireland': int,
    'Isle of Man': int,
    'Israel': int,
    'Italy': int,
    'Jamaica': int,
    'Japan': int,
    'Jersey': int,
    'Jordan': int,
    'Kazakhstan': int,
    'Kenya': int,
    'Kiribati': int,
    "Korea, Dem. People's Rep.": int,
    "Korea, Democratic People's Republic of": int,
    'Korea, Republic of': int,
    'Kosovo': int,
    'Kuwait': int,
    'Kyrgyzstan': int,
    'Laos': int,
    'Latvia': int,
    'Lebanon': int,
    'Lesotho': int,
    'Liberia': int,
    'Libya': int,
    'Libyan Arab Jamahiriya': int,
    'Liechtenstein': int,
    'Lithuania': int,
    'Location not given': int,
    'Luxembourg': int,
    'Macao': int,
    'Macedonia': int,
    'Macedonia, The Former Yugoslav Republic of': int,
    'Madagascar': int,
    'Malawi': int,
    'Malaysia': int,
    'Maldives': int,
    'Mali': int,
    'Malta': int,
    'Marshall Islands': int,
    'Martinique': int,
    'Mauritania': int,
    'Mauritius': int,
    'Mayotte': int,
    'Mexico': int,
    'Micronesia, Federated States of': int,
    'Moldova': int,
    'Moldova, Republic of': int,
    'Monaco': int,
    'Mongolia': int,
    'Montenegro': int,
    'Montserrat': int,
    'Morocco': int,
    'Mozambique': int,
    'Myanmar': int,
    'NO': int,
    'Namibia': int,
    'Nauru': int,
    'Nepal': int,
    'Netherlands': int,
    'Netherlands Antilles': int,
    'New Caledonia': int,
    'New Zealand': int,
    'Nicaragua': int,
    'Niger': int,
    'Nigeria': int,
    'Niue': int,
    'Norfolk Island': int,
    'North Korea': int,
    'Northern Mariana Islands': int,
    'Norway': int,
    'Oman': int,
    'Pakistan': int,
    'Palau': int,
    'Palestine': int,
    'Palestine, State of': int,
    'Palestinian Territory, Occupied': int,
    'Panama': int,
    'Papua New Guinea': int,
    'Paraguay': int,
    'Peru': int,
    'Philippines': int,
    'Pitcairn': int,
    'Poland': int,
    'Portugal': int,
    'Puerto Rico': int,
    'Qatar': int,
    'Reunion': int,
    'Romania': int,
    'Russia': int,
    'Russian Federation': int,
    'Rwanda': int,
    'ST': int,
    'Saint Barthelemy': int,
    'Saint Helena': int,
    'Saint Kitts and Nevis': int,
    'Saint Lucia': int,
    'Saint Martin': int,
    'Saint Pierre and Miquelon': int,
    'Saint Vincent and The Grenadines': int,
    'Samoa': int,
    'San Marino': int,
    'Sao Tome and Principe': int,
    'Saudi Arabia': int,
    'Senegal': int,
    'Serbia': int,
    'Serbia and Montenegro': int,
    'Seychelles': int,
    'Sierra Leone': int,
    'Singapore': int,
    'Sint Maarten': int,
    'Slovakia': int,
    'Slovenia': int,
    'Solomon Islands': int,
    'Somalia': int,
    'Somewhere': int,
    'South Africa': int,
    'South Georgia and the South Sandwich Islands': int,
    'South Korea': int,
    'South Sudan': int,
    'Spain': int,
    'Sri Lanka': int,
    'St. Vincent': int,
    'Sudan': int,
    'Suriname': int,
    'Svalbard and Jan Mayen': int,
    'Swaziland': int,
    'Sweden': int,
    'Switzerland': int,
    'Syria': int,
    'Syrian Arab Republic': int,
    'TV': int,
    'Taiwan': int,
    'Taiwan, Province of China': int,
    'Tajikistan': int,
    'Tanzania': int,
    'Tanzania, United Republic of': int,
    'Thailand': int,
    'Timor-leste': int,
    'Togo': int,
    'Tokelau': int,
    'Tonga': int,
    'Trinidad and Tobago': int,
    'Tunisia': int,
    'Turkey': int,
    'Turkmenistan': int,
    'Turks and Caicos Islands': int,
    'Tuvalu': int,
    'US': int,
    'US Minor': int,
    'Uganda': int,
    'Ukraine': int,
    'United Arab Emirates': int,
    'United Kingdom': int,
    'United States': int,
    'United States Minor Outlying Islands': int,
    'Uruguay': int,
    'Uzbekistan': int,
    'Vanuatu': int,
    'Vatican City': int,
    'Venezuela': int,
    'Viet Nam': int,
    'Vietnam': int,
    'Virgin Islands, British': int,
    'Virgin Islands, U.S.': int,
    'Wallis and Futuna': int,
    'Western Sahara': int,
    'Yemen': int,
    'Zambia': int,
    'Zimbabwe': int
})


def country_counts() -> CountryCounts:
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


def send_password_reset_email(username: Optional[str] = None, email: Optional[str] = None):
    requests.post("https://scratch.mit.edu/accounts/password_reset/", data={
        "username": username,
        "email": email,
    }, headers=commons.headers, cookies={"scratchcsrftoken": 'a'})


def translate(language: str | Languages, text: str = "hello"):
    if isinstance(language, str):
        lang = Languages.find_by_attrs(language.lower(), ["code", "tts_locale", "name"], str.lower)
    elif isinstance(language, Languages):
        lang = language.value
    else:
        lang = language

    if not isinstance(lang, Language):
        raise InvalidLanguage(f"{language} is not a language")

    if lang.code is None:
        raise InvalidLanguage(f"{lang} is not a valid translate language")

    response_json = requests.get(
        f"https://translate-service.scratch.mit.edu/translate?language={lang.code}&text={text}").json()

    if "result" in response_json:
        return response_json["result"]
    else:
        raise BadRequest(f"Language '{language}' does not seem to be valid.\nResponse: {response_json}")


def text2speech(text: str = "hello", voice_name: str = "female", language: str = "en-US"):
    """
    Sends a request to Scratch's TTS synthesis service.
    Returns:
        - The TTS audio (mp3) as bytes
        - The playback rate (e.g. for giant it would be 0.84)
    """
    if isinstance(voice_name, str):
        voice = TTSVoices.find_by_attrs(voice_name.lower(), ["name", "gender"], str.lower)
    elif isinstance(voice_name, TTSVoices):
        voice = voice_name.value
    else:
        voice = voice_name

    if not isinstance(voice, TTSVoice):
        raise InvalidTTSGender(f"TTS Gender {voice_name} is not supported.")

    # If it's kitten, make sure to change everything to just meows
    if voice.name == "kitten":
        text = ''
        for word in text.split(' '):
            if word.strip() != '':
                text += "meow "

    if isinstance(language, str):
        lang = Languages.find_by_attrs(language.lower(), ["code", "tts_locale", "name"], str.lower)
    elif isinstance(language, Languages):
        lang = language.value
    else:
        lang = language

    if not isinstance(lang, Language):
        raise InvalidLanguage(f"Language '{language}' is not a language")

    if lang.tts_locale is None:
        raise InvalidLanguage(f"Language '{language}' is not a valid TTS language")

    response = requests.get(f"https://synthesis-service.scratch.mit.edu/synth"
                            f"?locale={lang.tts_locale}&gender={voice.gender}&text={text}")
    return response.content, voice.playback_rate
