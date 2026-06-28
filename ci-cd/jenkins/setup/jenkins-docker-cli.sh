#!/bin/bash
set -e

kubectl exec -i deployment/jenkins -n jenkins -- /bin/bash <<'EOF'
cd /var/jenkins_home

curl -fsSL https://download.docker.com/linux/static/stable/x86_64/docker-27.0.3.tgz -o docker.tgz

tar xzf docker.tgz

mv docker docker-folder
mv docker-folder/docker .

chmod +x docker

rm -rf docker-folder docker.tgz
EOF

echo
echo "Done!"

# chmod +x jenkins-docker-cli.sh
# ./jenkins-docker-cli.sh

# Cấu hình Mount Volume trên Master Node:
# nano jenkins.yaml
# Thêm vào dưới khối containers:
#         volumeMounts:
#         - name: docker-sock
#           mountPath: /var/run/docker.sock
#         (Giữ nguyên cấu hình mount /var/jenkins_home ở đây)

# Thêm vào dưới khối volumes ở cuối tệp:
#       volumes:
#       - name: docker-sock
#         hostPath:
#           path: /var/run/docker.sock
#       (Giữ nguyên cấu hình PVC jenkins-pvc của bạn ở đây)
# Áp dụng cấu hình mới
# kubectl apply -f jenkins.yaml
# Ép Kubernetes khởi động lại Pod Jenkins để làm mới tiến trình kết nối Volume 
# kubectl rollout restart deployment jenkins -n jenkins