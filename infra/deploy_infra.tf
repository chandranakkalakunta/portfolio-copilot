resource "google_artifact_registry_repository" "containers" {
  location      = var.region
  repository_id = "containers"
  format        = "DOCKER"
  description   = "Container images for Portfolio Copilot"
}

resource "google_service_account" "run_app" {
  account_id   = "run-app"
  display_name = "Cloud Run runtime SA (Portfolio Copilot) — no roles for hello service"
}

resource "google_project_iam_member" "deployer_run_developer" {
  project = var.project_id
  role    = "roles/run.developer"
  member  = "serviceAccount:${google_service_account.gh_deployer.email}"
}

resource "google_project_iam_member" "deployer_ar_writer" {
  project = var.project_id
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${google_service_account.gh_deployer.email}"
}

resource "google_service_account_iam_member" "deployer_actas_runapp" {
  service_account_id = google_service_account.run_app.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.gh_deployer.email}"
}
