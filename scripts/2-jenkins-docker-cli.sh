#!/usr/bin/env bash
set -euo pipefail

DOCKER_VERSION="${DOCKER_VERSION:-27.0.3}"
NAMESPACE="${NAMESPACE:-jenkins}"

echo "==> Waiting for Jenkins to be available"
kubectl -n "${NAMESPACE}" rollout status deployment/jenkins --timeout=300s

echo "==> Installing Docker CLI ${DOCKER_VERSION} into /var/jenkins_home/docker"
kubectl -n "${NAMESPACE}" exec deployment/jenkins -- bash -c "
  set -euo pipefail
  cd /var/jenkins_home
  curl -fsSL https://download.docker.com/linux/static/stable/x86_64/docker-${DOCKER_VERSION}.tgz -o docker.tgz
  rm -rf docker-folder
  mkdir docker-folder
  tar xzf docker.tgz -C docker-folder
  mv -f docker-folder/docker/docker /var/jenkins_home/docker
  chmod +x /var/jenkins_home/docker
  rm -rf docker-folder docker.tgz
"

echo "==> Verifying"
kubectl -n "${NAMESPACE}" exec deployment/jenkins -- /var/jenkins_home/docker version
