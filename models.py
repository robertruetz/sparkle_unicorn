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


class Article(object):

    def __init__(self, linkOut, image, destination, displayName, concepts, text, id=None):
        self.id = id if id is not None else uuid.uuid4()
        self.linkOut = linkOut
        self.image = image
        self.destination = destination
        self.displayName = displayName
        self.concepts = concepts
        self.text = text

    def to_entrypoint_response(self):
        stuff = {}
        for k, v in self.__dict__.items():
            if not k.startswith("__") and "concepts" not in k:
                stuff[k] = str(v)
        return stuff

    def __str__(self):
        stuff = {}
        for k, v in self.__dict__.items():
            if not k.startswith("__"):
                stuff[k] = str(v)
        encoder = json.JSONEncoder()
        return encoder.encode(stuff)


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


class Hotel(object):

    def __init__(self, name, urls, address):
        self.name = name
        self.urls = urls
        self.address = address


class Destination(object):

    def __init__(self, city, state, country, hotels):
        self.city = city
        self.state = state
        self.country = country
        self.hotels = hotels
