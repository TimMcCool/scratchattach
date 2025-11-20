# Classes and methods for interacting with turbowarp placeholder (https://share.turbowarp.org/)
import re
import bs4
import json
import io

from dataclasses import dataclass
from typing_extensions import Optional
from bs4 import BeautifulSoup

from scratchattach.site import session
from scratchattach.site.typed_dicts import PlaceholderProjectDataDict
from scratchattach.utils.requests import requests
from scratchattach import editor
from scratchattach.utils import commons


@dataclass
class PlaceholderProject:
    id: str

    title: Optional[str] = None
    description: Optional[str] = None
    md5exts_to_sha256: Optional[dict[str, str]] = None
    admin_ownership_token: Optional[str] = None  # guessing it's a str

    _session: Optional[session.Session] = None

    def get_json(self):
        with requests.no_error_handling():
            return requests.get(f"https://share.turbowarp.org/api/projects/{self.id}").json()

    def update_by_html(self) -> None:
        """
        Scrape JS to update the project. Requires hjson
        """
        try:
            import hjson  # type: ignore
        except ImportError as e:
            raise ImportError("Please use pip install hjson if you want to use placeholder projects!") from e

        with requests.no_error_handling():
            resp = requests.get(f"https://share.turbowarp.org/projects/{self.id}")
            soup = BeautifulSoup(resp.text, "html.parser")

            for script in soup.find_all("script"):
                if not isinstance(script, bs4.element.Tag):
                    continue

                if raw_data := re.search("const data = \\[.*\"data\":{metadata:{.*},md5extsToSha256:.*];",
                                         str(script.contents[0])):
                    data = raw_data.group().removeprefix("const data = ").removesuffix(";")
                    # this data is NOT json. Therefore, we can't just JSON.parse it.
                    # it's actually native JavaScript, but we can extract the information in a relatively stable way using hjson
                    # maybe, instead, a request should be made to GarboMuffin.
                    data = hjson.loads(data)
                    # i am unsure if the other data here is of any use. It may be artifacts coming from svelte
                    parsed_data: PlaceholderProjectDataDict = data[1]["data"]

                    self.title = parsed_data["metadata"]["title"]
                    self.description = parsed_data["metadata"]["description"]
                    self.md5exts_to_sha256 = dict(parsed_data["md5extsToSha256"])
                    self.admin_ownership_token = parsed_data["adminOwnershipToken"]

                    break

    def get_project_body(self):
        self.update_by_html()

        data = self.get_json()
        body = editor.Project.from_json(data)
        body.name = self.title

        for asset in body.assets:
            table = self.md5exts_to_sha256
            assert table is not None # this should never happen
            data = get_asset(table[asset.md5ext])
            asset.asset_file.data = data

        return body


def get_asset(sha256: str) -> bytes:
    with requests.no_error_handling():
        return requests.get(f"https://share.turbowarp.org/api/assets/{sha256}").content

def get_placeholder_project(_id: str):
    return PlaceholderProject(_id)

def create_placeholder_project(title: str, data: bytes):
    body = editor.Project.from_sb3(data)

    asset_information: dict[str, dict[str, str | int]] = {}
    for asset in body.assets:
        print(asset)
        print(asset.asset_file.sha256)
        asset_information[asset.md5ext] = {
            "sha256": asset.asset_file.sha256,
            "size": len(asset.asset_file.data)
        }

    print(f"{asset_information = }")
    print(f"{body.name = }")
    with requests.no_error_handling():
        resp = requests.post("https://share.turbowarp.org/api/projects/new", data={
            "title": title,
            "assetInformation": asset_information,
        }, files={
                          "project": ("blob", data, 'application/octet-stream'), 
                             }, headers={
                             'accept': '*/*',
                             'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
                             # 'content-type': 'multipart/form-data; boundary=----WebKitFormBoundaryYzpNqB5A2GEr99Vd',
                             'dnt': '1',
                             'origin': 'https://share.turbowarp.org',
                             'priority': 'u=1, i',
                             'referer': 'https://share.turbowarp.org/',
                             'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
                             'sec-ch-ua-mobile': '?0',
                             'sec-ch-ua-platform': '"Windows"',
                             'sec-fetch-dest': 'empty',
                             'sec-fetch-mode': 'cors',
                             'sec-fetch-site': 'same-origin',
                             'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
                             })

    print(resp, resp.content)

if __name__ == '__main__':
    p = get_placeholder_project("44c35afc-fe00-49d8-afe7-d71f4430c121")
    pb = p.get_project_body()
    pb.export("test plac.sb3")
