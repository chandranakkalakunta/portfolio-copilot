# Default Firestore database (native mode). Import existing DB into state; never destroy via TF.

resource "google_firestore_database" "default" {
  project     = var.project_id
  name        = "(default)"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"

  # ABANDON: Terraform will not delete the database on destroy (data safety).
  deletion_policy = "ABANDON"

  depends_on = [google_project_service.firestore]
}
