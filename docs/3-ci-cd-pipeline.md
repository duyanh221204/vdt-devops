# 3. CI/CD Pipeline with Jenkins and GitOps

This step connects everything from step 2. A developer pushes a version tag `vX.Y.Z`, and the new version ends up running in the cluster with no manual action.

## Concepts

**CI/CD** automates the repetitive steps between a code change and a running release:

| Part | Role |
|------|------|
| **CI** (Continuous Integration) | Integrate the change, build, test/analyse if any, and package a versioned **artifact** (here: a Docker image) |
| **CD** (Continuous Delivery) | Bring the artifact to a state that is ready to deploy. The final deploy is still approved or triggered by hand |
| **CD** (Continuous Deployment) | Deploy the artifact automatically as soon as the pipeline succeeds |

There are two ways to get the artifact into the cluster:

| | Push-based (classic CI/CD) | Pull-based (GitOps) |
|---|---|---|
| Who deploys | The CI server pushes to the cluster (`kubectl`, `helm`, SSH) | An agent inside the cluster pulls the desired state from Git |
| Credentials | The CI server must store cluster credentials (kubeconfig, SSH keys) | Cluster credentials never leave the cluster |
| Drift | Not detected: manual changes stay | Detected and reverted (continuous reconciliation) |
| History / rollback | Spread across pipeline logs | Git history; rollback = `git revert` |

This project **combines both**:

- **Jenkins** does CI and stops at Git: it updates the image tag in the config repo.
- **ArgoCD** does the deployment, pulling from Git.

Jenkins never touches the cluster.

## Versioning: the Git tag is the image tag

A release has **one version number**: the Git tag `vX.Y.Z` pushed on the source repo. The same value is used as:

| Where | Example (backend `v1.2.0`) |
|-------|----------------------------|
| Git tag on the source repo | `vdt-backend` → `refs/tags/v1.2.0` |
| Docker image tag | `nguyenduyanh221204/vdt-backend:v1.2.0` |
| `image.tag` in the config repo | `vdt-backend-config/values.yaml` → `tag: v1.2.0` |

Images are never tagged `latest`. Every running Pod therefore points to an exact image, and every image points to an exact commit. Rolling back means moving `image.tag` to an earlier version.

## Flow

```mermaid
sequenceDiagram
    autonumber
    actor Dev as Developer
    participant SRC as GitHub<br/>vdt-backend / vdt-frontend
    participant NG as ngrok
    participant J as Jenkins
    participant HUB as Docker Hub
    participant CFG as GitHub<br/>vdt-*-config
    participant A as ArgoCD
    participant K as Kubernetes

    Dev->>SRC: git push (code) + git push origin vX.Y.Z
    SRC->>NG: webhook POST /github-webhook/ (ref: refs/tags/vX.Y.Z)
    NG->>J: forward to 192.168.192.136:32000
    J->>SRC: checkout the tag
    J->>J: check tag format and that it is greater than the current tag
    J->>HUB: docker build + push image:vX.Y.Z (Git tag = image tag)
    J->>CFG: sed image.tag in values.yaml, commit, push
    A->>CFG: poll, detect new commit (OutOfSync)
    A->>K: automated sync: helm template + apply
    K->>HUB: pull image:vX.Y.Z, rolling update
```

## 3.1 Jenkins credentials

The pipelines need two **Username with password** credentials, created in *Manage Jenkins → Credentials → System → Global credentials*. Their IDs must match the ones used in the Jenkinsfiles:

| ID | Username | Password | Used for |
|----|----------|----------|----------|
| `docker-hub-credentials` | Docker Hub user (`nguyenduyanh221204`) | Docker Hub **access token** | `docker login` and `docker push` |
| `github-credentials` | GitHub user (`duyanh221204`) | GitHub **Personal Access Token** (scope `repo`) | Clone and push the config repos |

![Docker Hub credential](../images/3-cred-dockerhub.png)

![GitHub credential](../images/3-cred-github.png)

![Credentials list](../images/3-credentials.png)

## 3.2 Expose Jenkins to GitHub with ngrok

Jenkins is only reachable on the private VM network, so GitHub cannot deliver webhooks to it directly. **ngrok** runs on the Windows host and opens a public HTTPS tunnel to the Jenkins NodePort:

```powershell
ngrok http 192.168.192.136:32000
```

![ngrok tunnel](../images/3-ngrok.png)

The `Forwarding` URL (`https://<subdomain>.ngrok-free.dev`) is the public address of Jenkins. On the free plan this URL can change when ngrok restarts. If it changes, update the webhooks.

## 3.3 GitHub webhooks

