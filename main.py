from flask import Flask, request, send_from_directory
import requests
import json
import utils
import models
import os


app = Flask(__name__, static_url_path='/static')

BASE_URL = "https://api.wayblazer.com/v1/"
APIKEY = "PEZlargze3A0nyPTBfkP1kQcUw2227Ix"
HEADERBASE = {"content-type": "application/json", "x-api-key": APIKEY}
YAMLPATH = r"./files/images_cities.yml"
IMAGETILES = utils.load_imgTiles_from_yaml(YAMLPATH)

ARTICLEPATH = r"./files/article_data.yml"
ARTICLES = utils.load_article_data_from_yaml(ARTICLEPATH)   # Dictionary of id: article obj

DISTINCTCITIES = utils.get_distinct_cities(IMAGETILES)

DATAFILEPATH = r"./files/data_file.yml"
CITYDATACACHE = utils.load_cached_city_data(DATAFILEPATH)


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
    return app.send_static_file('index.html')

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

@app.route('/entrypoint')
def entrypoint():
    article_list = []
    for id, article in ARTICLES.items():
        article_list.append(article.to_entrypoint_response())
    return json.dumps(article_list)


@app.route('/reload/<thing>')
def reload_thing(thing):
    global ARTICLES
    if thing == "articles":
        ARTICLES = utils.load_article_data_from_yaml(ARTICLEPATH)
    return json.dumps({"status_code": "200", "message": "{0} reloaded.".format(thing)})


@app.route('/filter', methods=["POST"])
def filter():
    data = request.json
    ids = data.get("ids", None)
    if ids is None:
        raise Exception
    cities = []
    for i in ids:
        tile = IMAGETILES.get(i)
        if tile is None:
            raise Exception     #TODO: Really? Exception?
        cities.extend(tile.cities)
    cities = set(cities)

    # TODO: implement concept matching

    hotels = []
    concepts = []

    for city in cities:
        city_part = city.split(',')[0].strip().replace(' ', '_')
        c = CITYDATACACHE.get(city_part)
        hotels.extend(c.hotels[:2])
        for con in c.concepts:
            concepts.append(con.get("name"))
    hotels = list(set(hotels[:20]))
    concepts = list(set(concepts[:20]))
    response = get_merchandising(data.get("adults"), data.get("children"), data.get("start_date"), data.get("end_date"),
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
        attraction = item.get("attraction")
        image = item.get("image")
        urls = None
        if image:
            urls = image.get("urls")
        location = attraction.get("location")
        address = None
        if location:
            address = location.get("formattedAddress")
        hotel = {"name": attraction.get("name"),
                 "urls": urls,
                 "address": address}
        # hotel = models.Hotel(attraction.get("name"), urls, address)
        city = item.get("attraction").get("location").get("city")
        country = item.get("attraction").get("location").get("country")
        state = item.get("attraction").get("location").get("stateProvince")
        key = []
        for thing in [city, state, country]:
            if thing:
                key.append(thing)
        # key = "{0}, {1} {2}".format(city, state, country)
        key = ", ".join(key)
        if destinations.get(key) is not None:
            destinations[key]["hotels"].append(hotel)
            destinations[key]["city"] = city
            destinations[key]["state"] = state
            destinations[key]["country"] = country
            destinations[key]["concepts"] = attraction.get("concepts")
        else:
            destinations[key] = {"hotels": []}
            destinations[key]["hotels"].append(hotel)
            destinations[key]["city"] = city
            destinations[key]["state"] = state
            destinations[key]["country"] = country
            destinations[key]["concepts"] = attraction.get("concepts")
    return destinations


def get_typeahead(typeahead):
    """
    Make api call to get typeahead
    """
    url = BASE_URL + "typeahead?search={0}".format(typeahead)
    response = requests.get(url, headers=HEADERBASE)
    #TODO: Handle response verification
    return response


def get_destination(destination):
    """
    Make api call to get destination
    """
    url = BASE_URL + "destinations/detail?destination=place:{0}".format(destination)
    response = requests.get(url, headers=HEADERBASE)
    # TODO: Handle response verification
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
            "getPricing": get_pricing,
            "page": 1,
            "hotelIds": hotels}
    response = requests.post(url, data=json.dumps(data), headers=HEADERBASE)
    # TODO: Handle response verification
    return response


def get_data_for_all_cities_in_list(cities_list):
    city_errors = []
    city_dict = {}
    for city in cities_list:
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
