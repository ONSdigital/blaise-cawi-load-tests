import csv
import os
import requests
import sys
import yaml

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2 import id_token

load_dotenv()
instrument_names = os.getenv("INSTRUMENT_NAMES", "ENV_VAR_NOT_SET").split(",")
bus_client_id = os.getenv("BUS_CLIENT_ID", "ENV_VAR_NOT_SET")
bus_url = os.getenv("BUS_URL", "ENV_VAR_NOT_SET")
host_url = os.getenv("HOST_URL", "ENV_VAR_NOT_SET")
rest_api_url = os.getenv("REST_API_URL", "http://localhost:90")
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


def chunk_seed_data(seed_data, chunk_size):
    return [seed_data[x:x + chunk_size] for x in range(0, len(seed_data), chunk_size)]


seed_data = []

for instrument_name in instrument_names:
    delete_uacs(bus_url, bus_client_id, instrument_name)
    instrument_seed_data = generate_uacs(bus_url, bus_client_id, instrument_name)
    instrument_id = get_instrument_id(rest_api_url, server_park, instrument_name)

    for uac, seed_info in instrument_seed_data.items():
        seed_data.append({
            "uac": uac,
            "case_id": seed_info.get("case_id"),
            "instrument_name": instrument_name,
            "instrument_id": instrument_id
        })

sorted_seed_data = sorted(seed_data, key=lambda k: k["uac"])

split_seed_data = chunk_seed_data(sorted_seed_data, 10000)

with open("values-template.yaml", "r") as values_template:
    helm_values = yaml.load(values_template, Loader=yaml.SafeLoader)

helm_values["master"] = {"environment": {"HOST_URL": host_url, "SERVER_PARK": server_park}}
helm_values["worker"]["environment"] = {"HOST_URL": host_url, "SERVER_PARK": server_park}

for index, seed_data_block in enumerate(split_seed_data):
    helm_values["loadtest"]["mount_external_secret"]["files"][f"seed-data{index}"] = [f"seed-data{index}.csv"]
    with open(f"seed-data{index}.csv", "w", newline="") as seed_data_csv:
        seed_data_fieldnames = ["uac", "case_id", "instrument_name", "instrument_id"]
        csv_writer = csv.DictWriter(seed_data_csv, fieldnames=seed_data_fieldnames)
        csv_writer.writeheader()
        for seed_data_row in seed_data_block:
            csv_writer.writerow(seed_data_row)

with open("values.yaml", "w") as values_file:
    yaml.dump(helm_values, values_file)
