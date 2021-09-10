import csv
import os
import sys

import requests
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2 import id_token

load_dotenv()

instrument_name = os.getenv("INSTRUMENT_NAME")
bus_client_id = os.getenv("BUS_CLIENT_ID")
bus_url = os.getenv("BUS_URL")
rest_api_url = os.getenv("REST_API_URL", "http://localhost:90")
server_park = os.getenv("SERVER_PARK", "gusty")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.split(os.path.abspath(os.path.realpath(sys.argv[0])))[0] + "\key.json"


def generate_uacs(bus_url, bus_client_id, instrument_name):
    token = id_token.fetch_id_token(Request(), bus_client_id)
    return requests.post(
        f"{bus_url}/uacs/instrument/{instrument_name}",
        headers={"Authorization": f"Bearer {token}"},
    ).json()


def get_postcodes(rest_api_url, server_park, instrument_name):
    return (
        requests.get(
            f"{rest_api_url}/api/v1/serverparks/{server_park}/instruments/{instrument_name}/report?fieldIds=qid.serial_number&fieldIds=qdatabag.postcode"
        )
            .json()
            .get("reportingData")
    )


def match_postcode(postcodes, case_id):
    for postcode_thing in postcodes:
        if postcode_thing.get("qid.serial_number") == case_id:
            return postcode_thing.get("qdatabag.postcode")
    return ""


uacs = generate_uacs(bus_url, bus_client_id, instrument_name)
postcodes = get_postcodes(rest_api_url, server_park, instrument_name)

with open("uacs.csv", "w", newline="") as csvfile:
    fieldnames = ["uaccode", "postcode", "caseid"]
    csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
    csvwriter.writeheader()
    for uac, uac_info in uacs.items():
        csvwriter.writerow(
            {
                "uaccode": uac,
                "caseid": uac_info.get("case_id"),
                "postcode": match_postcode(postcodes, uac_info.get("case_id")),
            }
        )
