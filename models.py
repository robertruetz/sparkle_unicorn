from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class CityData(object):

    def __init__(self, name, latitude, longitude, concepts, hotels):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.concepts = concepts
        self.hotels = hotels

