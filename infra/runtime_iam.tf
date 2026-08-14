resource "google_project_iam_member" "run_app_datastore" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.run_app.email}"
}

resource "google_project_iam_member" "run_app_aiplatform" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.run_app.email}"
}

resource "google_project_iam_member" "run_app_run_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.run_app.email}"
}

resource "google_service_account" "mcp_run" {
  account_id   = "mcp-run"
  display_name = "Cloud Run runtime SA for MCP services (no roles)"
}

resource "google_service_account_iam_member" "deployer_actas_mcprun" {
  service_account_id = google_service_account.mcp_run.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.gh_deployer.email}"
}
