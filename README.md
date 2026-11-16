# myapp

A small Python web API used to demonstrate a complete Kubernetes CI/CD pipeline:
GitHub Actions builds, tests, scans and signs the image; Argo CD deploys it from the
companion [`platform-config`](../platform-config) repo using GitOps.

```text
developer ─► PR ─► CI (test, SAST, deps scan, chart lint, build, image scan)
                         │ merge to main
                         ▼
               push image to GHCR (tag = commit SHA) + sign + SBOM
                         │
                         ▼
          bump envs/dev/myapp/values.yaml in platform-config
                         │
                         ▼
              Argo CD syncs the cluster (myapp-dev)
```

## Layout

| Path | What it is |
| --- | --- |
| `src/main.py` | FastAPI app with `/`, `/healthz`, `/readyz`, `/metrics` |
| `tests/` | Unit tests (pytest) |
| `Dockerfile` | Multi-stage, non-root image |
| `chart/` | Helm chart: Deployment, Service, Ingress, HPA, PDB |
| `.github/workflows/ci.yml` | The CI pipeline |

## Run locally

```bash
pip install -r requirements-dev.txt
pytest
uvicorn src.main:app --port 8080

docker build --build-arg APP_VERSION=local -t myapp:local .
docker run --rm -p 8080:8080 myapp:local
curl localhost:8080/healthz

helm template myapp chart/ --set image.tag=local
```

## One-time setup

1. **Config repo token.** Create a fine-grained personal access token with
   *Contents: read and write* on the `platform-config` repo only, then:
   ```bash
   gh secret set CONFIG_REPO_TOKEN --repo <you>/myapp
   ```
   Without it the pipeline still builds and pushes the image, and skips the deploy bump with a warning.
2. **Image visibility.** After the first push, open the `myapp` package on GitHub
   (Profile → Packages) and set it to **Public** so a lab cluster can pull it,
   or add an image pull secret (`imagePullSecrets` in the chart values).
3. **Branch protection** on `main`: require a PR and the `ci` checks to pass.

## Pipeline stages

| Job | Runs on | Purpose |
| --- | --- | --- |
| `test` | every PR and push | ruff lint, pytest, 80% coverage floor |
| `sast` | every PR and push | Semgrep static analysis |
| `deps-scan` | every PR and push | Trivy: library CVEs and leaked secrets |
| `chart-lint` | every PR and push | `helm lint` and `helm template` |
| `build` | after all checks | Build, scan the image; on `main` push, attach SBOM and sign |
| `update-config` | `main` only | Write the new SHA to the dev values in `platform-config` |
