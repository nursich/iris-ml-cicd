#!/usr/bin/env bash
# Creates kubeconfig-minikube.yaml that the Jenkins container can use to
# reach Minikube (docker driver), and connects Jenkins to Minikube's network.
#
# Run on your computer (not inside Jenkins) after `minikube start`:
#   bash scripts/make-jenkins-kubeconfig.sh
# Then upload kubeconfig-minikube.yaml to Jenkins as a "Secret file"
# credential with ID: kubeconfig-minikube
set -euo pipefail

OUT="kubeconfig-minikube.yaml"
MINIKUBE_IP="$(minikube ip)"

# Self-contained kubeconfig (certificates embedded) for the minikube context
kubectl config view --flatten --minify --context=minikube > "$OUT"

# Inside Docker, Minikube's API server is at <minikube ip>:8443
# (on the host it is published on 127.0.0.1:<random port>)
sed -i.bak -E "s#server: https://[^ ]+#server: https://${MINIKUBE_IP}:8443#" "$OUT"
rm -f "$OUT.bak"

# Let the Jenkins container reach the Minikube container
docker network connect minikube jenkins 2>/dev/null || true

echo "Created $OUT (API server https://${MINIKUBE_IP}:8443)"
echo "Check from Jenkins:"
echo "  docker cp $OUT jenkins:/tmp/kc.yaml && docker exec jenkins kubectl --kubeconfig /tmp/kc.yaml get nodes"
