from flask import Flask, request, send_from_directory
import requests
import json
import utils
import models
import os
from jinja2 import Template, Environment, FileSystemLoader


app = Flask(__name__, static_url_path='/static')

BASE_URL = "https://api.wayblazer.com/v1/"
APIKEY = "PEZlargze3A0nyPTBfkP1kQcUw2227Ix"
HEADERBASE = {"content-type": "application/json", "x-api-key": APIKEY}
YAMLPATH = r"./files/images_cities.yml"
IMAGETILES = utils.load_imgTiles_from_yaml(YAMLPATH)

ARTICLEPATH = r"./files/blogpost.yml"
ARTICLES = utils.load_article_data_from_yaml(ARTICLEPATH)   # Dictionary of id: article obj

DISTINCTCITIES = utils.get_distinct_cities(ARTICLES)

DATAFILEPATH = r"./files/data_file.yml"
CITYDATACACHE = utils.load_cached_city_data(DATAFILEPATH)

template_env = Environment(loader=FileSystemLoader('./static'))


def main():

    # Code below is only necessary for backloading data
    # error_list = []
    # if not os.path.exists(DATAFILEPATH):
    #     error_list = get_data_for_all_cities_in_list(DISTINCTCITIES)
    # else:
    #     CITYDATACACHE = utils.load_cached_city_data(DATAFILEPATH)
    # if len(error_list) > 0:
    #     print("Could not load data for {0}".format(error_list))
    # ---------

    app.run()

# region Routes

@app.route('/')
def index_page():
    article_list = []
    for id, article in ARTICLES.items():
        article_list.append(article.to_entrypoint_response())

    template = template_env.get_template('index.html')
    return template.render(article_list=json.dumps(article_list))

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('static/css', path)

@app.route('/img/<path:path>')
def send_img(path):
    return send_from_directory('static/img', path)

@app.route('/fonts/<path:path>')
def send_font(path):
    return send_from_directory('static/font', path)


@app.route('/reload/<thing>')
def reload_thing(thing):
    global ARTICLES
    if thing == "articles":
        ARTICLES = utils.load_article_data_from_yaml(ARTICLEPATH)
    return json.dumps({"status_code": "200", "message": "{0} reloaded.".format(thing)})


@app.route('/filter', methods=["POST"])
def filter_route():
    data = request.json
    ids = data.get("ids", None)
    print(ids)
    if ids is None:
        raise Exception
    cities = []
    for i in ids:
        article = ARTICLES.get(i)
        if article is None:
            return "ErrorPage"
        cities.append(article.destination)
    cities = set(cities)

    print(cities)

    hotels = []
    concepts = []

    for city in cities:
        c = CITYDATACACHE.get(city)
        hotels.extend(c.hotels)
        for con in c.concepts:
            concepts.append(con.get("name"))
    hotels = list(set(hotels))
    concepts = list(set(concepts))
    response = get_merchandising(data.get("adults"), data.get("children"), data.get("startDate"), data.get("endDate"),
                                 hotels, concepts=concepts)

    resp_data = build_destinations_response(response.json())
    return json.dumps(resp_data)


@app.route('/details', methods=["POST"])
def details():
    data = request.json


# endregion


def build_destinations_response(data):
    destinations = {}
    for item in data.get("accommodations"):
        # build key
        city = item.get("attraction").get("location").get("city")
        country = item.get("attraction").get("location").get("country")
        state = item.get("attraction").get("location").get("stateProvince")
        key = []
        for thing in [city, state, country]:
            if thing:
                key.append(thing)
        key = ", ".join(key)

        if not destinations.get(key):
            destinations[key] = {"hotels": []}

        destinations[key]["hotels"].append({"attraction": item.get("attraction"), "images": item.get("image")})
    return destinations


def get_typeahead(typeahead):
    """
    Make api call to get typeahead
    """
    url = BASE_URL + "typeahead?search={0}".format(typeahead)
    response = requests.get(url, headers=HEADERBASE)
    if response.status_code != 200:
        return "ErrorPage"
    return response


def get_destination(destination):
    """
    Make api call to get destination
    """
    url = BASE_URL + "destinations/detail?destination=place:{0}".format(destination)
    response = requests.get(url, headers=HEADERBASE)
    if response.status_code != 200:
        return "ErrorPage"
    return response


def get_merchandising(adults, children, start_date, end_date, hotels, get_pricing=False, concepts=None):
    url = BASE_URL + "hotels"
    data = {"adults": adults,
            "children": children,
            "rooms": 1,
            "startDate": start_date,
            "endDate": end_date,
            "hotelProvider": "hotelscombined",
            "concepts": concepts if concepts is not None else [],
            "getPricing": True,
            "page": 1,
            "hotelIds": hotels}

    data = {"adults": 2,
            "children": 2,
            "rooms": 1,
            "startDate": '2016-10-15',
            "endDate": '2016-10-25',
            "hotelProvider": "hotelscombined",
            "concepts": [],
            "getPricing": False,
            "page": 1,
            "hotelIds": hotels}

    print(data['hotelIds'])
    response = requests.post(url, data=json.dumps(data), headers=HEADERBASE)
    if response.status_code != 200:
        response.raise_for_status()
        return "ErrorPage"
    return response


def get_data_for_all_cities_in_list(cities_list, update=False):
    city_errors = []
    city_dict = {}
    city_cache = utils.load_cached_city_data(DATAFILEPATH)
    for city in cities_list:
        if city_cache.get(city) and not update:
            continue
        response = get_destination(city)
        if response.status_code != 200:
            city_errors.append(city)
        else:
            city_dict[city] = response.json()
    with open(os.path.abspath(DATAFILEPATH), 'a') as f:
        f.write(json.dumps(city_dict))
    return city_errors


def get_hotel_list(response):
    resp = response.json()
    return resp.get("hotels", None)


# TODO: this
def return_error_page(message):
    # load error page html
    # add message
    # return
    pass


if __name__ == "__main__":
    main()
