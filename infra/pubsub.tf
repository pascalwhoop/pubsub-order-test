
resource "google_pubsub_topic" "default-topic" {
  name = "queue_topic"
}

resource "google_pubsub_subscription" "default" {
  name  = "default-subscription"
  topic = google_pubsub_topic.default-topic.name

  push_config {
    push_endpoint = "https://${google_app_engine_application.reader.default_hostname}/push"
  }
}

resource "google_pubsub_topic" "function_trigger_topic" {
  name = "function_trigger_topic"
}