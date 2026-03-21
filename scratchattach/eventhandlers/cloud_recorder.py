"""CloudRecorder class (used by ScratchCloud, TwCloud and other classes inheriting from BaseCloud to deliver cloud var values)"""
from __future__ import annotations

from typing import Optional, Any
from threading import Event

from scratchattach.site import cloud_activity

from .cloud_events import CloudEvents


class CloudRecorder(CloudEvents):
    has_data: Event
    received_data: Event
    cloud_values: dict[str, Any]
    def __init__(self, cloud, *, initial_values: Optional[dict[str, Any]] = None):
        self.has_data = Event()
        self.received_data = Event()
        initial_values = initial_values or {}

        super().__init__(cloud)
        self.cloud_values = initial_values
        if self.cloud_values:
            self.has_data.set()
        self.event(self.on_set)

    def get_var(self, var):
        if var not in self.cloud_values:
            return None
        return self.cloud_values[var]

    def get_all_vars(self):
        return self.cloud_values.copy()

    def on_set(self, activity: cloud_activity.CloudActivity):
        # print(f"{activity=}")
        if not self.has_data.is_set():
            self.has_data.set()
        if not self.received_data.is_set():
            self.received_data.set()
        self.cloud_values[activity.actual_var] = activity.value
