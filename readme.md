# Blaise CAWI load tests

## Prereqs

- Terraform
- python (>3.5)
- poetry

## Installing Poetry

Linux/ OSX:

```bash
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

Windows:

```powershell
(Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -UseBasicParsing).Content | python -
```

## Install dependencies

```sh
poetry install
```

## Seeding data

Get UACs, postcode and case ID into a csv

Set Env variables:

- instrument_name
- bus_client_id
- bus_url

Run the seed script
`poetry run python seed.py`

## Run locust

### Locally

Build docker image
`docker build -t mylocust .`

Run docker compose
`docker-compose up --scale worker=4`

### In kubernetes

**Note**: This stores terraform state locally in a `terraform.tfstate`. Look after this carefully, so you can easily update/ teardown.

```sh
export GOOGLE_OAUTH_ACCESS_TOKEN=$(gcloud auth print-access-token)
gcloud config set project <gcp_project_id>
terraform -chdir=terraform init
terraform -chdir=terraform apply --var=project_id="<gcp_project_id>"

./k8s-locust.sh
```

#### Cleanup

Running a kubernetes cluster gets expensive, tear it down when you are finished.

```sh
terraform -chdir=terraform destroy
```
