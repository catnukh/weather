import datetime as dt
import json

import requests
from flask import Flask, jsonify, request

#your own token
API_TOKEN = ""
# you need to sign up here - https://www.visualcrossing.com
API_KEY = ""

app = Flask(__name__)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return "<p><h2>KMA L2: python Saas.</h2></p>"


@app.route("/content/api/v1/integration/generate", methods=["POST"])
def weather_endpoint():
    start_dt = dt.datetime.now()
    json_data = request.get_json()

    if json_data.get("token") is None:
        raise InvalidUsage("token is required", status_code=400)

    token = json_data.get("token")

    if token != API_TOKEN:
        raise InvalidUsage("wrong API token", status_code=403)

    requester_name = ""
    if json_data.get("requester_name"):
        requester_name = json_data.get("requester_name")

    location = ""
    if json_data.get("location"):
        location = json_data.get("location")

    date = ""
    if json_data.get("date"):
        date = json_data.get("date")

    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}/{date}?key={API_KEY}"
    url_elements = url+"&elements=temp,windspeed,pressure,humidity,snow"

    response = requests.get(url_elements, params={"unitGroup":"metric"})
    resp_dict = response.json()

    temp_c = resp_dict['days'][0]['temp']
    if temp_c <= 5:
        temp_message = " Your mum said you need to wear hat!"
    elif temp_c >= 27:
        temp_message = " You are not allowed to be naked on the street!"
    elif temp_c > 5 and temp_c <= 13:
        temp_message = " Just wear your autumn jacket"
    elif temp_c > 13 and temp_c <= 18:
        temp_message = " Just wear your denim jacket"
    elif temp_c > 18 and temp_c < 27:
        temp_message = " Comfort weather. Put on your T-shirt"
    else:
        temp_message = ""

    snow = resp_dict['days'][0]['snow']
    snow_message = ""
    if type(snow) == "float":
        if snow > 0 and snow is not None:
            snow_message = " Jingle Bells!"
        else:
            snow_message = ""

    result = {
        "requester_name": requester_name, 
        "timestamp": start_dt.isoformat(),
        "location": resp_dict.get("address"),
        "date": date,
        "weather":
            {
            "temp_c": f"{temp_c}{temp_message}",
            "wind_kph": resp_dict['days'][0]['windspeed'],
            "pressure_mb": resp_dict['days'][0]['pressure'],
            "humidity": resp_dict['days'][0]['humidity'],
            "snow": f"{snow}{snow_message}"
            }
            }

    return result
