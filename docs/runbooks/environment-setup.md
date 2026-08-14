# Environment setup (minimal-manual install)

Goal: a new GCP environment (dev / test / prod) is reproducible via Terraform after a small bootstrap. **Everything else is `terraform apply`.**

Aligned with O6 (IaC) and Phase 2.3.1.

## Residual manual steps (bootstrap only)

Do these **once per environment**, before the first `terraform apply`:

### (a) Create the GCP project

```bash
gcloud projects create <PROJECT_ID> --name="<display name>"
# or use an existing empty project
```

### (b) Link billing

```bash
gcloud billing projects link <PROJECT_ID> --billing-account=<BILLING_ACCOUNT_ID>
```

### (c) Terraform state bucket (bootstrap; not managed by this stack yet)

```bash
gcloud storage buckets create gs://<PROJECT_ID>-tfstate \
  --project=<PROJECT_ID> \
  --location=<REGION> \
  --uniform-bucket-level-access
# Enable versioning on the bucket (recommended for state)
gcloud storage buckets update gs://<PROJECT_ID>-tfstate --versioning
```

Point `infra/backend.tf` (or a backend config file) at this bucket and prefix before `terraform init`.

### (d) Google Sign-In OAuth (console only — Google limitation)

Identity Platform / Firebase Auth needs a **Web OAuth client** and **OAuth consent screen** configured in Google Cloud Console. This cannot be fully automated without org-level constraints:

1. **OAuth consent screen** (APIs & Services → OAuth consent screen): external or internal; app name; support email; authorized domains if needed.
2. **Web OAuth client** (APIs & Services → Credentials → Create credentials → OAuth client ID → Web application): authorized JavaScript origins + redirect URIs for the app (local + Cloud Run URLs).
3. Wire the client into **Identity Platform / Firebase Auth** Google provider.
4. Authorized **JavaScript origin** for local e2e: `http://localhost:8000` (and the Cloud Run origin when deployed). Redirect URI is the Firebase handler (`https://<project>.firebaseapp.com/__/auth/handler`).
5. Export the public web client values (browser-safe; not service-account secrets):

   ```bash
   export PCOPILOT_FIREBASE_API_KEY="..."
   export PCOPILOT_FIREBASE_AUTH_DOMAIN="<project>.firebaseapp.com"
   export PCOPILOT_FIREBASE_PROJECT_ID="<project>"
   export PCOPILOT_AUTH_BACKEND=firebase
   export PCOPILOT_REPO_BACKEND=firestore
   ```

   The API exposes these via `GET /config` for the vanilla UI (`web/`). Never hardcode them.

The backend AuthPort verifies ID tokens; the UI (`signInWithPopup`) is the real-token e2e path (Phase 2.6).

## Everything else: Terraform

From `infra/` (with ADC / WIF credentials that can manage the project):

```bash
cd infra
terraform init
# First-time only if resources already exist imperatively:
#   terraform import google_firestore_database.default "projects/<PROJECT_ID>/databases/(default)"
terraform plan
terraform apply   # after Strategist review for risk-sensitive changes
```

This stack codifies (non-exhaustive):

| Area | Resources |
|------|-----------|
| APIs | `google_project_service` — Run, Artifact Registry, IAM, STS, CRM, Service Usage, AI Platform, Firestore, Identity Toolkit, … |
| Identity (CI) | Workload Identity Pool + GitHub OIDC provider + `gh-deployer` SA (WIF) |
| Deploy | Artifact Registry `containers`, runtime SA `run-app`, scoped deployer roles |
| Data | Firestore `(default)` database (`FIRESTORE_NATIVE`, `deletion_policy = ABANDON`) |

## Not in Terraform yet (follow-ups)

- Cloud Run services for API + MCP HTTP microservices (later deploy phases)
- Firestore security rules + composite indexes
- Identity Platform Google-provider config (with OAuth client — 2.6)
- Import of the bootstrap state bucket itself

## Safety notes

- **Never** create service-account keys (org policy; keyless only — ADR-0009).
- Firestore `deletion_policy = ABANDON` — Terraform destroy will **not** delete the database.
- `disable_on_destroy = false` on APIs — destroy will **not** disable APIs.
