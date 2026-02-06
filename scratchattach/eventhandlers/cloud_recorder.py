"""CloudRecorder class (used by ScratchCloud, TwCloud and other classes inheriting from BaseCloud to deliver cloud var values)"""
from __future__ import annotations

from typing import Optional, Any
from threading import Event

from .cloud_events import CloudEvents


class CloudRecorder(CloudEvents):
    has_data: Event
    cloud_values: dict[str, Any]
    def __init__(self, cloud, *, initial_values: Optional[dict[str, Any]] = None):
        self.has_data = Event()
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
        return self.cloud_values

    def on_set(self, activity):
        # print(f"{activity=}")
        if not self.has_data.is_set():
            self.has_data.set()
        self.cloud_values[activity.var] = activity.value
