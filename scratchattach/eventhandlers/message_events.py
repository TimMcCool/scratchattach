"""MessageEvents class"""
from __future__ import annotations

from ..site import user
from ._base import BaseEventHandler
import time

class MessageEvents(BaseEventHandler):
    """
    Class that calls events when you receive messages on your Scratch account. Data fetched from Scratch's API.
    """
    def __init__(self, user, *, update_interval=2):
        super().__init__()
        self.user = user
        self.current_message_count = 0
        self.update_interval = update_interval

    def _updater(self):
        """
        A process that listens for cloud activity and executes events on cloud activity
        """
        self.current_message_count = int(self.user.message_count())
        
        self.call_event("on_ready")

        while True:
            if self.running is False:
                return
            message_count = int(self.user.message_count())
            if message_count != self.current_message_count:
                self.call_event("on_count_change", [int(self.current_message_count), int(message_count)])
                if message_count != 0:
                    if message_count < self.current_message_count:
                        self.current_message_count = 0
                    if self.user._session is not None: # authentication check
                        if self.user._session.username == self.user.username: # authorization check
                            new_messages = self.user._session.messages(limit=message_count-self.current_message_count)
                            for message in new_messages[::-1]:
                                self.call_event("on_message", [message])
                self.current_message_count = int(message_count)
            time.sleep(self.update_interval)
            