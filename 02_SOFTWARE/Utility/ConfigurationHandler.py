from yaml import load, dump, CLoader as Loader, CDumper as Dumper


class ConfigurationHandler(object):
    def __init__(self):
        self.data = load(open("Utility/config.yaml"), Loader=Loader)

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
            file.write(dump(self.data, Dumper=Dumper))
