terraform {
  backend "gcs" {
    bucket = "pcopilot-dev-tfstate"
    prefix = "infra/dev"
  }
}
