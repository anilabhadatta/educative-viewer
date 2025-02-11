output "app_url" {
  description = "The URL of the deployed container app"
  value       = "https://${azurerm_container_app.app.ingress[0].fqdn}"
}

output "storage_account_name" {
  description = "Storage account name for manual uploads"
  value       = azurerm_storage_account.storage.name
}

output "file_share_name" {
  description = "File share name for manual uploads"
  value       = azurerm_storage_share.share.name
}
