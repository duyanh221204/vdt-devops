# VDT DevOps — CI/CD & Cloud Observability for a Student Management Web System

This repository applies a **CI/CD pipeline with GitOps** and a **Cloud Observability** stack to deploy and operate a small web application on a self-managed **Kubernetes** cluster.

The application is a **Student Management** system:

| Layer    | Technology                               | Notes                                                                 |
|----------|------------------------------------------|-----------------------------------------------------------------------|
| Frontend | Vue 3 + Vite, served by **nginx**        | nginx also reverse-proxies `/api/*` to the backend service            |
| Backend  | **FastAPI** (Python 3.11), SQLAlchemy async | JWT auth (`admin` / `user` roles), CRUD on students, rate limiting |
| Database | **PostgreSQL 15**                        | Initialised from [db.sql](app/helm/backend/db.sql)                    |

## Architecture

```mermaid
flowchart LR
    dev(["Developer"])
    src[("GitHub: source repos")]
    jenkins["Jenkins (CI)"]
    hub[("Docker Hub")]
    cfg[("GitHub: Helm config repos")]

    dev -->|"git push + tag vX.Y.Z"| src
    src -->|"webhook via ngrok"| jenkins
    jenkins -->|"build and push image:vX.Y.Z"| hub
    jenkins -->|"update image tag in values.yaml"| cfg

    subgraph k8s ["Kubernetes cluster (kubeadm: 1 master + 1 worker)"]
        argocd["ArgoCD (GitOps CD)"]
        fe["Frontend: nginx + Vue"]
        be["Backend: FastAPI"]
        db[("PostgreSQL")]
        prom["Prometheus"]
        promtail["Promtail"]
        loki["Loki"]
        tempo["Tempo"]
        grafana["Grafana"]

        argocd -->|"deploy"| fe
        argocd -->|"deploy"| be
        fe -->|"/api proxy"| be
        be --> db
        prom -->|"scrape /metrics"| be
        promtail -->|"collect logs"| be
        promtail --> loki
        be -->|"OTLP traces"| tempo
        grafana --> prom
        grafana --> loki
        grafana --> tempo
    end

    argocd -->|"pull and sync"| cfg
    fe -.->|"image pull"| hub
    be -.->|"image pull"| hub
```

- **CI (Jenkins):** a Git tag `vX.Y.Z` on a source repo triggers a pipeline. It builds the Docker image with the **Git tag as the image tag**, pushes it to Docker Hub, and commits that tag into the matching Helm config repo.
- **CD (ArgoCD, GitOps):** ArgoCD watches the config repos and automatically syncs the cluster to what is in Git.
- **Observability:** Prometheus (metrics), Loki + Promtail (logs) and Tempo + OpenTelemetry (traces), all visualised and **correlated** in Grafana.

## Repository layout

This is an umbrella repository; every component lives in its own Git repository, included as a **submodule**.

| Path | Repository | Content |
|------|------------|---------|
| [app/src/backend](app/src/backend) | [vdt-backend](https://github.com/duyanh221204/vdt-backend) | FastAPI source, `Dockerfile`, `Jenkinsfile` |
| [app/src/frontend](app/src/frontend) | [vdt-frontend](https://github.com/duyanh221204/vdt-frontend) | Vue source, `nginx.conf`, `Dockerfile`, `Jenkinsfile` |
| [app/helm/backend](app/helm/backend) | [vdt-backend-config](https://github.com/duyanh221204/vdt-backend-config) | Helm chart: backend + PostgreSQL + ServiceMonitor |
| [app/helm/frontend](app/helm/frontend) | [vdt-frontend-config](https://github.com/duyanh221204/vdt-frontend-config) | Helm chart: frontend |
| [cloud-observability](cloud-observability) | [vdt-cloud-observability](https://github.com/duyanh221204/vdt-cloud-observability) | ArgoCD apps + Helm values for Prometheus, Loki, Promtail, Tempo |
| [ci-cd](ci-cd) | *(this repo)* | Manifests for ArgoCD, Jenkins and the ArgoCD Applications |
| [scripts](scripts) | *(this repo)* | Helper scripts used by the docs |
| [docs](docs) | *(this repo)* | Step-by-step setup guide |

Clone everything at once:

```bash
git clone --recurse-submodules https://github.com/duyanh221204/vdt-devops.git
# or, in an existing clone
git submodule update --init --recursive
```

## Endpoints

| Service | URL |
|---------|-----|
| Frontend | http://192.168.192.136:30001 |
| Backend (Swagger UI) | http://192.168.192.136:30000/docs |
| Jenkins | http://192.168.192.136:32000 |
| ArgoCD | https://192.168.192.136:32002 |
| Grafana | http://192.168.192.136:32100 |
| Prometheus | http://192.168.192.136:32200 |

All services are exposed as `NodePort`, so any node IP works (`192.168.192.136` or `192.168.192.138`).

## Documentation

Start with **[docs/README.md](docs/README.md)**: it describes the environment and links to each step in order:

1. [Kubernetes cluster](docs/1-kubernetes-cluster.md)
2. [ArgoCD, first deployment and Jenkins](docs/2-argocd-and-jenkins.md)
3. [CI/CD pipeline](docs/3-ci-cd-pipeline.md)
4. [Cloud observability setup](docs/4-cloud-observability-setup.md)
5. [Metrics, logs, traces and their correlation](docs/5-metrics-logs-traces.md)
