import undetected_chromedriver as uc
from selenium.webdriver.support import expected_conditions as ec

from .scratchblocks_lang import LANGUAGES
from ..utils.commons import driver, wait

By = uc.By


class ScratchVersion:
    scratch2 = "scratch2"  # "Scratch 2.0"
    scratch3 = "scratch3"  # "Scratch 3.0"
    scratch3_high_contrast = "scratch3-high-contrast"  # "Scratch 3.0 (high-contrast)"


def scratchblocks_to_svg(code: str, scratch_version: str = ScratchVersion.scratch3, lang: str = '') -> str:
    driver.get(f"https://scratchblocks.github.io/#?style={scratch_version}&lang={lang}&script={code}")
    wait.until(ec.visibility_of_element_located((By.TAG_NAME, "path")))

    return driver.find_element(By.ID, "export-svg").get_attribute("href")


def scratchblocks_to_png(code: str, scratch_version: str = ScratchVersion.scratch3, lang: str = '') -> str:
    if lang not in LANGUAGES.values():
        if lang in LANGUAGES.keys():
            lang = LANGUAGES[lang]
        else:
            lang = LANGUAGES['']

    driver.get(f"https://scratchblocks.github.io/#?style={scratch_version}&lang={lang}&script={code}")
    wait.until(ec.visibility_of_element_located((By.TAG_NAME, "path")))

    return driver.find_element(By.ID, "export-png").get_attribute("href")


def translate_scratchblocks(code: str, lang: str = ''):
    if lang not in LANGUAGES.values():
        if lang in LANGUAGES.keys():
            lang = LANGUAGES[lang]
        else:
            lang = LANGUAGES['']
    if lang == LANGUAGES['']:
        lang = LANGUAGES["English"]

    driver.get(f"https://scratchblocks.github.io/translator/#?lang={lang}&script={code}")
    wait.until(ec.visibility_of_element_located((By.ID, "out-preview")))

    return driver.execute_script(f"return document.getElementById(\"out-editor\").value;")
