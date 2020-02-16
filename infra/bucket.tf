resource "google_storage_bucket" "deployment_config" {
  bucket_policy_only = true
  force_destroy      = true
  name               = "deployment-config-${local.project}"
  requester_pays     = false
  storage_class      = "STANDARD"
}