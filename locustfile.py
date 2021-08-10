from os import times
from locust import HttpUser, task, constant
from locust_plugins.csvreader import CSVDictReader
from locust.contrib.fasthttp import FastHttpUser
import time

uac_reader = CSVDictReader("/mnt/locust/uacs.csv")


class CAWI(FastHttpUser):
    host = "https://dev-cawi.social-surveys.gcp.onsdigital.uk"
    wait_time = constant(0)

    @task
    def open_questionnaire(self):
        uac = next(uac_reader)
        print(uac["uaccode"])
        print(uac["postcode"])
        print(uac["caseid"])
        self.client.get("/auth/login")
        time.sleep(3)
        self.client.post("/auth/login", {"uac": uac["uaccode"]})
        self.client.get("/auth/login/postcode")
        time.sleep(3)
        self.client.post("/auth/login/postcode", {"postcode": uac["postcode"]})
        self.client.get("/dst2106a/")
        self.client.post("/dst2106a/api/application/start_interview", json={
            "RuntimeParameters": {
              "ServerPark": "gusty",
              "InstrumentId": "da6db4df-f429-4685-b861-e5c9d0f94c70",
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
              "Width": 1720
            },
            "AccessToken": None,
            "RefreshToken": None
        })
        time.sleep(5)
        self.client.get("/auth/logout")
