"""v2 ready: CloudRecorder class (used by ScratchCloud, TwCloud and other classes inheriting from BaseCloud to deliver cloud var values)"""

from .cloud_events import CloudEvents

class CloudRecorder(CloudEvents):

    def __init__(self, cloud, *, initial_values={}):
        super().__init__(cloud)
        self.cloud_values = initial_values
        self.event(self.on_set)

    def get_var(self, var):
        if not var in self.cloud_values:
            return None
        return self.cloud_values[var]
    
    def get_all_vars(self):
        return self.cloud_values
    
    def on_set(self, activity):
        self.cloud_values[activity.var] = activity.value
