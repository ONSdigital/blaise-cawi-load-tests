import os

from dotenv import load_dotenv
from locust import HttpUser, task, constant
from locust_plugins.csvreader import CSVDictReader

load_dotenv()

instrument_name = os.getenv("INSTRUMENT_NAME", "dst2106a")
instrument_guid = os.getenv("INSTRUMENT_GUID", "da6db4df-f429-4685-b861-e5c9d0f94c70")
host_url = os.getenv("HOST_URL", "https://dev-nik13-cati.social-surveys.gcp.onsdigital.uk")
server_park = os.getenv("SERVER_PARK", "gusty")

if os.path.isfile("/seed-data/seed-data.csv"):
    seed_data_reader = CSVDictReader("/seed-data/seed-data.csv")
else:
    seed_data_reader = CSVDictReader("seed-data.csv")


class CAWI(HttpUser):
    host = f"{host_url}"
    wait_time = constant(0)

    @task
    def open_questionnaire(self):
        seed_data = next(seed_data_reader)
        print(seed_data["uac"])
        print(seed_data["postcode"])
        print(seed_data["case_id"])

        """
        # cawi portal
        self.client.get("/auth/login")
        time.sleep(3)
        self.client.post("/auth/login", {"uac": seed_data["uac"]})
        self.client.get("/auth/login/postcode")
        time.sleep(2)
        self.client.post("/auth/login/postcode", {"postcode": seed_data["postcode"]})
        """

        self.client.get(f"/{instrument_name}/")
        self.client.post(
            f"/{instrument_name}/api/application/start_interview",
            json={
                "RuntimeParameters": {
                    "ServerPark": f"{server_park}",
                    "InstrumentId": f"{instrument_guid}",
                    "MeasurePageTimes": False,
                    "IsPreview": False,
                    "IsTesting": False,
                    "KeyValue": seed_data["case_id"],
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
                    "ReferrerUrl": f"https://{self.host}/auth/login/postcode",
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

        """
        # cawi portal
        time.sleep(5)
        self.client.get("/auth/logout")
        """
