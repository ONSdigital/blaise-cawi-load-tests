# Blaise CAWI Load Tests

### Local Setup

Prerequisites:
- Python ≥ 3.5
- gcloud

Clone the project locally:

```shell
git clone https://github.com/ONSdigital/ ...
```

Install Poetry:

Linux/macOS:
```bash
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

Windows:
```powershell
(Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -UseBasicParsing).Content | python -
```

Install dependencies:

```shell
poetry install
```

Authenticate with GCP:
```shell
gcloud auth login
```

Set your GCP project:
```shell
gcloud config set project ons-blaise-v2-dev-sandbox123
```

Open a tunnel to our Blaise RESTful API in your GCP project:
```shell
gcloud compute start-iap-tunnel restapi-1 80 --local-host-port=localhost:90 --zone europe-west2-a
```

Get service account key:
```shell
gcloud iam service-accounts keys create key.json --iam-account ons-blaise-v2-dev-sandbox123@appspot.gserviceaccount.com
```

Create an .env file in the root of the project and add the following environment variables:

| Variable | Description | Example |
| --- | --- | --- |
| INSTRUMENT_NAME | The name of the questionnaire instrument. | dst2106a |
| INSTRUMENT_GUID | The globally unique identifier of the questionnaire instrument. | da6db4df-f429-4685-b861-e5c9d0f94c70 |
| BUS_CLIENT_ID | The bearer token to authenticate with BUS. | blah.apps.googleusercontent.com |
| BUS_URL | The URL for BUS. | https://dev-sandbox123-bus.social-surveys.gcp.onsdigital.uk |
| HOST_URL | The URL for Locust to run load tests on. | https://dev-sandbox123-cati.social-surveys.gcp.onsdigital.uk https://dev-sandbox123-cawi.social-surveys.gcp.onsdigital.uk |

```shell
INSTRUMENT_NAME="dst2106a"
INSTRUMENT_GUID="da6db4df-f429-4685-b861-e5c9d0f94c70"
BUS_CLIENT_ID="blah.apps.googleusercontent.com"
BUS_URL="https://dev-sandbox123-bus.social-surveys.gcp.onsdigital.uk"
HOST_URL="https://dev-sandbox123-cati.social-surveys.gcp.onsdigital.uk"
```

Seed data and download to csv file:

```shell
poetry run python seed.py
```

Start Locust:

```shell
poetry run python -m locust
```

Access Locust:

http://localhost:8089/

### Run locally via Docker

Prerequisites:
- Docker

Build docker image:

```shell
docker build -t mylocust .
```

Run docker compose:

```shell
docker-compose up --scale worker=4
```

Access Locust:

http://localhost:8089/

### Run via Kubernetes in GCP

Prerequisites:
- kubectl
- helm

Temporarily set an env var with your access token:
```shell
export GOOGLE_OAUTH_ACCESS_TOKEN=$(gcloud auth print-access-token)
```

Initialise Terraform:
```shell
terraform -chdir=terraform init
```

Set Terraform to your GCP project ID:
```shell
terraform -chdir=terraform apply --var=project_id=ons-blaise-v2-dev-sandbox123
```

Execute this script:
```shell
./k8s-locust.sh
```

Access Locust:

http://localhost:8089/

**Note:** This process stores your Terraform state locally in a `terraform.tfstate` file. Look after this file carefully, so that you can easily update and teardown your cluster.

Teardown cluster:

```shell
terraform -chdir=terraform destroy --var=project_id=ons-blaise-v2-dev-sandbox123
```