// POC placeholder for Azure IaC.
// Intended resources: App Service (API), Static Web App/App Service (frontend), Azure SQL, Blob Storage.
param location string = resourceGroup().location
param environmentName string = 'poc'

output summary string = 'Define API host, frontend host, Azure SQL and Blob Storage resources here for environment ${environmentName} in ${location}.'
