import json
import os

import requests
from loguru import logger

from src._config import app_reference, config
from src.apkmirror import APKmirror


class Downloader:
    def __init__(self):
        self.client = requests.Session()
        self.client.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0)"
                + " Gecko/20100101 Firefox/112.0"
            }
        )

    def _download(self, url: str, name: str) -> str:
        filepath = f"./{config['dist_dir']}/{name}"

        # Check if the tool exists
        if os.path.exists(filepath):
            logger.warning(f"{filepath} already exists, skipping")
            return filepath

        with self.client.get(url, stream=True) as res:
            res.raise_for_status()

            with open(filepath, "wb") as file:
                for chunk in res.iter_content(chunk_size=8192):
                    file.write(chunk)

        logger.success(f"{filepath} downloaded")

        return filepath

    def download_required(self):
        logger.info("Downloading required resources")

        # Get the tool list
        tools = self.client.get("https://releases.revanced.app/tools").json()

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

    def download_apk(self, app_name: str):
        hasversion = False

        # Load from patches.json
        with open(f"./{config['dist_dir']}/patches.json", "r") as patches_file:
            patches = json.load(patches_file)

            for patch in patches:
                for package in patch["compatiblePackages"]:
                    if package["name"] == app_reference[app_name]["name"]:
                        version = package["versions"]

                        if len(version) == 0:
                            continue

                        version = version[-1]

                        hasversion = True

                        page = (
                            f"{app_reference[app_name]['apkmirror']}"
                            + f"-{version.replace('.', '-')}-release/"
                        )

                        download_page = APKmirror().get_download_page(url=page)

                        href = APKmirror().extract_download_link(download_page)

                        filename = f"{app_reference[app_name]['name']}-{version}.apk"

                        return self._download(href, filename)

            if not hasversion:
                data = APKmirror().apkmirror_get_latest_version_download_page(
                    app_name=app_name
                )

                href = APKmirror().extract_download_link(data["url"])

                filename = f"{app_reference[app_name]['name']}-{data['version']}.apk"

                return self._download(href, filename)
