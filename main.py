""" Get the newest release that supports specified minecraft version
if no version is specified we get the latest release
"""

from urllib.parse import urlparse, unquote
from requests import Session
from pathlib import Path
import pyjson5 as json
import requests


BASE = "https://api.modrinth.com/v2"
H = {"User-Agent": "my_cool_app"}


def download(session: Session, url: str) -> None:
    # from https://stackoverflow.com/a/15803460
    p = urlparse(url).path
    filename = p.rsplit("/", 1)[-1]
    filename = unquote(filename, "utf-8")

    mods = Path("mods")
    mods.mkdir(exist_ok=True)
    with open(mods / filename, "wb") as outfp:
        outfp.write(session.get(url).content)


def get_release(session: Session, slug: str, version: str) -> None:
    for project in session.get(f"{BASE}/project/{slug}/version", headers=H).json():
        if version in project["game_versions"]:
            url = project["files"][0]["url"]
            print("downloading slug", slug)
            download(session, url)
            return
    else:
        print(f"version {version} not avalable found for {slug} skipped")


if __name__ == "__main__":
    session = requests.session()

    with open("mods.jsonc") as infp:
        content: dict = json.load(infp)
        version: str = content["version"]
        mods: list[str] = content["mods"]

    for mod in mods:
        if mod.startswith("https://") or mod.startswith("http://"):
            url = mod
            print("downloading from url", url)
            download(session, url)
        else:
            mod = mod.lower()
            if session.get(f"{BASE}/project/{mod}/check", headers=H).status_code == 200:
                get_release(session, mod, version)
            else:
                print(f"could not find", mod)


# TODO:
# - [X] modrinth support https://docs.modrinth.com/api-spec/
# - [ ] curse forge support https://docs.curseforge.com/
# - [ ] spigot support https://spiget.org/