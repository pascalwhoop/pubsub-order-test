resource "google_cloud_scheduler_job" "job" {
  name        = "test-trigger-job"
  description = "trigger job"
  schedule    = "0 */6 * * *"

  pubsub_target {
    # topic.id is the topic's full resource name.
    topic_name = google_pubsub_topic.function_trigger_topic.id
    data       = base64encode("GO!")
  }
}
