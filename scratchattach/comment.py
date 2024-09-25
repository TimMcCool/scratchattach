"""v2 WIP: Comment class"""

import json
import re
import requests

from . import user
from . import session
from . import project
from . import studio
from . import forum
from . import exceptions
from .abstractscratch import AbstractScratch
from .commons import headers
from bs4 import BeautifulSoup

class Comment(AbstractScratch):

    '''
    Represents a Scratch comment (on a profile, studio or project)
    '''

    def str(self):
        return str(self.content)

    def __init__(self, **entries):
        
        # Set attributes every Comment object needs to have:
        self.id = None
        self._session = None
        self.source_id = None
        self.cached_replies = []
        if not "source" in entries:
            "source" == "Unknown"

        # Update attributes from entries dict:
        self.__dict__.update(entries)
    
    def _update_from_dict(self, data):
        try: self.id = data["id"]
        except Exception: pass
        try: self.parent_id = data["parent_id"]
        except Exception: pass
        try: self.commentee_id = data["commentee_id"]
        except Exception: pass
        try: self.content = data["content"]
        except Exception: pass
        try: self.datetime_created = data["datetime_created"]
        except Exception: pass
        try: self.author_name = data["author"]["username"]
        except Exception: pass
        try: self.author_id = data["author"]["id"]
        except Exception: pass
        try: self.written_by_scratchteam = data["author"]["scratchteam"]
        except Exception: pass
        try: self.reply_count = data["reply_count"]
        except Exception: pass
