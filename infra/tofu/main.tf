resource "azurerm_resource_group" "rg" {
  name     = "${var.project_name}-rg"
  location = var.location
}

resource "azurerm_storage_account" "storage" {
  name                     = replace("${var.project_name}storage", "-", "")
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_share" "share" {
  name                 = "edu-share"
  storage_account_name = azurerm_storage_account.storage.name
  quota                = 50
}

resource "azurerm_log_analytics_workspace" "law" {
  name                = "${var.project_name}-law"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_container_app_environment" "env" {
  name                       = "${var.project_name}-env"
  location                   = azurerm_resource_group.rg.location
  resource_group_name        = azurerm_resource_group.rg.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.law.id
}

resource "azurerm_container_app_environment_storage" "storage_mount" {
  name                         = "edu-mount"
  container_app_environment_id = azurerm_container_app_environment.env.id
  account_name                 = azurerm_storage_account.storage.name
  share_name                   = azurerm_storage_share.share.name
  access_key                   = azurerm_storage_account.storage.primary_access_key
  access_mode                  = "ReadWrite"
}

resource "azurerm_container_app" "app" {
  name                         = var.project_name
  container_app_environment_id = azurerm_container_app_environment.env.id
  resource_group_name          = azurerm_resource_group.rg.name
  revision_mode                = "Single"

  template {
    container {
      name   = "viewer"
      image  = var.container_image
      cpu    = 0.25
      memory = "0.5Gi"

      env {
        name  = "FLASK_APP"
        value = "__init__.py"
      }
      env {
        name  = "COURSE_DIR"
        value = "/mnt/azure/courses"
      }
      env {
        name  = "EDUCATIVE_VIEWER_ROOT"
        value = "/mnt/azure/data"
      }
      env {
        name  = "AUTHTOKEN"
        value = var.auth_token
      }
      env {
        name  = "DOWNLOADTOKEN"
        value = var.download_token
      }
      env {
        name  = "SECRET_KEY"
        value = var.secret_key
      }

      volume_mounts {
        name = "edu-volume"
        path = "/mnt/azure"
      }
    }

    volume {
      name         = "edu-volume"
      storage_name = azurerm_container_app_environment_storage.storage_mount.name
      storage_type = "AzureFile"
    }

    min_replicas = 0
    max_replicas = 1
  }

  ingress {
    external_enabled = true
    target_port      = 5001
    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }
}
