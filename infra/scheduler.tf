resource "google_cloud_scheduler_job" "job" {
  name        = "test-trigger-job"
  description = "trigger job"
  schedule    = "0 */1 * * *"

  pubsub_target {
    # topic.id is the topic's full resource name.
    topic_name = google_pubsub_topic.function_trigger_topic.id
    data       = base64encode("GO!")
  }

  depends_on = [google_app_engine_application.reader]
}
