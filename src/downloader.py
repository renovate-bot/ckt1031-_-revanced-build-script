import json
from colorama import Fore, Style
import os, requests
from urllib.request import urlretrieve
from src._config import config
from distutils.version import StrictVersion
from selectolax.lexbor import LexborHTMLParser
from requests import Session


class Downloader:
    def __init__(self):
        self.session = Session()
        self.session.headers["User-Agent"] = "anything"

    def _download(self, url: str, name: str) -> str:
        filepath = f"./{config['dist_dir']}/{name}"

        # Check if the tool exists
        if os.path.exists(filepath):
            print(
                Fore.YELLOW
                + f"⚠️ {filepath} already exists, skipping"
                + Style.RESET_ALL
            )
            return filepath

        with self.session.get(url, stream=True) as r:
            r.raise_for_status()
            with open(filepath, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        print(Fore.GREEN + f"✅ {filepath} downloaded" + Style.RESET_ALL)
        return filepath

    def download_required(self):
        print(Fore.BLUE + "⬇️ Downloading required resources" + Style.RESET_ALL)

        # Get the tool list
        tools = requests.get("https://releases.revanced.app/tools").json()

        # Download the tools
        download_repository = [
            "revanced/revanced-cli",
            "revanced/revanced-patches",
            "revanced/revanced-integrations",
        ]

        downloaded_files = {}

        for tool in tools["tools"]:
            if tool["repository"] in download_repository:
                filepath = self._download(tool["browser_download_url"], tool["name"])

                name = tool["repository"].replace("revanced/", "")

                downloaded_files[name] = filepath

        return downloaded_files

    def get_download_page(self, parser: LexborHTMLParser) -> str:
        apm = parser.css(".apkm-badge")

        sub_url = ""
        for is_apm in apm:
            parent_text = is_apm.parent.parent.text()

            if "APK" in is_apm.text() and (
                "arm64-v8a" in parent_text
                or "universal" in parent_text
                or "noarch" in parent_text
            ):
                parser = is_apm.parent
                sub_url = parser.css_first(".accent_color").attributes["href"]
                break
        if sub_url == "":
            raise Exception("No download page found")
        download_url = "https://www.apkmirror.com" + sub_url
        return download_url

    def extract_download_link(self, page: str, app: str) -> None:
        parser = LexborHTMLParser(self.session.get(page).text)

        resp = self.session.get(
            "https://www.apkmirror.com"
            + parser.css_first("a.accent_bg").attributes["href"]
        )
        parser = LexborHTMLParser(resp.text)

        href = parser.css_first(
            "p.notes:nth-child(3) > span:nth-child(1) > a:nth-child(1)"
        ).attributes["href"]

        self._download("https://www.apkmirror.com" + href, f"{app}.apk")

    def download_apk(self, app_name: str):
        # Load from patches.json
        with open(f"./{config['dist_dir']}/patches.json", "r") as patches_file:
            patches = json.load(patches_file)

            # Reference APK app name
            app = {
                "youtube": {
                    "name": "com.google.android.youtube",
                    "apkmirror": "google-inc/youtube/youtube",
                },
                "youtube-music": {
                    "name": "com.google.android.apps.youtube.music",
                    "apkmirror": "google-inc/youtube-music/youtube-music",
                },
            }

            for patch in patches:
                for package in patch["compatiblePackages"]:
                    if package["name"] == app[app_name]["name"]:
                        versions = package["versions"]

                        version = max(versions, key=StrictVersion)

                        page = f"https://www.apkmirror.com/apk/{app[app_name]['apkmirror']}-{version}-release/"

                        parser = LexborHTMLParser(
                            self.session.get(page, timeout=10).text
                        )
                        download_page = self.get_download_page(parser)

                        parser = LexborHTMLParser(self.session.get(download_page).text)

                        resp = self.session.get(
                            "https://www.apkmirror.com"
                            + parser.css_first("a.accent_bg").attributes["href"]
                        )
                        parser = LexborHTMLParser(resp.text)

                        href = parser.css_first(
                            "p.notes:nth-child(3) > span:nth-child(1) > a:nth-child(1)"
                        ).attributes["href"]

                        filename = f"{app[app_name]['name']}-{version}.apk"

                        return self._download(
                            "https://www.apkmirror.com" + href, filename
                        )
