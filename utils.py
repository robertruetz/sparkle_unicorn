import datetime
import yaml
import os
import images
import json
import models


def get_date_today_string(year_offset=None):
    """
    return a properly formatted date string including a year offset if given
    """
    now = datetime.date.today()
    if year_offset is not None:
        now = now.replace(year=now.year + year_offset)
    return now.strftime("%Y-%m-%d")


def load_imgTiles_from_yaml(yaml_path):
    y_file = load_yaml_data(yaml_path)
    image_list = {}
    imgs = y_file.get("images", None)
    if imgs is None:
        raise Exception
    for img in imgs:
        n_image = images.imageTile(img["url"], img["cities"], img["tags"])
        image_list[n_image.id] = n_image
    return image_list


def load_cached_city_data(cache_file_path):
    cities_dict = {}
    with open(os.path.abspath(cache_file_path), 'r') as f:
        for line in f:
            j = json.loads(line)
            for city, data in j.items():
                cities_dict[city] = models.CityData(city, data.get("latitude"), data.get("longitude"),
                                                    data.get("concepts"), data.get("hotels"))
    return cities_dict


def load_yaml_data(yaml_path):
    if not os.path.exists(os.path.abspath(yaml_path)):
        raise Exception
    y_file = None
    with open(os.path.abspath(yaml_path), 'r') as stream:
        try:
            y_file = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return y_file


def get_distinct_cities(img_tiles_dict):
    cities = []
    for k, v in img_tiles_dict.items():
        for c in v.cities:
            city = c.split(',')[0].replace(' ', '_').strip()
            cities.append(city)
    return set(cities)


