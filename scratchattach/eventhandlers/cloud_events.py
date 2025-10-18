"""CloudEvents class"""
from __future__ import annotations

import traceback

from scratchattach.cloud import _base
from ._base import BaseEventHandler
from scratchattach.utils import exceptions
from scratchattach.site import cloud_activity
import time
import json
from collections.abc import Iterator

class CloudEvents(BaseEventHandler):
    """
    Class that calls events when on cloud updates that are received through a websocket connection.
    """
    def __init__(self, cloud: _base.AnyCloud):
        super().__init__()
        self.cloud = cloud
        self._session = cloud._session
        self.source_stream = cloud.create_event_stream()
        self.startup_time = time.time() * 1000

    def disconnect(self):
        self.source_stream.close()

    def _updater(self):
        """
        A process that listens for cloud activity and executes events on cloud activity
        """
        
        self.call_event("on_ready")

        if self.running is False:
            return
        
        # TODO: refactor this method. It works, but is hard to read
        while True:
            try:
                while True:
                    # print("Checking for more events")
                    for data in self.source_stream.read():
                        # print(f"Got event {data}")
                        subsequent_reconnects = 0
                        try:
                            _a = cloud_activity.CloudActivity(timestamp=time.time()*1000, _session=self._session, cloud=self.cloud)
                            if _a.timestamp < self.startup_time + 500: # catch the on_connect message sent by TurboWarp's (and sometimes Scratch's) cloud server
                                # print(f"Skipped as {_a.timestamp} < {self.startup_time + 500}")
                                continue
                            data["variable_name"] = data["name"]
                            data["name"] = data["variable_name"].replace("☁ ", "")
                            _a._update_from_dict(data)
                            # print(f"sending event {_a}")
                            self.call_event("on_"+_a.type, [_a])
                        except Exception as e:
                            print(f"Cloud events _updated ignored: {e} {traceback.format_exc()}")
                            pass
            except Exception:
                self.subsequent_reconnects += 1
                time.sleep(0.1) # cooldown

            if subsequent_reconnects >= 5:
                print(f"Warning: {subsequent_reconnects} subsequent cloud disconnects. Cloud may be down, causing CloudEvents to not call events.")
            self.call_event("on_reconnect", [])

class ManualCloudLogEvents:
    """
    Class that calls events on cloud updates that are received from a clouddata log.
    """
    def __init__(self, cloud: _base.LogCloud):
        if not isinstance(cloud, _base.LogCloud):
            raise ValueError("Cloud log events can't be used with a cloud that has no logs available")
        self.cloud = cloud
        self.source_cloud = cloud
        self._session = cloud._session
        self.last_timestamp = 0
        self.subsequent_failed_log_fetches = 0

    def update(self) -> Iterator[tuple[str, list[cloud_activity.CloudActivity]]]:
        """
        Update once and yield all packets
        """
        try:
            data = self.source_cloud.logs(limit=25)
            self.subsequent_failed_log_fetches = 0
            for _a in data[::-1]:
                if _a.timestamp <= self.last_timestamp:
                    continue
                self.last_timestamp = _a.timestamp
                yield ("on_"+_a.type, [_a])
        except Exception:
            self.subsequent_failed_log_fetches += 1
            if self.subsequent_failed_log_fetches == 20:
                print("Warning: 20 subsequent clouddata log fetches failed. Scrach's cloud logs may be down, causing CloudLogEvents to not call events.")
        
class CloudLogEvents(BaseEventHandler):
    """
    Class that calls events on cloud updates that are received from a clouddata log.
    """
    def __init__(self, cloud: _base.LogCloud, *, update_interval=0.1):
        super().__init__()
        if not isinstance(cloud, _base.LogCloud):
            raise ValueError("Cloud log events can't be used with a cloud that has no logs available")
        self.cloud = cloud
        self.source_cloud = cloud
        self.update_interval = update_interval
        self._session = cloud._session
        self.last_timestamp = 0
        self.manual_cloud_log_events = ManualCloudLogEvents(cloud)

    def _updater(self):
        try:
            logs = self.source_cloud.logs(limit=25)
        except exceptions.FetchError:
            logs = []

        self.last_timestamp = 0
        if len(logs) != 0:
            self.last_timestamp = logs[0].timestamp

        self.call_event("on_ready")

        while True:
            if self.running is False:
                return
            for event_type, event_data in self.manual_cloud_log_events.update():
                self.call_event(event_type, event_data)
            time.sleep(self.update_interval)
