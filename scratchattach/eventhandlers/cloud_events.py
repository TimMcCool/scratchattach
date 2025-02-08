"""CloudEvents class"""
from __future__ import annotations

from ..cloud import _base
from ._base import BaseEventHandler
from ..site import cloud_activity
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
        while True:
            try:
                while True:
                    for data in self.source_stream.read():
                        try:
                            _a = cloud_activity.CloudActivity(timestamp=time.time()*1000, _session=self._session, cloud=self.cloud)
                            if _a.timestamp < self.startup_time + 500: # catch the on_connect message sent by TurboWarp's (and sometimes Scratch's) cloud server
                                continue
                            data["variable_name"] = data["name"]
                            data["name"] = data["variable_name"].replace("☁ ", "")
                            _a._update_from_dict(data)
                            self.call_event("on_"+_a.type, [_a])
                        except Exception as e:
                            pass
            except Exception:
                print("CloudEvents: Disconnected. Reconnecting ...", time.time())
                time.sleep(0.1) # cooldown

            print("CloudEvents: Reconnected.", time.time())
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
    
    def update(self) -> Iterator[tuple[str, list[cloud_activity.CloudActivity]]]:
        """
        Update once and yield all packets
        """
        try:
            data = self.source_cloud.logs(limit=25)
            for _a in data[::-1]:
                if _a.timestamp <= self.last_timestamp:
                    continue
                self.last_timestamp = _a.timestamp
                yield ("on_"+_a.type, [_a])
        except Exception:
            pass
        

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
        logs = self.source_cloud.logs(limit=25)
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
