
resource "google_app_engine_application" "reader" {
  project     = local.project
  location_id = "us-central"
}
