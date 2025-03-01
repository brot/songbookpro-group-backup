from pathlib import Path
from time import sleep
import logging

from pathvalidate import sanitize_filename
from playwright.sync_api import Page, sync_playwright
from pydantic import DirectoryPath, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


# Configure and read settings
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    url: HttpUrl = "https://groups.songbookpro.app/dashboard"
    email: str
    password: str

    export_path: DirectoryPath

    chord_over_lyrics_extension: str = ".crd"
    chord_pro_extension: str = ".cho"


SETTINGS = Settings()

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)
LOGGER = logging.getLogger(__name__)


def login(page: Page):
    page.wait_for_selector("#email").fill(SETTINGS.email)
    page.wait_for_selector("#password").fill(SETTINGS.password)
    page.wait_for_selector("#next").click()
    page.wait_for_load_state()

    sleep(10)


def save_file(page: Page, artist: str, title: str, file_extension: str):
    filename = SETTINGS.export_path / Path(
        sanitize_filename(f"{artist.replace(".", "_")} - {title.replace(".", "_")}")
    ).with_suffix(file_extension)

    song_content = page.wait_for_selector(
        "textarea[placeholder='Song Content']"
    ).text_content()

    stored_song = ""
    if filename.exists():
        with open(filename, "r") as fobj:
            stored_song = fobj.read()

    if stored_song != song_content:
        if stored_song:
            LOGGER.info("--- Save %s - different", filename)
        else:
            LOGGER.info("--- Save %s - new song", filename)

        with open(filename, "w") as fobj:
            fobj.write(song_content)


def process_song(page: Page, sequence: int, artist: str, title: str):
    LOGGER.info("[%03d] Process: %s - %s", sequence, artist, title)

    chord_over_lyrics_option = page.query_selector("input[value='col']")
    chord_over_lyrics_label = page.query_selector(
        f"label[for='{chord_over_lyrics_option.get_attribute("id")}']"
    )
    assert chord_over_lyrics_option is not None
    assert chord_over_lyrics_label is not None

    chord_pro_option = page.query_selector("input[value='cpo']")
    chord_pro_label = page.query_selector(
        f"label[for='{chord_pro_option.get_attribute("id")}']"
    )
    assert chord_pro_option is not None
    assert chord_pro_label is not None

    for _ in range(2):
        if chord_over_lyrics_option.is_checked():
            save_file(page, artist, title, SETTINGS.chord_over_lyrics_extension)
            chord_pro_label.check()
        else:
            save_file(page, artist, title, SETTINGS.chord_pro_extension)
            chord_over_lyrics_label.check()

    buttons = page.query_selector_all("button")[::-1]
    cancel_button = next(
        (button for button in buttons if "Cancel" in button.text_content()),
        None,
    )
    cancel_button.click()


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(str(SETTINGS.url))

        login(page)

        # just wait a little bit to make sure all songs are loaded
        page.wait_for_selector(".py-2")
        for i, song in enumerate(page.query_selector_all(".py-2"), start=1):
            artist = song.query_selector(".font-light").text_content()
            title = song.query_selector(".font-medium").text_content()
            song.query_selector("[title='Edit']").click()

            process_song(page, i, artist, title)

        browser.close()


if __name__ == "__main__":
    main()
