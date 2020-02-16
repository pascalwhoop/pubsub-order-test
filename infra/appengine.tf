resource "google_app_engine_application" "reader" {
  project     = local.project
  location_id = "europe-west"
}

resource "google_app_engine_standard_app_version" "reader" {
  version_id     = formatdate("YYYYMMDD't'hhmmss",timestamp())
  service        = "default"
  runtime        = "python37"
  instance_class = "F1"

  entrypoint {
    shell = "gunicorn -b :$PORT main:app --log-level=DEBUG"
  }
  noop_on_destroy = true

  env_variables = {
    redis_host = google_redis_instance.cache.host
    redis_port = google_redis_instance.cache.port

  }

  deployment {
    zip {
      source_url = "https://storage.googleapis.com/${google_storage_bucket.deployment_config.name}/${google_storage_bucket_object.reader_zip.name}"
    }
  }
  # archive must exist first
  depends_on = [google_storage_bucket_object.reader_zip]
}

resource "google_vpc_access_connector" "connector" {
  name          = "appengine-connector"
  provider      = google-beta
  region        = local.region
  network       = google_compute_network.redis-network.name
  ip_cidr_range = var.appengine_cidr_range
}



data "archive_file" "reader_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../reader"
  output_path = local.reader_zip_path
}

locals {
  reader_zip_path = "${path.module}/../artifacts/reader.zip"
}


resource "google_storage_bucket_object" "reader_zip" {
  source = local.reader_zip_path
  bucket = google_storage_bucket.deployment_config.name
  name   = "reader-${data.archive_file.reader_zip.output_md5}.zip"

  # archive must exist first
  depends_on = [data.archive_file.reader_zip]
}
