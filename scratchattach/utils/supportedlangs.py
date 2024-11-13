"""
List of supported languages of scratch's translate and text2speech extensions.
Adapted from https://translate-service.scratch.mit.edu/supported?language=en
"""

# Supported langs for translate
SUPPORTED_LANGS = {'sq': 'Albanian', 'am': 'Amharic', 'ar': 'Arabic', 'hy': 'Armenian', 'az': 'Azerbaijani',
                   'eu': 'Basque', 'be': 'Belarusian', 'bg': 'Bulgarian', 'ca': 'Catalan',
                   'zh-tw': 'Chinese (Traditional)', 'hr': 'Croatian', 'cs': 'Czech', 'da': 'Danish', 'nl': 'Dutch',
                   'en': 'English', 'eo': 'Esperanto', 'et': 'Estonian', 'fi': 'Finnish', 'fr': 'French',
                   'gl': 'Galician', 'de': 'German', 'el': 'Greek', 'ht': 'Haitian Creole', 'hi': 'Hindi',
                   'hu': 'Hungarian', 'is': 'Icelandic', 'id': 'Indonesian', 'ga': 'Irish', 'it': 'Italian',
                   'ja': 'Japanese', 'kn': 'Kannada', 'ko': 'Korean', 'ku': 'Kurdish (Kurmanji)', 'la': 'Latin',
                   'lv': 'Latvian', 'lt': 'Lithuanian', 'mk': 'Macedonian', 'ms': 'Malay', 'ml': 'Malayalam',
                   'mt': 'Maltese', 'mi': 'Maori', 'mr': 'Marathi', 'mn': 'Mongolian', 'my': 'Myanmar (Burmese)',
                   'fa': 'Persian', 'pl': 'Polish', 'pt': 'Portuguese', 'ro': 'Romanian', 'ru': 'Russian',
                   'gd': 'Scots Gaelic', 'sr': 'Serbian', 'sk': 'Slovak', 'sl': 'Slovenian', 'es': 'Spanish',
                   'sv': 'Swedish', 'te': 'Telugu', 'th': 'Thai', 'tr': 'Turkish', 'uk': 'Ukrainian', 'uz': 'Uzbek',
                   'vi': 'Vietnamese', 'cy': 'Welsh', 'zu': 'Zulu', 'he': 'Hebrew', 'zh-cn': 'Chinese (Simplified)'}
SUPPORTED_CODES = tuple(SUPPORTED_LANGS.keys())
SUPPORTED_NAMES = tuple(SUPPORTED_LANGS.values())

# Code for generating the dict again:
# import requests
#
# SUPPORTED_LANGS = {}
# raw = requests.get("https://translate-service.scratch.mit.edu/supported").json()
# for lang in raw:
#     SUPPORTED_LANGS[lang["code"]] = lang["name"]
# print(SUPPORTED_LANGS)

# Language info for tts
TTS_LANGUAGE_INFO = [
    {
        "name": 'Arabic',
        "locales": ['ar'],
        "speechSynthLocale": 'arb',
        "singleGender": True
    },
    {
        "name": 'Chinese (Mandarin)',
        "locales": ['zh-cn', 'zh-tw'],
        "speechSynthLocale": 'cmn-CN',
        "singleGender": True
    },
    {
        "name": 'Danish',
        "locales": ['da'],
        "speechSynthLocale": 'da-DK'
    },
    {
        "name": 'Dutch',
        "locales": ['nl'],
        "speechSynthLocale": 'nl-NL'
    },
    {
        "name": 'English',
        "locales": ['en'],
        "speechSynthLocale": 'en-US'
    },
    {
        "name": 'French',
        "locales": ['fr'],
        "speechSynthLocale": 'fr-FR'
    },
    {
        "name": 'German',
        "locales": ['de'],
        "speechSynthLocale": 'de-DE'
    },
    {
        "name": 'Hindi',
        "locales": ['hi'],
        "speechSynthLocale": 'hi-IN',
        "singleGender": True
    },
    {
        "name": 'Icelandic',
        "locales": ['is'],
        "speechSynthLocale": 'is-IS'
    },
    {
        "name": 'Italian',
        "locales": ['it'],
        "speechSynthLocale": 'it-IT'
    },
    {
        "name": 'Japanese',
        "locales": ['ja', 'ja-hira'],
        "speechSynthLocale": 'ja-JP'
    },
    {
        "name": 'Korean',
        "locales": ['ko'],
        "speechSynthLocale": 'ko-KR',
        "singleGender": True
    },
    {
        "name": 'Norwegian',
        "locales": ['nb', 'nn'],
        "speechSynthLocale": 'nb-NO',
        "singleGender": True
    },
    {
        "name": 'Polish',
        "locales": ['pl'],
        "speechSynthLocale": 'pl-PL'
    },
    {
        "name": 'Portuguese (Brazilian)',
        "locales": ['pt-br'],
        "speechSynthLocale": 'pt-BR'
    },
    {
        "name": 'Portuguese (European)',
        "locales": ['pt'],
        "speechSynthLocale": 'pt-PT'
    },
    {
        "name": 'Romanian',
        "locales": ['ro'],
        "speechSynthLocale": 'ro-RO',
        "singleGender": True
    },
    {
        "name": 'Russian',
        "locales": ['ru'],
        "speechSynthLocale": 'ru-RU'
    },
    {
        "name": 'Spanish (European)',
        "locales": ['es'],
        "speechSynthLocale": 'es-ES'
    },
    {
        "name": 'Spanish (Latin American)',
        "locales": ['es-419'],
        "speechSynthLocale": 'es-US'
    },
    {
        "name": 'Swedish',
        "locales": ['sv'],
        "speechSynthLocale": 'sv-SE',
        "singleGender": True
    },
    {
        "name": 'Turkish',
        "locales": ['tr'],
        "speechSynthLocale": 'tr-TR',
        "singleGender": True
    },
    {
        "name": 'Welsh',
        "locales": ['cy'],
        "speechSynthLocale": 'cy-GB',
        "singleGender": True
    }]


def tts_lang(attribute: str, by: str = None):
    for lang in TTS_LANGUAGE_INFO:
        if by is None:
            if attribute in lang.values():
                return lang
            continue

        if lang.get(by) == attribute:
            return lang
