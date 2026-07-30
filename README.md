# ledger-api

Payments microservice for tokenising PANs and serving transaction metadata.
Deployed on Kubernetes in the `payments` namespace.

## Secure CI/CD and GitOps flow

The repository now uses a GitHub Actions pipeline that enforces security gates before an image is published, signed, and rolled out.

### Security gate policy

| Gate | Tool | Hard block | Warning-only | Notes |
|---|---|---|---|---|
| SAST | Semgrep | Yes | No | Any violation blocks the run and uploads SARIF to the repository Security tab. |
| Dependency/CVE scan | Trivy filesystem scan | Yes for HIGH/CRITICAL | MEDIUM/LOW | A vulnerability with no fix yet blocks deployment until the base image or dependency is upgraded. |
| Image scan | Trivy image scan | Yes for HIGH/CRITICAL | MEDIUM/LOW | The pipeline refuses to push or deploy an image that still has unresolved critical findings. |
| Secret scan | Gitleaks | Yes | No | Any detected secret blocks the build. |
| Image signing | Cosign keyless | Yes | No | The workflow signs the image and creates an SLSA-style attestation before deployment. |

### GitOps and drift handling

The workflow updates the image tag inside the deployment manifest and pushes the change back to the repository. Argo CD watches the repository and applies the desired state. The application manifest in [deploy/argocd/application.yaml](deploy/argocd/application.yaml) enables automated sync and self-heal with `selfHeal: true`.

A manual edit such as `kubectl edit deployment/ledger-api -n payments` will be detected as drift, and Argo CD will revert the cluster back to the Git state automatically.

### Bonus capabilities

- SARIF results from Semgrep and Trivy are uploaded to GitHub Security.
- `cosign verify` is executed in CI to prove that the published image was signed by the workflow.
- The deployment uses a rolling update strategy for safer rollout progression.

## Endpoints

| Method | Path            | Description                          |
|--------|-----------------|--------------------------------------|
| GET    | `/health`       | Liveness check                       |
| POST   | `/tokenize`     | `{"pan": "..."}` → opaque token      |
| GET    | `/transactions` | Recent transaction records           |
| POST   | `/import`       | Import a YAML configuration blob     |
| GET    | `/fetch?url=`   | Fetch a remote resource by URL       |
