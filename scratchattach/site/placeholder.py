# Classes and methods for interacting with turbowarp placeholder (https://share.turbowarp.org/)
import re
import json
import bs4

from dataclasses import dataclass
from typing_extensions import Optional
from bs4 import BeautifulSoup

from scratchattach.site import session
from scratchattach.utils.requests import requests
from scratchattach import editor

@dataclass
class PlaceholderProject:
    id: str

    title: Optional[str] = None
    description: Optional[str] = None
    md5exts_to_sha256: Optional[dict[str, str]] = None

    _session: Optional[session.Session] = None

    def get_json(self):
        with requests.no_error_handling():
            return requests.get(f"https://share.turbowarp.org/api/projects/{self.id}").json()

    def update_by_html(self):
        """
        Scrape JS to update the project. Hopefully this will not be necessary in the future, as it is very error-prone.
        """

        with requests.no_error_handling():
            resp = requests.get(f"https://share.turbowarp.org/projects/{self.id}")
            soup = BeautifulSoup(resp.text, "html.parser")

            for script in soup.find_all("script"):
                if not isinstance(script, bs4.element.Tag):
                    continue

                if raw_data := re.search("const data = \\[.*\"data\":{metadata:{.*},md5extsToSha256:.*];", str(script.contents[0])):
                    data = raw_data.group().removeprefix("const data = ").removesuffix(";")
                    # this data is NOT json. Therefore, we can't just JSON.parse it.
                    # it's actually native JavaScript, but we can extract the information in a really flimsy way using regex
                    # This flimsy method would probably break with bad input, so maybe, instead, a request should be made to GarboMuffin.
                    # If you want full JS support, use an automated browser.
                    print(data)

                    # get title
                    pf, sf = 'metadata:{title:"', '",description'
                    if group := re.search(pf+'.*?'+sf, data).group():
                        self.title = json.loads('"' + group.removeprefix(pf).removesuffix(sf) + '"')

                    # Get description. It is probably very easy to break this regex
                    pf, sf = 'description:"', '"},'
                    if group := re.search(pf+'.*?'+sf, data).group():
                        self.description = json.loads('"' + group.removeprefix(pf).removesuffix(sf) + '"')

                    pf, sf = 'md5extsToSha256:{', '},'
                    if group := re.search(pf+'.*?'+sf, data).group():
                        self.md5exts_to_sha256 = json.loads('{' + group.removeprefix(pf).removesuffix(sf) + '}')

                    break

    def get_project_body(self):
        data = self.get_json()
        body = editor.Project.from_json(data)

        for asset in body.assets:
            print(asset.md5ext)

        return body


def get_placeholder_project(_id: str):
    return PlaceholderProject(_id)

if __name__ == '__main__':
    p = get_placeholder_project("44c35afc-fe00-49d8-afe7-d71f4430c121")
    p.update_by_html()
    print(p)
