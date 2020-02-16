variable "project_id" {

}

variable "apis" {
    
    type = list(string)
    default = [
        # make sure you ALWAYS APPEND at the END
        "cloudfunctions.googleapis.com",
        "pubsub.googleapis.com",
        "appengine.googleapis.com",
        "cloudscheduler.googleapis.com"
    ]
}

resource "google_project_service" "project" {
    count = length(var.apis)
    project = var.project_id
    service = var.apis[count.index]
    disable_dependent_services = true
    disable_on_destroy = true
}