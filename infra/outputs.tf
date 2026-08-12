output "workload_identity_provider" {
  value = google_iam_workload_identity_pool_provider.github.name
}
output "deployer_service_account" {
  value = google_service_account.gh_deployer.email
}
output "artifact_registry_repo" {
  value = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.containers.repository_id}"
}
output "runtime_service_account" {
  value = google_service_account.run_app.email
}
