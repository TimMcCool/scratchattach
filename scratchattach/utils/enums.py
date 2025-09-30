"""
List of supported languages of scratch's translate and text2speech extensions.
Adapted from https://translate-service.scratch.mit.edu/supported?language=en
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Callable, Iterable


@dataclass
class Language:
    name: str = None
    code: str = None
    locales: list[str] = None
    tts_locale: str = None
    single_gender: bool = None


# should this underscore be removed
class _EnumWrapper(Enum):
    @classmethod
    def find(cls, value, by: str, apply_func: Optional[Callable] = None):
        """
        Finds the enum item with the given attribute that is equal to the given value.
        the apply_func will be applied to the attribute of each language object before comparison.

        i.e. Languages.find("ukranian", "name", str.lower) will return the Ukrainian language dataclass object
        (even though Ukrainian was spelt lowercase, since str.lower will convert the "Ukrainian" string to lowercase)
        """
        if apply_func is None:
            def apply_func(x):
                return x

        for item in cls:
            item_obj = item.value

            try:
                if by is None:
                    _val = item_obj
                else:
                    _val = getattr(item_obj, by)

                if apply_func(_val) == value:
                    return item_obj

            except TypeError:
                pass

    @classmethod
    def all_of(cls, attr_name: str, apply_func: Optional[Callable] = None) -> Iterable:
        """
        Returns the list of each listed enum item's specified attribute by "attr_name"

        i.e. Languages.all_of("name") will return a list of names:
        ["Albanian", "Amharic", ...]

        The apply_func function will be applied to every list item,
        i.e. Languages.all_of("name", str.lower) will return the same except in lowercase:
        ["albanian", "amharic", ...]
        """
        if apply_func is None:
            def apply_func(x):
                return x

        for item in cls:
            item_obj = item.value
            attr = getattr(item_obj, attr_name)
            try:
                yield apply_func(attr)

            except TypeError:
                yield attr

    @classmethod
    def find_by_attrs(cls, value, bys: list[str], apply_func: Optional[Callable] = None) -> list:
        """
        Calls the EnumWrapper.by function multiple times until a match is found, using the provided 'by' attribute names
        """
        for by in bys:
            ret = cls.find(value, by, apply_func)
            if ret is not None:
                return ret


class Languages(_EnumWrapper):
    Albanian = Language('Albanian', 'sq', None, None, None)
    Amharic = Language('Amharic', 'am', None, None, None)
    Arabic = Language('Arabic', 'ar', ['ar'], 'arb', True)
    Armenian = Language('Armenian', 'hy', None, None, None)
    Azerbaijani = Language('Azerbaijani', 'az', None, None, None)
    Basque = Language('Basque', 'eu', None, None, None)
    Belarusian = Language('Belarusian', 'be', None, None, None)
    Bulgarian = Language('Bulgarian', 'bg', None, None, None)
    Catalan = Language('Catalan', 'ca', None, None, None)
    Chinese_Traditional = Language('Chinese (Traditional)', 'zh-tw', ['zh-cn', 'zh-tw'], 'cmn-CN', True)
    Croatian = Language('Croatian', 'hr', None, None, None)
    Czech = Language('Czech', 'cs', None, None, None)
    Danish = Language('Danish', 'da', ['da'], 'da-DK', False)
    Dutch = Language('Dutch', 'nl', ['nl'], 'nl-NL', False)
    English = Language('English', 'en', ['en'], 'en-US', False)
    Esperanto = Language('Esperanto', 'eo', None, None, None)
    Estonian = Language('Estonian', 'et', None, None, None)
    Finnish = Language('Finnish', 'fi', None, None, None)
    French = Language('French', 'fr', ['fr'], 'fr-FR', False)
    Galician = Language('Galician', 'gl', None, None, None)
    German = Language('German', 'de', ['de'], 'de-DE', False)
    Greek = Language('Greek', 'el', None, None, None)
    Haitian_Creole = Language('Haitian Creole', 'ht', None, None, None)
    Hindi = Language('Hindi', 'hi', ['hi'], 'hi-IN', True)
    Hungarian = Language('Hungarian', 'hu', None, None, None)
    Icelandic = Language('Icelandic', 'is', ['is'], 'is-IS', False)
    Indonesian = Language('Indonesian', 'id', None, None, None)
    Irish = Language('Irish', 'ga', None, None, None)
    Italian = Language('Italian', 'it', ['it'], 'it-IT', False)
    Japanese = Language('Japanese', 'ja', ['ja', 'ja-hira'], 'ja-JP', False)
    Kannada = Language('Kannada', 'kn', None, None, None)
    Korean = Language('Korean', 'ko', ['ko'], 'ko-KR', True)
    Kurdish_Kurmanji = Language('Kurdish (Kurmanji)', 'ku', None, None, None)
    Latin = Language('Latin', 'la', None, None, None)
    Latvian = Language('Latvian', 'lv', None, None, None)
    Lithuanian = Language('Lithuanian', 'lt', None, None, None)
    Macedonian = Language('Macedonian', 'mk', None, None, None)
    Malay = Language('Malay', 'ms', None, None, None)
    Malayalam = Language('Malayalam', 'ml', None, None, None)
    Maltese = Language('Maltese', 'mt', None, None, None)
    Maori = Language('Maori', 'mi', None, None, None)
    Marathi = Language('Marathi', 'mr', None, None, None)
    Mongolian = Language('Mongolian', 'mn', None, None, None)
    Myanmar_Burmese = Language('Myanmar (Burmese)', 'my', None, None, None)
    Persian = Language('Persian', 'fa', None, None, None)
    Polish = Language('Polish', 'pl', ['pl'], 'pl-PL', False)
    Portuguese = Language('Portuguese', 'pt', ['pt'], 'pt-PT', False)
    Romanian = Language('Romanian', 'ro', ['ro'], 'ro-RO', True)
    Russian = Language('Russian', 'ru', ['ru'], 'ru-RU', False)
    Scots_Gaelic = Language('Scots Gaelic', 'gd', None, None, None)
    Serbian = Language('Serbian', 'sr', None, None, None)
    Slovak = Language('Slovak', 'sk', None, None, None)
    Slovenian = Language('Slovenian', 'sl', None, None, None)
    Spanish = Language('Spanish', 'es', None, None, None)
    Swedish = Language('Swedish', 'sv', ['sv'], 'sv-SE', True)
    Telugu = Language('Telugu', 'te', None, None, None)
    Thai = Language('Thai', 'th', None, None, None)
    Turkish = Language('Turkish', 'tr', ['tr'], 'tr-TR', True)
    Ukrainian = Language('Ukrainian', 'uk', None, None, None)
    Uzbek = Language('Uzbek', 'uz', None, None, None)
    Vietnamese = Language('Vietnamese', 'vi', None, None, None)
    Welsh = Language('Welsh', 'cy', ['cy'], 'cy-GB', True)
    Zulu = Language('Zulu', 'zu', None, None, None)
    Hebrew = Language('Hebrew', 'he', None, None, None)
    Chinese_Simplified = Language('Chinese (Simplified)', 'zh-cn', ['zh-cn', 'zh-tw'], 'cmn-CN', True)
    Mandarin = Chinese_Simplified

    nb_NO = Language(None, None, ['nb', 'nn'], 'nb-NO', True)
    pt_BR = Language(None, None, ['pt-br'], 'pt-BR', False)
    Brazilian = pt_BR
    es_ES = Language(None, None, ['es'], 'es-ES', False)
    es_US = Language(None, None, ['es-419'], 'es-US', False)

    @classmethod
    def find(cls, value, by: str = "name", apply_func: Optional[Callable] = None) -> Language:
        return super().find(value, by, apply_func)

    @classmethod
    def all_of(cls, attr_name: str = "name", apply_func: Optional[Callable] = None) -> list:
        return super().all_of(attr_name, apply_func)


@dataclass
class TTSVoice:
    name: str
    gender: str
    playback_rate: float | int = 1


class TTSVoices(_EnumWrapper):
    alto = TTSVoice("alto", "female")
    # female is functionally equal to alto
    female = TTSVoice("female", "female")

    tenor = TTSVoice("tenor", "male")
    # male is functionally equal to tenor
    male = TTSVoice("male", "male")

    squeak = TTSVoice("squeak", "female", 1.19)
    giant = TTSVoice("giant", "male", .84)
    kitten = TTSVoice("kitten", "female", 1.41)

    @classmethod
    def find(cls, value, by: str = "name", apply_func: Optional[Callable] = None) -> TTSVoice:
        return super().find(value, by, apply_func)

    @classmethod
    def all_of(cls, attr_name: str = "name", apply_func: Optional[Callable] = None) -> Iterable:
        return super().all_of(attr_name, apply_func)


@dataclass
class AlertType:
    id: int
    message: str


class AlertTypes(_EnumWrapper):
    """
    Enum for associating alert type indecies with their messages, for use with the str.format() method.
    """
    # Reference: https://github.com/TimMcCool/scratchattach/issues/304#issuecomment-2800110811
    # NOTE: THE TEXT WITHIN THE BRACES HERE MATTERS! IF YOU WANT TO CHANGE IT, MAKE SURE TO EDIT `site.alert.EducatorAlert`!
    ban = AlertType(0, "{username} was banned.")
    unban = AlertType(1, "{username} was unbanned.")
    excluded_from_homepage = AlertType(2, "{username} was excluded from homepage")
    excluded_from_homepage2 = AlertType(3, "{username} was excluded from homepage") # for some reason there are duplicates
    notified = AlertType(4, "{username} was notified by a Scratch Administrator. Notification type: {notification_type}") # not sure what notification type is
    autoban = AlertType(5, "{username} was banned automatically")
    autoremoved = AlertType(6, "{project} by {username} was removed automatically")
    project_censored2 = AlertType(7, "{project} by {username} was censored.")  # <empty #7>
    project_censored = AlertType(20, "{project} by {username} was censored.")
    project_uncensored = AlertType(8, "{project} by {username} was uncensored.")
    project_reviewed2 = AlertType(9, "{project} by {username} was reviewed by a Scratch Administrator.")  # <empty #9>
    project_reviewed = AlertType(10, "{project} by {username} was reviewed by a Scratch Administrator.")
    project_deleted = AlertType(11, "{project} by {username} was deleted by a Scratch Administrator.")
    user_deleted2 = AlertType(12, "{username} was deleted by a Scratch Administrator")  # <empty #12>
    user_deleted = AlertType(17, "{username} was deleted by a Scratch Administrator")
    studio_reviewed2 = AlertType(13, "{studio} was reviewed by a Scratch Administrator.")  # <empty #13>
    studio_reviewed = AlertType(14, "{studio} was reviewed by a Scratch Administrator.")
    studio_deleted = AlertType(15, "{studio} was deleted by a Scratch Administrator.")
    email_confirm2 = AlertType(16, "The email address of {username} was confirmed by a Scratch Administrator")  # <empty #16>
    email_confirm = AlertType(18, "The email address of {username} was confirmed by a Scratch Administrator") # no '.' in HTML
    email_unconfirm = AlertType(19, "The email address of {username} was set as not confirmed by a Scratch Administrator")
    automute = AlertType(22, "{username} was automatically muted by our comment filters. The comment they tried to post was: {comment}")
    default = AlertType(-1, "{username} had an admin action performed.") # default case

    @classmethod
    def find(cls, value, by: str = "id", apply_func: Optional[Callable] = None) -> AlertType:
        return super().find(value, by, apply_func)
