"""v2 ready: CloudStorage class"""

from .cloud_requests import CloudRequests
import json

class Database:

    """
    A Database is a simple key-value storage that stores data in a JSON file saved locally (other database services like MongoDB can be implemented)
    """

    def __init__(self, name, *, json_file_path, save_interval=30):
        # Import from JSON file
        if not json_file_path.endswith(".json"):
            json_file_path = json_file_path+".json"
        self.json_file_path = json_file_path

        try:
            with open(json_file_path, 'r') as json_file:
                self.data = json.load(json_file_path)
        except FileNotFoundError:
            print(f"Creating file {json_file_path}. Your database {name} will be stored there.")
            self.data = []
            self.save_to_json()
        
        if isinstance(self.data , list):
            raise ValueError(
                "Invalid JSON file content: Top-level object must be a dict, not a list"
            )
    
        # Other initialization
        self.save_event_function = None
    
    def save_to_json(self):
        with open(self.json_file_path, 'w') as json_file:
            json.dump(self.data, json_file, indent=4)
        
        if self.save_event_function is not None:
            self.save_event_function()
    
    def keys(self) -> list:
        return list(self.data.keys())

    def get(self, key) -> str:
        return self.data[key]
    
    def set(self, key, value):
        self.data[key] = value
    
    def event(self, event_function):
        # Decorator function for adding the on_save event that is called when a save is performed
        if event_function.__name__ == "on_save":
            self.save_event_function = event_function

class CloudStorage(CloudRequests):
    
    """
    A CloudStorage object saves multiple databases and allows the connected Scratch project to access and modify the data of these databases through cloud requests

    The CloudStorage class is built upon CloudRequests
    """

    def __init__(self, cloud, used_cloud_vars=["1", "2", "3", "4", "5", "6", "7", "8", "9"], no_packet_loss=False):
        super().__init__(cloud, used_cloud_vars=used_cloud_vars, no_packet_loss=no_packet_loss)
        # Setup
        self._databases = {}
        self.request(self.get, thread=True)
        self.request(self.set, thread=True)
        self.request(self.keys, thread=True)
        self.request(self.database_names, thread=True)
    
    def get(self, db_name, key) -> str:
        return self.get_database(db_name).get(key)

    def set(self, db_name, key, value):
        return self.get_database(db_name).set(key, value)

    def keys(self, db_name) -> list:
        return self.get_database(db_name).keys()

    def databases(self) -> list:
        return list(self._databases.values())

    def database_names(self) -> list:
        return list(self._databases.keys())
    
    def add_database(self, database:Database):
        self._databases[database.name] = database

    def get_database(self, name) -> Database:
        return self._databases[name]