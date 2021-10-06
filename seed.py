import csv
import os
import requests
import sys
import yaml

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2 import id_token


load_dotenv()
insturment_names = os.getenv("INSTRUMENT_NAMES", "").split(",")

bus_client_id = os.getenv("BUS_CLIENT_ID", "ENV_VAR_NOT_SET")
bus_url = os.getenv("BUS_URL", "ENV_VAR_NOT_SET")
rest_api_url = os.getenv("REST_API_URL", "http://localhost:8000")
server_park = os.getenv("SERVER_PARK", "gusty")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.split(os.path.abspath(os.path.realpath(sys.argv[0])))[
                                                   0] + "/key.json"

def delete_uacs(bus_url, bus_client_id, instrument_name):
    token = id_token.fetch_id_token(Request(), bus_client_id)
    requests.delete(
        f"{bus_url}/uacs/admin/instrument/{instrument_name}",
        headers={"Authorization": f"Bearer {token}"},
    )


def generate_uacs(bus_url, bus_client_id, instrument_name):
    token = id_token.fetch_id_token(Request(), bus_client_id)
    return requests.post(
        f"{bus_url}/uacs/instrument/{instrument_name}",
        headers={"Authorization": f"Bearer {token}"},
    ).json()


def get_instrument_id(rest_api_url, server_park, instrument_name):
    return (
        requests.get(
            f"{rest_api_url}/api/v1/serverparks/{server_park}/instruments/{instrument_name}/id"
        )
            .json()
    )

def chunk_uacs(uac_list, chunk_size):
    return [uac_list[x:x+chunk_size] for x in range(0, len(uac_list), chunk_size)]

uacs = []

for instrument_name in instrument_names:
    delete_uacs(bus_url, bus_client_id, instrument_name)
    instrument_uacs = generate_uacs(bus_url, bus_client_id, instrument_name)
    instrument_id = get_instrument_id(rest_api_url, server_park, instrument_name)

    for uac, uac_info in instrument_uacs.items():
        uacs.append({
            "uac": uac,
            "case_id": uac_info.get("case_id"),
            "instrument_name": instrument_name,
            "instrument_id": instrument_id
        })

sorted_uacs = sorted(uacs, key=lambda k: k["uac"])

split_uacs = chunk_uacs(sorted_uacs, 10000)

with open("values-template.yaml", "r") as values_template:
    helm_values = yaml.load(values_template, Loader=yaml.SafeLoader)

for index, uac_block in enumerate(split_uacs):
    helm_values["loadtest"]["mount_external_secret"]["files"][f"seed-data{index}"] = [f"seed-data{index}.csv"]
    with open(f"seed-data{index}.csv", "w", newline="") as seed_data_csv:
        seed_data_fieldnames = ["uac", "case_id", "instrument_name", "instrument_id"]
        csv_writer = csv.DictWriter(seed_data_csv, fieldnames=seed_data_fieldnames)
        csv_writer.writeheader()
        for uac_detail in uac_block:
            csv_writer.writerow(uac_detail)

with open("values.yaml", "w") as values_file:
    yaml.dump(helm_values, values_file)
