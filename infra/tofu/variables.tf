variable "project_name" {
  description = "Name of the project used for naming resources"
  type        = string
  default     = "edu-viewer"
}

variable "location" {
  description = "Azure region to deploy resources"
  type        = string
  default     = "centralindia"
}

variable "container_image" {
  description = "The container image to deploy (e.g., ghcr.io/username/educative-viewer:latest)"
  type        = string
}

variable "auth_token" {
  description = "Token for authentication"
  type        = string
  sensitive   = true
}

variable "download_token" {
  description = "Token for downloads"
  type        = string
  sensitive   = true
}

variable "secret_key" {
  description = "Flask secret key"
  type        = string
  sensitive   = true
  default     = "change-me-in-production"
}
