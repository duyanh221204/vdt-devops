#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Please run as root (sudo $0)" >&2
  exit 1
fi

echo "==> [1/3] Creating hostPath directories"
mkdir -p /data/jenkins_home /data/postgres_home
chown -R 1000:1000 /data/jenkins_home
chown -R 999:999 /data/postgres_home

echo "==> [2/3] Installing Docker Engine"
apt-get update
apt-get install -y docker.io

echo "==> [3/3] Setting docker.sock mode to 0666"
mkdir -p /etc/systemd/system/docker.socket.d
cat <<EOF > /etc/systemd/system/docker.socket.d/override.conf
[Socket]
SocketMode=0666
EOF
systemctl daemon-reload
systemctl enable --now docker.socket
systemctl enable --now docker
systemctl restart docker.socket
systemctl restart docker

ls -l /var/run/docker.sock
echo "==> Done: Docker $(docker version --format '{{.Server.Version}}') on $(hostname)"
