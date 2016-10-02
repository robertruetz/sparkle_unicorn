from flask import Flask, request, send_from_directory
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


def main():
    error_list = None
    if not os.path.exists(DATAFILEPATH):
        error_list = get_data_for_all_cities_in_list(DISTINCTCITIES)
    if error_list is not None:
        print("Could not load data for {0}".format(error_list))
    app.run()
    print("NOTHING")
    # app = Flask(__name__)


@app.route('/')
def index_page():
    return app.send_static_file('index.html')

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)
@app.route('/css/<path:path>')
def send_js(path):
    return send_from_directory('css', path)

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


def get_merchandising(adults, children, hotels, get_pricing=False, concepts=None):
    url = BASE_URL + "hotels"
    data = {"adults": adults,
            "children": children,
            "rooms": 1,
            "startDate": utils.get_date_today_string(),
            "endDate": utils.get_date_today_string(1),
            "hotelProvider": "hotelscombined",
            "concepts": concepts if concepts is not None else [],
            "getPricing": get_pricing,
            "page": 1,
            "hotelIds": hotels}
    response = requests.post(url, data=json.dumps(data), headers=HEADERBASE)
    # TODO: Handle response verification
    return response


@app.route('/entrypoint')
def entrypoint():
    img_files = []
    for k, v in IMAGETILES.items():
        img_files.append({"url": v.url, "id": v.id})
    return json.dumps(img_files)


@app.route('/filter', methods=["POST"])
def filter():
    data = request.form
    ids = data.get("ids", None)
    if ids is None:
        raise Exception
    imgs = []
    for i in ids:
        imgs.append(IMAGETILES.get(i))


def get_data_for_all_cities_in_list(cities_list):
    city_errors = []
    for city in cities_list:
        response = get_destination(city)
        if response.status_code != 200:
            city_errors.append(city)
        else:
            with open(os.path.abspath(DATAFILEPATH), 'a') as f:
                f.write("{0}: ".format(city) + response.text + "\n")
    return city_errors


# @app.route('/entrypoint/<city>')
# def entrypoint(city):
#     # Make destination call with the city
#     response = get_destination(city)
#     # pull list of hotels
#     hotel_list = get_hotel_list(response)
#     if hotel_list is None:
#         raise()
#     # Make merchandising call for family and couple
#     family, couple = get_full_merchandising(hotel_list)
#     return family.text + "\n\n" + couple.text
#     # Pull concepts from that city
#     # Return images that match the distinct set of concepts


def get_full_merchandising(hotels):
    family = get_merchandising(2, 2, hotels)
    couple = get_merchandising(2, 0, hotels)

    # TODO: combine data into distinct set

    return family, couple


def get_hotel_list(response):
    resp = response.json()
    return resp.get("hotels", None)


if __name__ == "__main__":
    main()
