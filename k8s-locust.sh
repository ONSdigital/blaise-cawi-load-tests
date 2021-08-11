#!/bin/bash

set -euo pipefail

gcloud container clusters get-credentials locust-gke-cluster --region=europe-west2

kubectl create configmap my-loadtest-locustfile --from-file locustfile.py ||
  kubectl create configmap my-loadtest-locustfile --from-file locustfile.py -o yaml --dry-run | kubectl replace -f -

kubectl create secret generic uacs --from-file uacs.csv ||
  kubectl create secret generic uacs --from-file uacs.csv -o yaml --dry-run | kubectl replace -f -

helm repo add deliveryhero https://charts.deliveryhero.io/
helm uninstall locust
helm install locust deliveryhero/locust -f values.yaml --wait

kubectl --namespace default port-forward service/locust 8089:8089