Add a webhook on **each source repo** (`vdt-backend` and `vdt-frontend`) under *Settings → Webhooks → Add webhook*:

| Field | Value |
|-------|-------|
| Payload URL | `https://<ngrok-domain>/github-webhook/`. This endpoint is provided by the Jenkins GitHub plugin; keep the trailing `/` |
| Content type | `application/json` |
| SSL verification | Enabled |
| Events | *Let me select individual events* → **Pushes** and **Branch or tag creation** |

Backend repo (`vdt-backend`):

![Backend webhook](../images/3-backend-webhook.png)

Frontend repo (`vdt-frontend`), same settings:

![Frontend webhook](../images/3-frontend-webhook.png)

## 3.4 Pipeline jobs

There is one **Pipeline** job per app: `vdt-backend-pipeline` and `vdt-frontend-pipeline`. Both use the same settings; only the repository URL differs:

| Section | Setting |
|---------|---------|
| Triggers | **GitHub hook trigger for GITScm polling** |
| Pipeline → Definition | Pipeline script from SCM |
| SCM | Git, Repository URL `https://github.com/duyanh221204/vdt-backend.git` / `vdt-frontend.git`. No credentials, because the repos are public |
| Branch Specifier | `refs/tags/*` |
| Script Path | `Jenkinsfile` |
| Lightweight checkout | **unchecked** |

- **GitHub hook trigger for GITScm polling:** when the webhook arrives, Jenkins checks the repository for refs that match the job's specifier. It starts a build only for refs it has not built yet.
- **Branch Specifier `refs/tags/*`:** only **tags** match, so ordinary commits pushed to `main` never start a build.
- **Lightweight checkout:** with this option on, Jenkins reads only the `Jenkinsfile` through the SCM API. That does not work with the `refs/tags/*` specifier.

### Backend job

*New Item → Pipeline*, named `vdt-backend-pipeline`:

![New backend pipeline](../images/3-backend-new-job.png)

![Backend trigger](../images/3-backend-job-trigger.png)

![Backend SCM](../images/3-backend-job-scm.png)

![Backend branch specifier and script path](../images/3-backend-job-branch.png)

### Frontend job

The frontend job, `vdt-frontend-pipeline`, is created the same way, with the `vdt-frontend` repository:

![New frontend pipeline](../images/3-frontend-new-job.png)

![Frontend trigger](../images/3-frontend-job-trigger.png)

![Frontend SCM](../images/3-frontend-job-scm.png)

![Frontend branch specifier and script path](../images/3-frontend-job-branch.png)

Both jobs on the Jenkins dashboard:

![Jenkins pipelines](../images/3-jenkins-pipelines.png)

## 3.5 The pipeline (Jenkinsfile)

The pipeline is defined in each source repo:

- [app/src/backend/Jenkinsfile](../app/src/backend/Jenkinsfile)
- [app/src/frontend/Jenkinsfile](../app/src/frontend/Jenkinsfile)

The two files are identical except for `DOCKER_IMAGE` and `CONFIG_REPO_URL`.

| Stage | Purpose |
|-------|---------|
| Checkout Source Code | Check out the tagged revision |
| Check Git Tag | The build must come from a tag. The tag must match `^v\d+\.\d+\.\d+$` and be **strictly greater** (`sort -V`) than `image.tag` in the config repo's `values.yaml` |
| Build and Push Docker Image | `docker build` and `docker push` `<image>:<tag>` to Docker Hub, where `<tag>` is the **Git tag** |
| Update Config Repo | Replace `tag:` in `values.yaml` with the Git tag, then commit `Update image tag to <tag> via Jenkins Pipeline` as `Jenkins CI` and push to `main` |
| Post | Clean the workspace |

The tag check makes every release reach the cluster as a new, higher version. A re-pushed or older tag fails early, before anything is built.

## 3.6 Releasing a new version

In a source repo, after committing the change:

```bash
git push origin main
git tag v1.2.0
git push origin v1.2.0
```

Then, for each release:

1. The webhook delivers a `push` event for `refs/tags/vX.Y.Z`.
2. Jenkins runs the pipeline.
3. The image is pushed to Docker Hub.
4. Jenkins commits the new tag to the config repo.
5. ArgoCD syncs.
6. The Pod is replaced with the new image.

The two releases below show this for each app.

### Backend release `v1.2.0`

The change (the root message in `main.py`) is committed, tagged and pushed:

![Commit, tag and push](../images/3-backend-release-tag.png)

**1. Webhook delivered.** GitHub sends a `push` event with `"ref": "refs/tags/v1.2.0"`, and Jenkins answers `200`:

![Backend webhook delivery](../images/3-backend-webhook-delivery.png)

