import os
import time
import csv
from datetime import datetime
from dotenv import load_dotenv
from locust import HttpUser, task, constant, events
from locust.runners import MasterRunner, WorkerRunner, LocalRunner
from bs4 import BeautifulSoup
import glob

load_dotenv()
host_url = os.getenv("HOST_URL", "ENV_VAR_NOT_SET")
server_park = os.getenv("SERVER_PARK", "gusty")

seed_files = glob.glob("/seed-data/seed-data*.csv")
if len(seed_files) == 0:
    seed_files = glob.glob("/mnt/locust/seed-data*.csv")
if len(seed_files) == 0:
    seed_files = ["seed-data.csv"]

seed_data_readers = []

for seed_file in seed_files:
    seed_data_file = open(seed_file)
    seed_data_reader = csv.DictReader(seed_data_file)
    seed_data_readers.append(seed_data_reader)

csv_data = []
seed_index = 0

def setup_seed_data(environment, msg, **kwargs):
    # Fired when the worker recieves a message of type 'setup_seed_data'
    csv_data.extend(msg.data)
    environment.runner.send_message("acknowledge_seed_data", f"Thanks for the {len(msg.data)} caseId! they are: {msg.data}")


def on_acknowledge(msg, **kwargs):
    # Fired when the master recieves a message of type 'acknowledge_seed_data'
    print(msg.data)


@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    if not isinstance(environment.runner, MasterRunner):
        environment.runner.register_message("seed_data", setup_seed_data)
    if not isinstance(environment.runner, WorkerRunner):
        environment.runner.register_message("acknowledge_seed_data", on_acknowledge)


@events.test_start.add_listener
def on_test_start(environment, **_kwargs):
    # When the test is started, evenly divides list between
    # worker nodes to ensure unique data across threads
    if not isinstance(environment.runner, WorkerRunner):
        seed_data = []
        for seed_data_reader in seed_data_readers:
            for row in seed_data_reader:
                seed_data.append(row)
    if isinstance(environment.runner, MasterRunner):
        worker_count = environment.runner.worker_count
        chunk_size = int(len(seed_data) / worker_count)

        for i, worker in enumerate(environment.runner.clients):
            start_index = i * chunk_size

            if i + 1 < worker_count:
                end_index = start_index + chunk_size
            else:
                end_index = len(seed_data)

            data = seed_data[start_index:end_index]
            environment.runner.send_message("seed_data", data, worker)
    elif isinstance(environment.runner, LocalRunner):
        csv_data.extend(seed_data)
    else:
        print("Im not in the workers")

class CAWI(HttpUser):
    host = f"{host_url}"
    wait_time = constant(2)

    def next(self):
        global seed_index
        if seed_index == len(csv_data) - 1:
            print("reset index")
            seed_index = 0
        else:
            print("increment index")
            seed_index += 1

    @task
    def open_questionnaire(self):
        global seed_index
        seeded_case = csv_data[seed_index]

        print(f"user running open questionnaire task for index: {seed_index}")
        print(seeded_case)
        print(datetime.now())

        self.next()

        # cawi portal
        response = self.client.get("/auth/login")
        time.sleep(3)

        content = BeautifulSoup(response.content)
        csrf_token = content.body.find('input', {'name': '_csrf'})['value']
        self.client.post("/auth/login", {"uac": seeded_case["uac"], "_csrf": csrf_token})

        self.client.get(f"/{seeded_case['instrument_name']}/")
        self.client.post(
            f"/{seeded_case['instrument_name']}/api/application/start_interview",
            json={
                "RuntimeParameters": {
                    "ServerPark": f"{server_park}",
                    "InstrumentId": f"{seeded_case['instrument_id']}",
                    "MeasurePageTimes": False,
                    "IsPreview": False,
                    "IsTesting": False,
                    "KeyValue": seeded_case["case_id"],
                    # "KeyValue": "1001011",
                    "LayoutSet": "CAWI-Web_Large",
                    "Mode": "CAWI",
                },
                "ClientFeatures": {
                    "Browser": 3,
                    "Device": 2,
                    "Height": 790,
                    "Language": "en-GB",
                    "Latitude": 0,
                    "Longitude": 0,
                    "OS": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
                    "PixelRatio": 1,
                    "Platform": 1,
                    "RecorderAvailable": False,
                    "Referrer": "",
                    "ReferrerUrl": f"https://{self.host}/auth/login",
                    "ScreenHeight": 790,
                    "ScreenWidth": 1720,
                    "ScrollbarSize": 15,
                    "TouchEnabled": False,
                    "Width": 1720,
                },
                "AccessToken": None,
                "RefreshToken": None,
            },
        )

        # cawi portal
        time.sleep(5)
        self.client.get("/auth/logout")
