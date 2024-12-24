"""CloudStorage class"""
from __future__ import annotations

from .cloud_requests import CloudRequests
import json
import time
from threading import Thread

class Database:

    """
    A Database is a simple key-value storage that stores data in a JSON file saved locally (other database services like MongoDB can be implemented)
    """

    def __init__(self, name, *, json_file_path, save_interval=30):
        self.save_event_function = None
        self.set_event_function = None
        self.name = name

        # Import from JSON file
        if not json_file_path.endswith(".json"):
            json_file_path = json_file_path+".json"
        self.json_file_path = json_file_path

        try:
            with open(json_file_path, 'r') as json_file:
                self.data = json.load(json_file)
        except FileNotFoundError:
            print(f"Creating file {json_file_path}. Your database {name} will be stored there.")
            self.data = {}
            self.save_to_json()
        
        if isinstance(self.data , list):
            raise ValueError(
                "Invalid JSON file content: Top-level object must be a dict, not a list"
            )
        
        # Start autosaving
        self.save_interval = save_interval
        if self.save_interval is not None:
            Thread(target=self._autosaver).start()

    def save_to_json(self):
        with open(self.json_file_path, 'w') as json_file:
            json.dump(self.data, json_file, indent=4)
        
        if self.save_event_function is not None:
            self.save_event_function()
    
    def keys(self) -> list:
        return list(self.data.keys())

    def get(self, key) -> str:
        if not key in self.data:
            return None
        return self.data[key]
    
    def set(self, key, value):
        self.data[key] = value

        if self.set_event_function is not None:
            self.set_event_function(key, value)

    def event(self, event_function):
        # Decorator function for adding the on_save event that is called when a save is performed
        if event_function.__name__ == "on_save":
            self.save_event_function = event_function
        if event_function.__name__ == "on_set":
            self.set_event_function = event_function
        
    def _autosaver(self):
        # Task autosaving the db. save interval specified in .save_interval attribute
        while True:
            time.sleep(self.save_interval)
            self.save_to_json()

class CloudStorage(CloudRequests):
    
    """
    A CloudStorage object saves multiple databases and allows the connected Scratch project to access and modify the data of these databases through cloud requests

    The CloudStorage class is built upon CloudRequests
    """

    def __init__(self, cloud, used_cloud_vars=["1", "2", "3", "4", "5", "6", "7", "8", "9"], no_packet_loss=False):
        super().__init__(cloud, used_cloud_vars=used_cloud_vars, no_packet_loss=no_packet_loss)
        # Setup
        self._databases = {}
        self.request(self.get, thread=False)
        self.request(self.set, thread=False)
        self.request(self.keys, thread=False)
        self.request(self.database_names, thread=False)
        self.request(self.ping, thread=False)

    def ping(self):
        return "Database backend is running"
    
    def get(self, db_name, key) -> str:
        try:
            return self.get_database(db_name).get(key)
        except Exception:
            if self.get_database(db_name) is None:
                return f"Error: Database {db_name} doesn't exist"
            else:
                return f"Error: Key {key} doesn't exist in database {db_name}"

    def set(self, db_name, key, value):
        print(db_name, key, value, self._databases)
        return self.get_database(db_name).set(key, value)

    def keys(self, db_name) -> list:
        try:
            return self.get_database(db_name).keys()
        except Exception:
            return f"Error: Database {db_name} doesn't exist"

    def databases(self) -> list:
        return list(self._databases.values())

    def database_names(self) -> list:
        return list(self._databases.keys())
    
    def add_database(self, database:Database):
        self._databases[database.name] = database

    def get_database(self, name) -> Database:
        if name in self._databases:
            return self._databases[name]
        return None

    def save(self):
        """
        Saves the data in the JSON files for all databases in self._databases
        """
        for dbname in self._databases:
            self._databases[dbname].save_to_json()