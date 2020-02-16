resource "google_redis_instance" "cache" {
  name           = "appengine-memory-cache"
  tier           = "BASIC"
  memory_size_gb = 1

  region = local.region

  authorized_network = google_compute_network.redis-network.self_link

  redis_version = "REDIS_3_2"
  display_name  = "App Engine Pubsub experiment Cache"

}

// This example assumes this network already exists.
// The API creates a tenant network per network authorized for a
// Redis instance and that network is not deleted when the user-created
// network (authorized_network) is deleted, so this prevents issues
// with tenant network quota.
// If this network hasn't been created and you are using this example in your
// config, add an additional network resource or change
// this from "data"to "resource"
resource "google_compute_network" "redis-network" {
  name = "redis-test-network"
}

output "redis_ip" {
  value = google_redis_instance.cache.host
}