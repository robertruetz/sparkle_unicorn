from flask import Flask, request
import requests
import json
import utils
import os

app = Flask(__name__, static_url_path='/static')

BASE_URL = "https://api.wayblazer.com/v1/"
APIKEY = "PEZlargze3A0nyPTBfkP1kQcUw2227Ix"
HEADERBASE = {"content-type": "application/json", "x-api-key": APIKEY}

YAMLPATH = r"./files/images_cities.yml"
IMAGETILES = utils.load_imgTiles_from_yaml(YAMLPATH)
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


@app.route('/entrypoint')
def entrypoint():
    img_files = []
    for k, v in IMAGETILES.items():
        img_files.append({"url": v.url, "id": v.id})
    return json.dumps(img_files)


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
        hotels.extend(c.hotels)
        for con in c.concepts:
            concepts.append(con.get("name"))
    hotels = list(set(hotels[:20]))
    concepts = list(set(concepts[:20]))
    response = get_merchandising(data.get("adults"), data.get("children"), data.get("start_date"), data.get("end_date"),
                                 hotels, concepts=concepts)
    return json.dumps(response.json())

# endregion


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
