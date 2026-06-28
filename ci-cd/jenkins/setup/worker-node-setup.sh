#!/bin/bash
set -e

echo "==> Install Docker"
sudo apt-get update
sudo apt-get install -y docker.io

echo "==> Configure docker.socket permissions"
sudo mkdir -p /etc/systemd/system/docker.socket.d

echo -e "[Socket]\nSocketMode=0666" | sudo tee /etc/systemd/system/docker.socket.d/override.conf

sudo systemctl daemon-reload
sudo systemctl enable --now docker.socket
sudo systemctl enable --now docker
sudo systemctl restart docker.socket
sudo systemctl restart docker

echo
echo "Done!"

# chmod +x worker-node-setup.sh
# ./worker-node-setup.sh