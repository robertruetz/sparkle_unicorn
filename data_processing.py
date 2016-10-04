import json
import os
import main
import utils
import models
import sys


DATAFILEPATH = r"./files/data_file_us_cities.yml"


def load_article_data_from_yaml(yaml_path):
    y_file = utils.load_yaml_data(yaml_path)
    article_list = []
    count = 0
    for article in y_file:
        article_list.append(models.Article(article.get("linkOut"), article.get("image"), article.get("destination"),
                                           article.get("displayName"), article.get("concepts"), article.get("text"), count))
        count += 1
    return article_list

#
#
# def load_imgTiles_from_yaml(yaml_path):
#     y_file = load_yaml_data(yaml_path)
#     image_list = {}
#     imgs = y_file.get("images", None)
#     if imgs is None:
#         raise Exception
#     for img in imgs:
#         n_image = models.imageTile(img["url"], img["cities"], img["tags"])
#         image_list[n_image.id] = n_image
#     return image_list


def backload_us_city_data():
    with open(os.path.abspath("./files/top_cities_us.txt"), 'r') as file:
        j = json.load(file)
        short_list = j[:200]
        cities = []
        for item in short_list:
            city = item["city"].replace(' ', '_')
            cities.append(city)
    print(get_data_for_all_cities_in_list(cities))


def get_data_for_all_cities_in_list(cities_list):
    city_errors = []
    city_dict = {}
    for city in cities_list:
        response = main.get_destination(city)
        if response.status_code != 200:
            city_errors.append(city)
        else:
            city_dict[city] = response.json()
    with open(os.path.abspath(DATAFILEPATH), 'a') as f:
        f.write(json.dumps(city_dict))
    return city_errors


if __name__ == "__main__":
    if sys.argv[1] == "loadArticles":
        load_article_data_from_yaml(r"./files/article_data.yml")
    elif sys.argv[1] == "loadCityData":
        backload_us_city_data()
