"""v2 ready: CloudEvents class"""

from ..cloud import cloud
from ._base import BaseEventHandler
from ..site import cloud_activity
import time
import json
from threading import Thread

class CloudEvents(BaseEventHandler):
    """
    Class that calls events when on cloud updates that are received through a websocket connection.
    """
    def __init__(self, cloud):
        super().__init__()
        self.cloud = cloud
        self._session = cloud._session
        self.source_cloud = type(cloud)(project_id=cloud.project_id, _session=cloud._session)
        self.source_cloud.ws_timeout = None # No timeout -> allows continous listening
        self.startup_time = time.time() * 1000

    def _updater(self):
        """
        A process that listens for cloud activity and executes events on cloud activity
        """
        self.source_cloud.connect()
        
        Thread(target=self.call_event, args=["on_ready"]).start()

        while True:
            if self.running is False:
                return
            try:
                data = self.source_cloud.websocket.recv().split('\n')   
                result = []
                for i in data:
                    try:
                        _a = cloud_activity.CloudActivity(timestamp=time.time()*1000, _session=self._session)
                        if _a.timestamp < self.startup_time + 500: # catch the on_connect message sent by TurboWarp's (and sometimes Scratch's) cloud server
                            continue
                        data = json.loads(i)
                        data["name"] = data["name"].replace("☁ ", "")
                        _a._update_from_dict(data)
                        self.call_event("on_"+_a.type, [_a])
                    except Exception as e:
                        pass
            except Exception:
                time.sleep(0.1) # cooldown
                self.source_cloud.connect()
                self.call_event("on_reconnect", [])


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
        self._session = cloud._session

    def _updater(self):
        self.old_data = self.source_cloud.logs(limit=25)

        self.call_event("on_ready")

        while True:
            if self.running is False:
                return
            try:
                data = self.source_cloud.logs(limit=25)
                for _a in data:
                    if _a.timestamp < self.startup_time:
                        continue
                    if _a in self.old_data:
                        break
                    self.call_event("on_"+_a.type, [_a])
                self.old_data = data
            except Exception:
                pass
            time.sleep(self.update_interval)


