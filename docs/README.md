# DevOps Documentation — Overview

This documentation describes how the CI/CD and Cloud Observability platform for the Student Management web system was built, step by step, on a self-managed Kubernetes cluster.

The work is split into numbered documents, in the order they were carried out:

| Step | Document | Outcome |
|------|----------|---------|
| 0 | *This page* — [Virtual machines](#virtual-machines) | Two Ubuntu VMs |
| 1 | [1-kubernetes-cluster.md](1-kubernetes-cluster.md) | kubeadm cluster: 1 master + 1 worker, Flannel CNI |
| 2 | [2-argocd-and-jenkins.md](2-argocd-and-jenkins.md) | ArgoCD installed, backend & frontend deployed for the first time, Jenkins able to build Docker images |
| 3 | [3-ci-cd-pipeline.md](3-ci-cd-pipeline.md) | Pushing a Git tag `vX.Y.Z` builds an image with the same tag and deploys it automatically |
| 4 | [4-cloud-observability-setup.md](4-cloud-observability-setup.md) | Prometheus, Grafana, Loki, Promtail and Tempo deployed through ArgoCD |
| 5 | [5-metrics-logs-traces.md](5-metrics-logs-traces.md) | Backend metrics, logs and traces collected and linked together in Grafana |

## Virtual machines

The cluster runs on two VMs (VMware Workstation on a Windows host), both **Ubuntu Server** with **2 vCPU**, on the same network:

| Role | Hostname | IP address | RAM | Disk |
|------|----------|------------|-----|------|
| Master node (control plane) | `k8s-master-node` | `192.168.192.136` | 3 GB | 20 GB |
| Worker node | `k8s-worker-node-1` | `192.168.192.138` | 5 GB | 50 GB |

- Both VMs use a **static IP**: the API server address and node registration depend on it.
- The master keeps its default `NoSchedule` taint and only runs the control plane. Every workload (applications, ArgoCD, Jenkins, observability stack) runs on the worker, which is why the worker has most of the RAM and disk.
- All operations are done over SSH from the host. The Windows host is also used to run **ngrok** (step 3) and to build the very first Docker images (step 2).

## Exposed services

Every service is exposed as a `NodePort`, so it is reachable on either node IP (`192.168.192.136` or `192.168.192.138`):

| Port | Service | Defined in |
|------|---------|------------|
| 30000 | Backend (FastAPI — `/docs`, `/metrics`) | [app/helm/backend/values.yaml](https://github.com/duyanh221204/vdt-backend-config/blob/main/values.yaml) |
| 30001 | Frontend (nginx) | [app/helm/frontend/values.yaml](https://github.com/duyanh221204/vdt-frontend-config/blob/main/values.yaml) |
| 32000 | Jenkins | [ci-cd/jenkins/jenkins.yaml](../ci-cd/jenkins/jenkins.yaml) |
| 32001 / 32002 | ArgoCD (HTTP / HTTPS) | [ci-cd/argocd/argoCD.yaml](../ci-cd/argocd/argoCD.yaml) |
| 32100 | Grafana | [prometheus-stack-values.yaml](https://github.com/duyanh221204/vdt-cloud-observability/blob/main/values/prometheus-stack-values.yaml) |
| 32200 | Prometheus | [prometheus-stack-values.yaml](https://github.com/duyanh221204/vdt-cloud-observability/blob/main/values/prometheus-stack-values.yaml) |

## Scripts

Long sequences of consecutive commands are also kept as scripts in [scripts/](../scripts). Each document shows the commands and links to the matching script. The repository is cloned on both nodes, and the scripts and `kubectl apply -f` commands are run from its root.

| Script | Run on | Step |
|--------|--------|------|
| [1-node-prepare.sh](../scripts/1-node-prepare.sh) | both nodes (`sudo`) | 1 |
| [1-master-init.sh](../scripts/1-master-init.sh) | master (normal user) | 1 |
| [2-worker-prepare.sh](../scripts/2-worker-prepare.sh) | worker (`sudo`) | 2 |
| [2-jenkins-docker-cli.sh](../scripts/2-jenkins-docker-cli.sh) | master | 2 |

## Repository map

```text
vdt-devops/
├── app/
│   ├── src/                          # source code (submodules)
│   │   ├── backend/                  # FastAPI, Dockerfile, Jenkinsfile
│   │   └── frontend/                 # Vue, nginx.conf, Dockerfile, Jenkinsfile
│   └── helm/                         # Helm charts watched by ArgoCD (submodules)
│       ├── backend/                  # backend + PostgreSQL + ServiceMonitor
│       └── frontend/                 # frontend
├── ci-cd/
│   ├── argocd/
│   │   ├── argoCD.yaml               # NodePort service for the ArgoCD UI
│   │   └── apps/
│   │       ├── vdt-backend-app.yaml
│   │       └── vdt-frontend-app.yaml
│   └── jenkins/
│       ├── jenkins-pvc.yaml          # PV + PVC (hostPath /data/jenkins_home)
│       └── jenkins.yaml              # Deployment + NodePort Service
├── cloud-observability/              # submodule
│   ├── root-app.yaml                 # parent Application (app-of-apps)
│   ├── applications/                 # loki, prometheus-stack, promtail, tempo
│   └── values/                       # Helm values for each chart
├── docs/                             # this documentation
├── images/                           # screenshots used by the documentation
└── scripts/
    ├── 1-node-prepare.sh
    ├── 1-master-init.sh
    ├── 2-worker-prepare.sh
    └── 2-jenkins-docker-cli.sh
```

## Reproducing this setup

The pipelines push images to the Docker Hub account `nguyenduyanh221204` and commit to the GitHub repos of `duyanh221204`, so another account needs its own copies:

- Fork the six repositories (`vdt-devops` and the five submodules), point the submodule URLs in `.gitmodules` to the forks, and clone the `vdt-devops` fork on both nodes.
- In the forks, replace `nguyenduyanh221204` with the Docker Hub account and `duyanh221204` with the GitHub account. `grep -rn duyanh221204 .` finds every place, since the string is part of both names.
- Set `image.tag` to `v1.0.0` in both config repos. The current tags only exist on the original Docker Hub account, and the pipeline only accepts a Git tag greater than `image.tag`.
- Use the IPs of your own VMs wherever `192.168.192.136` / `192.168.192.138` appear in the commands and URLs.
