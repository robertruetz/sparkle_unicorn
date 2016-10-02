from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import json
import uuid


class CityData(object):

    def __init__(self, name, latitude, longitude, concepts, hotels):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.concepts = concepts
        self.hotels = hotels


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