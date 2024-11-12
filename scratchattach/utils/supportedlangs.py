"""
List of supported languages of scratch's translate extension.
Adapted from https://translate-service.scratch.mit.edu/supported?language=en
"""

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
