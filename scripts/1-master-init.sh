#!/usr/bin/env bash
set -euo pipefail

POD_CIDR="${POD_CIDR:-10.244.0.0/16}"
FLANNEL_URL="https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml"

if [[ "${EUID}" -eq 0 ]]; then
  echo "Run this script as your normal user (it calls sudo itself)" >&2
  exit 1
fi

echo "==> [1/4] kubeadm init (pod CIDR ${POD_CIDR})"
if [[ -f /etc/kubernetes/admin.conf ]]; then
  echo "    Control plane already initialized, skipping"
else
  sudo kubeadm init --pod-network-cidr="${POD_CIDR}"
fi

echo "==> [2/4] Configuring kubectl for $(id -un)"
mkdir -p "${HOME}/.kube"
sudo cp /etc/kubernetes/admin.conf "${HOME}/.kube/config"
sudo chown "$(id -u):$(id -g)" "${HOME}/.kube/config"

echo "==> [3/4] Installing Flannel"
kubectl apply -f "${FLANNEL_URL}"

echo "==> [4/4] Waiting for the node to become Ready"
kubectl wait --for=condition=Ready node --all --timeout=180s

echo
echo "==> Run this on the WORKER node with sudo:"
sudo kubeadm token create --print-join-command
