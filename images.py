import json
import uuid


class imageTile(object):

    def __init__(self, url, cities, tags):
        self.url = url
        self.cities = cities
        self.tags = tags
        self.id = str(uuid.uuid4())

    def __str__(self):
        stuff = {}
        for k, v in self.__dict__.items():
            if not k.startswith("__"):
                stuff[k] = v
        encoder = json.JSONEncoder()
        return encoder.encode(stuff)
