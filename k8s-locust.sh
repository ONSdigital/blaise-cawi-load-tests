#!/bin/bash

set -euo pipefail

gcloud container clusters get-credentials locust-gke-cluster --region=europe-west2

kubectl create configmap my-loadtest-locustfile --from-file locustfile.py ||
  kubectl create configmap my-loadtest-locustfile --from-file locustfile.py -o yaml --dry-run | kubectl replace -f -

for seed_file in seed-data*.csv; do
  kubectl create secret generic seed-data --from-file "${seed_file}" ||
    kubectl create secret generic seed-data --from-file "${seed_file}" -o yaml --dry-run | kubectl replace -f -
done

helm repo add deliveryhero https://charts.deliveryhero.io/ || true
helm uninstall locust || true
helm install locust deliveryhero/locust -f values.yaml --wait

kubectl --namespace default port-forward service/locust 8089:8089