**2. Pipeline runs.** The build shows *Started by GitHub push* and checks out `refs/tags/v1.2.0`:

![Backend stage view](../images/3-backend-stages.png)

![Backend console](../images/3-backend-console.png)

**3. Image pushed** to Docker Hub with the Git tag as image tag:

![Backend Docker Hub tags](../images/3-backend-dockerhub.png)

**4. Config repo updated** by `Jenkins CI`. Only `image.tag` changes, from `v1.1.2` to `v1.2.0`:

![Backend config repo commit](../images/3-backend-config-commit.png)

**5. ArgoCD syncs.** ArgoCD polls the config repo (about every 3 minutes by default). It sees the new commit (`OutOfSync`), runs an automated sync, and the app returns to `Synced` / `Healthy`. Every deployment is recorded with its Git revision:

![Backend ArgoCD history](../images/3-backend-argocd-history.png)

![Backend ArgoCD sync events](../images/3-backend-argocd-events.png)

**6. Rolling update.** The new Pod pulls `vdt-backend:v1.2.0` on the worker:

![Backend pod events](../images/3-backend-pod-events.png)

**7. New version live:** `GET /` returns the new message:

![Backend new version](../images/3-backend-new-version.png)

### Frontend release `v1.0.1`

The change (removing the role badge from the header) is released the same way, with tag `v1.0.1` on `vdt-frontend`.

**1. Webhook delivered.** One tag push produces a `create` event and a `push` event. Jenkins reacts to the `push`:

![Frontend webhook deliveries](../images/3-frontend-webhook-deliveries.png)

![Frontend webhook delivery](../images/3-frontend-webhook-delivery.png)

**2. Pipeline runs** on `refs/tags/v1.0.1`:

![Frontend console](../images/3-frontend-console.png)

**3. Image pushed** as `vdt-frontend:v1.0.1`, the same tag as the Git tag:

![Frontend Docker Hub tags](../images/3-frontend-dockerhub.png)

**4. Config repo updated**, from `v1.0.0` to `v1.0.1`:

![Frontend config repo commit](../images/3-frontend-config-commit.png)

**5. ArgoCD syncs** to the new commit:

![Frontend ArgoCD tree](../images/3-frontend-argocd-tree.png)

![Frontend ArgoCD sync events](../images/3-frontend-argocd-events.png)

**6. Rolling update.** The new Pod pulls `vdt-frontend:v1.0.1`:

![Frontend pod events](../images/3-frontend-pod-events.png)

**7. New version live:** the role badge is gone from the header:

![Frontend new version](../images/3-frontend-new-version.png)

## 3.7 Rollback

Git is the source of truth, and `selfHeal` reverts any manual change in the cluster. So a rollback is done **in the config repo**:

```bash
# in vdt-backend-config (or vdt-frontend-config)
git revert <commit-of-the-release-to-roll-back>
git push origin main
```

ArgoCD then syncs back to the previous image tag. The *History and Rollback* panel in ArgoCD can also roll back, but only while auto-sync is disabled.

After the revert, `values.yaml` holds the previous tag again. The next release must use a version **higher than the one that was rolled back**, so an existing image tag on Docker Hub is never overwritten.

## 3.8 Troubleshooting

| Symptom | Cause / fix |
|---------|-------------|
| Build fails at *Check Git Tag*: "Không phải Tag hợp lệ" | The build was not started from a tag (e.g. *Build Now* on a branch). Push a tag instead |
| *Check Git Tag*: invalid format | The tag is not `vX.Y.Z` (e.g. `v1.2`, `1.2.0`) |
| *Check Git Tag*: new tag must be greater | The tag is equal to or lower than `image.tag` in the config repo. Use a higher version |
| *Build and Push* fails: `permission denied ... docker.sock` | The socket override from [step 2.1](2-argocd-and-jenkins.md#21-prepare-the-worker-node) is missing, or Docker restarted without it. Check `ls -l /var/run/docker.sock` on the worker (`srw-rw-rw-`) |
| *Build and Push* fails: `docker: not found` | The CLI is missing from `/var/jenkins_home` (see [step 2.5](2-argocd-and-jenkins.md#25-let-jenkins-build-docker-images)) |
| Webhook delivery fails (non-200) | ngrok is not running, or its URL changed. Restart ngrok and update the Payload URL |
| Webhook OK but no build | The job trigger is not enabled, the Branch Specifier is not `refs/tags/*`, or Lightweight checkout is on |
| ArgoCD does not pick up the new tag | Wait for the poll interval or click *Refresh*. Check that the Jenkins commit reached the config repo |

Next: [4. Cloud observability setup](4-cloud-observability-setup.md)
