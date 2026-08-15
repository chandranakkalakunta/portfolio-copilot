# Analytical store (ADR-0004) — BigQuery dataset + tables + run-app IAM.

resource "google_project_service" "bigquery" {
  project            = var.project_id
  service            = "bigquery.googleapis.com"
  disable_on_destroy = false
}

resource "google_bigquery_dataset" "analytics" {
  project    = var.project_id
  dataset_id = "pcopilot_analytics"
  location   = "asia-south1"

  depends_on = [google_project_service.bigquery]
}

resource "google_bigquery_table" "valuation_snapshots" {
  project    = var.project_id
  dataset_id = google_bigquery_dataset.analytics.dataset_id
  table_id   = "valuation_snapshots"

  deletion_protection = true

  time_partitioning {
    type  = "DAY"
    field = "as_of"
  }

  clustering = ["portfolio_id"]

  schema = jsonencode([
    { name = "portfolio_id", type = "STRING", mode = "REQUIRED" },
    { name = "as_of", type = "TIMESTAMP", mode = "REQUIRED" },
    { name = "market_value", type = "NUMERIC", mode = "REQUIRED" },
    { name = "cash", type = "NUMERIC", mode = "NULLABLE" },
    { name = "cost_basis", type = "NUMERIC", mode = "NULLABLE" },
    { name = "twr", type = "NUMERIC", mode = "NULLABLE" },
    { name = "mwr", type = "NUMERIC", mode = "NULLABLE" },
    { name = "currency", type = "STRING", mode = "REQUIRED" },
    { name = "source", type = "STRING", mode = "REQUIRED" },
    { name = "created_at", type = "TIMESTAMP", mode = "REQUIRED" },
    { name = "schema_version", type = "INTEGER", mode = "REQUIRED" },
  ])
}

resource "google_bigquery_table" "recommendations" {
  project    = var.project_id
  dataset_id = google_bigquery_dataset.analytics.dataset_id
  table_id   = "recommendations"

  deletion_protection = true

  time_partitioning {
    type  = "DAY"
    field = "issued_at"
  }

  clustering = ["user_id", "ticker"]

  schema = jsonencode([
    { name = "rec_id", type = "STRING", mode = "REQUIRED" },
    { name = "user_id", type = "STRING", mode = "REQUIRED" },
    { name = "portfolio_id", type = "STRING", mode = "NULLABLE" },
    { name = "ticker", type = "STRING", mode = "REQUIRED" },
    { name = "market", type = "STRING", mode = "REQUIRED" },
    { name = "action", type = "STRING", mode = "REQUIRED" },
    { name = "rating", type = "STRING", mode = "REQUIRED" },
    { name = "price_at_issue", type = "NUMERIC", mode = "REQUIRED" },
    { name = "price_as_of", type = "TIMESTAMP", mode = "REQUIRED" },
    { name = "currency", type = "STRING", mode = "REQUIRED" },
    { name = "issued_at", type = "TIMESTAMP", mode = "REQUIRED" },
    { name = "note_ref", type = "STRING", mode = "NULLABLE" },
    { name = "model_attribution", type = "STRING", mode = "NULLABLE" },
    { name = "schema_version", type = "INTEGER", mode = "REQUIRED" },
  ])
}

resource "google_bigquery_dataset_iam_member" "run_app_analytics_editor" {
  project    = var.project_id
  dataset_id = google_bigquery_dataset.analytics.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.run_app.email}"
}

resource "google_project_iam_member" "run_app_bq_jobuser" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.run_app.email}"
}
