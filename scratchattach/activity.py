"""v2 ready: Activity class"""

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

class Activity(AbstractScratch):

    '''
    Represents a Scratch activity (message or other user page activity)
    '''

    def str(self):
        return str(self.raw)

    def __init__(self, **entries):

        # Set attributes every Activity object needs to have:
        self.raw = None
        self._session = None

        # Update attributes from entries dict:
        self.__dict__.update(entries)
    
    def update():
        return False # Objects of this type cannot be update
    
    def _update_from_dict(self, data):
        self.__dict__.update(data)
        return True
    
    def _update_from_html(self, data):
                
        time=data.find('div').find('span').findNext().findNext().text.strip()
            
        if '\xa0' in time:
            while '\xa0' in time: time=time.replace('\xa0', ' ')
        
        self.time = time
        self.actor_username=(data.find('div').find('span').text)
            
        self.type=data.find('div').find_all('span')[0].next_sibling.strip()
        if self.type == "loved":
            self.type = "loveproject"
        if self.type == "favorited":
            self.type = "favoriteproject"
        if "curator" in self.type:
            self.type = "becomecurator"
        if "shared" in self.type:
            self.type = "shareproject"

        self.target=(data.find('div').find('span').findNext().text)
                    
        return True

    def actor(self):
        """
        Returns the user that performed the activity as User object
        """
        _user = user.User(_session = self._session, username=self.actor_username)
        try:
            _user.update()
        except Exception:
            raise(exceptions.FetchError)
        return _user



