resource "google_cloudfunctions_function" "generator" {
  name        = "Generator"
  description = "Generator for my pubsub test"
  runtime     = "python37"
  region      = local.region
  timeout     = 540

  available_memory_mb   = 128
  source_archive_bucket = google_storage_bucket.deployment_config.name
  source_archive_object = google_storage_bucket_object.generator_zip.name

  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource   = google_pubsub_topic.function_trigger_topic.id
  }
  entry_point = "main"
}

data "archive_file" "generator_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../generator"
  output_path = local.generator_zip_path
}

locals {
  generator_zip_path = "${path.module}/../artifacts/generator.zip"
}


resource "google_storage_bucket_object" "generator_zip" {
  source = local.generator_zip_path
  bucket = google_storage_bucket.deployment_config.name
  name   = "generator-${data.archive_file.generator_zip.output_md5}.zip"

  # archive must exist first
  depends_on = [data.archive_file.generator_zip]
}
