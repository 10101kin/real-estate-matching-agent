# Deployment Notes

This project ships with:
- `Dockerfile` (API container)
- `.dockerignore`
- `azure-pipelines.yml` (Verify -> Publish -> optional Deploy)

## Required Azure DevOps setup
1. Create service connection for ACR and set name in `acrServiceConnection`.
2. Create Azure RM service connection and set name in `azureSubscriptionServiceConnection`.
3. Update variables:
   - `containerRegistry`
   - `webAppName`
4. Use protected environment `prod-real-estate-event-registration` with approvals.
5. Keep `deployEnabled=false` by default; enable at run time when deployment is intended.

## Runtime contract in pipeline
- Health endpoint: `GET /health`
- API smoke test: `GET /api/v1/events`
- Container port: `8000`
