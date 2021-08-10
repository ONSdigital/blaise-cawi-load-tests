import os
import requests
from google.auth.transport.requests import Request
from google.oauth2 import id_token
import csv

instrument_name = os.getenv("INSTRUMENT_NAME")
bus_client_id = os.getenv("BUS_CLIENT_ID")
bus_url = os.getenv("BUS_URL")
restapi_url = os.getenv("RESTAPI_URL", "http://localhost:90")
serverpark = os.getenv("SERVERPARK", "gusty")


def generate_uacs(bus_url, bus_client_id, instrument_name):
    token = id_token.fetch_id_token(Request(), bus_client_id)
    return requests.post(
        f"{bus_url}/uacs/instrument/{instrument_name}",
        headers={"Authorization": f"Bearer {token}"},
    ).json()


def get_postcodes(restapi_url, serverpark, instrument_name):
    return (
        requests.get(
            f"{restapi_url}/api/v1/serverparks/{serverpark}/instruments/{instrument_name}/report?fieldIds=qid.serial_number&fieldIds=qdatabag.postcode"
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
postcodes = get_postcodes(restapi_url, serverpark, instrument_name)

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
