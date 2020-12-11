import json


class ConfigurationHandler(object):
    def __init__(self):
        self.data = json.load(open("Utility/config.json"))

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
        with open("Utility/config.yaml", "w") as file:
            file.write(json.dumps(self.data, indent=2))
