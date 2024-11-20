"""
List of supported languages of scratch's translate and text2speech extensions.
Adapted from https://translate-service.scratch.mit.edu/supported?language=en
"""

from enum import Enum
from dataclasses import dataclass

from typing import Callable


@dataclass(init=True, repr=True)
class _Language:
    name: str = None
    code: str = None
    locales: list[str] = None
    tts_locale: str = None
    single_gender: bool = None


class Languages(Enum):
    Albanian = _Language('Albanian', 'sq', None, None, None)
    Amharic = _Language('Amharic', 'am', None, None, None)
    Arabic = _Language('Arabic', 'ar', ['ar'], 'arb', True)
    Armenian = _Language('Armenian', 'hy', None, None, None)
    Azerbaijani = _Language('Azerbaijani', 'az', None, None, None)
    Basque = _Language('Basque', 'eu', None, None, None)
    Belarusian = _Language('Belarusian', 'be', None, None, None)
    Bulgarian = _Language('Bulgarian', 'bg', None, None, None)
    Catalan = _Language('Catalan', 'ca', None, None, None)
    Chinese_Traditional = _Language('Chinese (Traditional)', 'zh-tw', None, None, None)
    Croatian = _Language('Croatian', 'hr', None, None, None)
    Czech = _Language('Czech', 'cs', None, None, None)
    Danish = _Language('Danish', 'da', ['da'], 'da-DK', False)
    Dutch = _Language('Dutch', 'nl', ['nl'], 'nl-NL', False)
    English = _Language('English', 'en', ['en'], 'en-US', False)
    Esperanto = _Language('Esperanto', 'eo', None, None, None)
    Estonian = _Language('Estonian', 'et', None, None, None)
    Finnish = _Language('Finnish', 'fi', None, None, None)
    French = _Language('French', 'fr', ['fr'], 'fr-FR', False)
    Galician = _Language('Galician', 'gl', None, None, None)
    German = _Language('German', 'de', ['de'], 'de-DE', False)
    Greek = _Language('Greek', 'el', None, None, None)
    Haitian_Creole = _Language('Haitian Creole', 'ht', None, None, None)
    Hindi = _Language('Hindi', 'hi', ['hi'], 'hi-IN', True)
    Hungarian = _Language('Hungarian', 'hu', None, None, None)
    Icelandic = _Language('Icelandic', 'is', ['is'], 'is-IS', False)
    Indonesian = _Language('Indonesian', 'id', None, None, None)
    Irish = _Language('Irish', 'ga', None, None, None)
    Italian = _Language('Italian', 'it', ['it'], 'it-IT', False)
    Japanese = _Language('Japanese', 'ja', ['ja', 'ja-hira'], 'ja-JP', False)
    Kannada = _Language('Kannada', 'kn', None, None, None)
    Korean = _Language('Korean', 'ko', ['ko'], 'ko-KR', True)
    Kurdish_Kurmanji = _Language('Kurdish (Kurmanji)', 'ku', None, None, None)
    Latin = _Language('Latin', 'la', None, None, None)
    Latvian = _Language('Latvian', 'lv', None, None, None)
    Lithuanian = _Language('Lithuanian', 'lt', None, None, None)
    Macedonian = _Language('Macedonian', 'mk', None, None, None)
    Malay = _Language('Malay', 'ms', None, None, None)
    Malayalam = _Language('Malayalam', 'ml', None, None, None)
    Maltese = _Language('Maltese', 'mt', None, None, None)
    Maori = _Language('Maori', 'mi', None, None, None)
    Marathi = _Language('Marathi', 'mr', None, None, None)
    Mongolian = _Language('Mongolian', 'mn', None, None, None)
    Myanmar_Burmese = _Language('Myanmar (Burmese)', 'my', None, None, None)
    Persian = _Language('Persian', 'fa', None, None, None)
    Polish = _Language('Polish', 'pl', ['pl'], 'pl-PL', False)
    Portuguese = _Language('Portuguese', 'pt', None, None, None)
    Romanian = _Language('Romanian', 'ro', ['ro'], 'ro-RO', True)
    Russian = _Language('Russian', 'ru', ['ru'], 'ru-RU', False)
    Scots_Gaelic = _Language('Scots Gaelic', 'gd', None, None, None)
    Serbian = _Language('Serbian', 'sr', None, None, None)
    Slovak = _Language('Slovak', 'sk', None, None, None)
    Slovenian = _Language('Slovenian', 'sl', None, None, None)
    Spanish = _Language('Spanish', 'es', None, None, None)
    Swedish = _Language('Swedish', 'sv', ['sv'], 'sv-SE', True)
    Telugu = _Language('Telugu', 'te', None, None, None)
    Thai = _Language('Thai', 'th', None, None, None)
    Turkish = _Language('Turkish', 'tr', ['tr'], 'tr-TR', True)
    Ukrainian = _Language('Ukrainian', 'uk', None, None, None)
    Uzbek = _Language('Uzbek', 'uz', None, None, None)
    Vietnamese = _Language('Vietnamese', 'vi', None, None, None)
    Welsh = _Language('Welsh', 'cy', ['cy'], 'cy-GB', True)
    Zulu = _Language('Zulu', 'zu', None, None, None)
    Hebrew = _Language('Hebrew', 'he', None, None, None)
    Chinese_Simplified = _Language('Chinese (Simplified)', 'zh-cn', None, None, None)
    Mandarin = Chinese_Simplified

    cmn_CN = _Language(None, None, ['zh-cn', 'zh-tw'], 'cmn-CN', True)
    nb_NO = _Language(None, None, ['nb', 'nn'], 'nb-NO', True)
    pt_BR = _Language(None, None, ['pt-br'], 'pt-BR', False)
    Brazilian = pt_BR
    pt_PT = _Language(None, None, ['pt'], 'pt-PT', False)
    es_ES = _Language(None, None, ['es'], 'es-ES', False)
    es_US = _Language(None, None, ['es-419'], 'es-US', False)

    @staticmethod
    def find(value, by: str = "name", apply_func: Callable = None) -> _Language:
        """
        Finds the language with the given attribute that is equal to the given value.
        the apply_func will be applied to the attribute of each language object before comparison.

        i.e. Languages.find("ukranian", "name", str.lower) will return the Ukrainian language dataclass object
        (even though Ukrainian was spelt lowercase, since str.lower will convert the "Ukrainian" string to lowercase)
        """
        if apply_func is None:
            def apply_func(x):
                return x

        for lang_enum in Languages:
            lang = lang_enum.value

            try:
                if apply_func(getattr(lang, by)) == value:
                    return lang
            except TypeError:
                pass

    @staticmethod
    def all_of(attr_name: str = "name", apply_func: Callable = None):
        """
        Returns the list of each listed language's specified attribute by "attr_name"

        i.e. Languages.all_of("name") will return a list of names:
        ["Albanian", "Amharic", ...]

        The apply_func function will be applied to every list item,
        i.e. Languages.all_of("name", str.lower) will return the same except in lowercase:
        ["albanian", "amharic", ...]
        """
        if apply_func is None:
            def apply_func(x):
                return x

        for lang_enum in Languages:
            lang = lang_enum.value
            attr = getattr(lang, attr_name)
            try:
                yield apply_func(attr)

            except TypeError:
                yield attr
