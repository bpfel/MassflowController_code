import json
from GUI.Utils import resource_path


class ConfigurationHandler(object):
    def __init__(self):
        self.data = json.load(open(resource_path("..\\Utility\\config.json")))

    def __getitem__(self, item):
        if type(item) == str:
            return self.data[item]
        else:
            raise KeyError("Key has to be of type string!")

    def __setitem__(self, key, value):
        if type(key) == str:
            self.data[key] = value
        else:
            raise KeyError("Key has to be of type string!")

    def write(self):
        with open(resource_path("..\\Utility\\config.json"), "w") as file:
            file.write(json.dumps(self.data, indent=2))
