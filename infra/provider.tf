provider "google" {
  credentials = file("account.json")
  project     = local.project
  region      = "europe-west1"
}
provider "google-beta" {
  credentials = file("account.json")
  project     = local.project
  region      = "europe-west1"
}



locals {
  project = "quixotic-elf-256313"
  region  = "europe-west1"
}

module "apis" {
  source     = "./apis"
  project_id = local.project
}