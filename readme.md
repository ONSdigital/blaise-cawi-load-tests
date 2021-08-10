Get UACs, postcode and case ID into a csv

Set Env variables
- instrument_name
- bus_client_id
- bus_url

Install dependencies 
`poetry install`
`poetry add requests`

Run the seed script
`poetry run python seed.py`

run postcode-cacher cloud function to cache postcodes into redis 

Starting locust

Build docker image 
`docker build -t mylocust .`

Run docker compose 
`docker-compose up --scale worker=4`

