import os

from dotenv import load_dotenv
from locust import HttpUser, task, constant
from locust_plugins.csvreader import CSVDictReader

load_dotenv()

instrument_name = os.getenv("INSTRUMENT_NAME")
instrument_guid = os.getenv("INSTRUMENT_GUID")
host_url = os.getenv("HOST_URL")
server_park = os.getenv("SERVER_PARK", "gusty")

if os.path.isfile("/uacs/uacs.csv"):
    uac_reader = CSVDictReader("/uacs/uacs.csv")
else:
    uac_reader = CSVDictReader("uacs.csv")


class CAWI(HttpUser):
    host = f"{host_url}"
    wait_time = constant(0)

    @task
    def open_questionnaire(self):
        uac = next(uac_reader)
        print(uac["uaccode"])
        print(uac["postcode"])
        print(uac["caseid"])

        """
        # cawi portal
        self.client.get("/auth/login")
        time.sleep(3)
        self.client.post("/auth/login", {"uac": uac["uaccode"]})
        self.client.get("/auth/login/postcode")
        time.sleep(2)
        self.client.post("/auth/login/postcode", {"postcode": uac["postcode"]})
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
                    "KeyValue": uac["caseid"],
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
