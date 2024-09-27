"""v2 ready: CloudEvents class"""

from ..cloud import cloud
from ._base import BaseEventHandler
from ..site import activity
import time
import json

class CloudEvents(BaseEventHandler):
    """
    Class that calls events when on cloud updates that are received through a websocket connection.
    """
    def __init__(self, cloud):
        super().__init__()
        self.cloud = cloud
        self.source_cloud = type(cloud)(project_id=cloud.project_id, _session=cloud._session)
        self.source_cloud.ws_timeout = None # No timeout -> allows continous listening

    def _update(self):
        self.source_cloud.connect()
        
        self.call_event("on_ready")

        while True:
            if self.running is False:
                return
            try:
                data = self.source_cloud.websocket.recv().split('\n')
                result = []
                for i in data:
                    try:
                        _a = activity.CloudActivity()
                        _a._update_from_dict(json.loads(i))
                        if "on_"+_a.type in self._events:
                            self.call_event("on_"+_a.type, [_a])
                    except Exception as e:
                        print("DEBUG cloud events parse error", e)
                        pass
            except Exception:
                time.sleep(0.1) # cooldown
                self.source_cloud.connect()

class CloudLogEvents(BaseEventHandler):
    """
    Class that calls events on cloud updates that are received from a clouddata log.
    """
    def __init__(self, cloud, *, update_interval=0.1):
        super().__init__()
        if not hasattr(cloud, "logs"):
            raise ValueError("Cloud log events can't be used with a cloud that has no logs available")
        self.cloud = cloud
        self.source_cloud = cloud
        self.update_interval = update_interval

    def _update(self):
        self.old_data = self.source_cloud.logs(limit=25)

        self.call_event("on_ready")

        while True:
            if self.running is False:
                return
            try:
                data = self.source_cloud.logs(limit=25)
                if data != self.old_data:
                    for _a in data:
                        if _a in self.old_data:
                            break
                        if "on_"+_a.type in self._events:
                            self.call_event("on_"+_a.type, [_a])
                self.old_data = data
            except Exception:
                time.sleep(0.1) # cooldown
                self.source_cloud.connect()
            time.sleep(self.update_interval)


