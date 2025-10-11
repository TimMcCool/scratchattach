# Classes and methods for interacting with turbowarp placeholder (https://share.turbowarp.org/)
import re
import bs4

from dataclasses import dataclass
from typing_extensions import Optional
from bs4 import BeautifulSoup

from scratchattach.site import session
from scratchattach.site.typed_dicts import PlaceholderProjectDataDict
from scratchattach.utils.requests import requests
from scratchattach import editor


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
            data = get_asset(self.md5exts_to_sha256[asset.md5ext])
            asset.asset_file.data = data

        return body


def get_asset(sha256: str):
    with requests.no_error_handling():
        return requests.get(f"https://share.turbowarp.org/api/assets/{sha256}").content


def get_placeholder_project(_id: str):
    return PlaceholderProject(_id)


if __name__ == '__main__':
    p = get_placeholder_project("44c35afc-fe00-49d8-afe7-d71f4430c121")
    pb = p.get_project_body()
    pb.export("test plac.sb3")
