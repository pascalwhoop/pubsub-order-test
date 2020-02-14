provider "google" {
  credentials = file("account.json")
  project     = local.project
  region      = "europe-west1"
}


locals {
  project     = "quixotic-elf-256313"
}