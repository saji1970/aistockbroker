# Google Cloud Platform Setup Guide

This guide will help you set up Google Cloud Platform for deploying the AI Stock Trading System.

## Prerequisites

- Google Cloud Platform account
- Billing enabled on your GCP project
- Local development environment with required tools

## Step 1: Create GCP Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project details:
   - **Project name**: `ai-stock-trading-system`
   - **Project ID**: `ai-stock-trading-{your-unique-id}`
   - **Organization**: Select your organization (if applicable)
4. Click "Create"

## Step 2: Enable Required APIs

Enable the following APIs in your GCP project:

```bash
# Cloud Run API
gcloud services enable run.googleapis.com

# Container Registry API
gcloud services enable containerregistry.googleapis.com

# Cloud Build API
gcloud services enable cloudbuild.googleapis.com

# Cloud Scheduler API
gcloud services enable cloudscheduler.googleapis.com

# Cloud Storage API
gcloud services enable storage.googleapis.com

# Cloud Monitoring API
gcloud services enable monitoring.googleapis.com

# Cloud Logging API
gcloud services enable logging.googleapis.com
```

## Step 3: Create Service Account

1. Go to IAM & Admin → Service Accounts
2. Click "Create Service Account"
3. Enter details:
   - **Name**: `ai-stock-trading-deployer`
   - **Description**: `Service account for AI Stock Trading System deployment`
4. Grant the following roles:
   - Cloud Run Admin
   - Storage Admin
   - Cloud Build Editor
   - Cloud Scheduler Admin
   - Monitoring Admin
   - Logging Admin
5. Click "Create and Continue"
6. Click "Done"

## Step 4: Generate Service Account Key

1. Find your service account in the list
2. Click on the service account name
3. Go to "Keys" tab
4. Click "Add Key" → "Create new key"
5. Select "JSON" format
6. Click "Create"
7. Save the downloaded JSON file securely

## Step 5: Configure GitHub Secrets

Add the following secrets to your GitHub repository:

### Required Secrets

1. **GCP_SA_KEY**: Base64 encoded service account JSON key
   ```bash
   base64 -i path/to/service-account-key.json
   ```

2. **GCP_PROJECT_ID**: Your GCP project ID
   ```
   ai-stock-trading-{your-unique-id}
   ```

3. **GCP_SA_EMAIL**: Service account email
   ```
   ai-stock-trading-deployer@ai-stock-trading-{your-unique-id}.iam.gserviceaccount.com
   ```

### API Keys (Optional - for external services)

4. **GOOGLE_API_KEY**: Google API key for Gemini
5. **ALPHA_VANTAGE_API_KEY**: Alpha Vantage API key
6. **FINNHUB_API_KEY**: Finnhub API key
7. **MARKETSTACK_API_KEY**: Marketstack API key

### Optional Secrets

8. **CUSTOM_DOMAIN**: Custom domain for production
9. **PRODUCTION_DOMAIN**: Production domain
10. **ALERT_EMAIL**: Email for monitoring alerts
11. **SLACK_WEBHOOK**: Slack webhook for notifications

## Step 6: Set Up GitHub Environments

1. Go to your GitHub repository
2. Navigate to Settings → Environments
3. Create the following environments:

### Staging Environment
- **Name**: `staging`
- **Protection rules**: None (for automatic deployments)

### Production Environment
- **Name**: `production`
- **Protection rules**:
  - Required reviewers: Add team members
  - Wait timer: 5 minutes
  - Restrict deployments to main branch

## Step 7: Configure Local Development

### Install Google Cloud SDK

```bash
# macOS
brew install google-cloud-sdk

# Windows
# Download from https://cloud.google.com/sdk/docs/install

# Linux
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### Authenticate with GCP

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud auth configure-docker
```

## Step 8: Test Deployment

### Manual Deployment

```bash
# Make scripts executable
chmod +x deployment/scripts/*.sh

# Deploy to staging
./deployment/scripts/deploy-staging.sh

# Deploy to production (requires confirmation)
./deployment/scripts/deploy-production.sh
```

### GitHub Actions Deployment

1. Push to `master` branch for automatic staging deployment
2. Use "Actions" tab to manually trigger production deployment
3. Monitor deployment progress in the Actions tab

## Step 9: Monitor and Maintain

### Cloud Console Monitoring

1. **Cloud Run**: Monitor service health and performance
2. **Cloud Logging**: View application logs
3. **Cloud Monitoring**: Set up alerts and dashboards
4. **Cloud Storage**: Monitor data storage usage

### Cost Management

1. Set up billing alerts
2. Monitor resource usage
3. Use committed use discounts for predictable workloads
4. Implement auto-scaling to optimize costs

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify service account key is correct
   - Check service account permissions
   - Ensure APIs are enabled

2. **Build Failures**
   - Check Dockerfile syntax
   - Verify all dependencies are included
   - Review build logs in Cloud Build

3. **Deployment Failures**
   - Check Cloud Run service limits
   - Verify environment variables
   - Review service logs

4. **Permission Errors**
   - Ensure service account has required roles
   - Check IAM policies
   - Verify project permissions

### Useful Commands

```bash
# Check service status
gcloud run services list

# View service logs
gcloud run services logs read SERVICE_NAME --region=us-central1

# Update service configuration
gcloud run services update SERVICE_NAME --region=us-central1

# Delete service
gcloud run services delete SERVICE_NAME --region=us-central1
```

## Security Best Practices

1. **Use least privilege principle** for service accounts
2. **Rotate service account keys** regularly
3. **Enable audit logging** for all services
4. **Use VPC** for internal communication
5. **Implement proper IAM policies**
6. **Regular security updates** for base images
7. **Monitor for security vulnerabilities**

## Cost Optimization

1. **Use preemptible instances** for non-critical workloads
2. **Implement auto-scaling** to match demand
3. **Use Cloud Storage lifecycle policies**
4. **Monitor and optimize** resource usage
5. **Use committed use discounts** for predictable workloads

## Support and Resources

- [Google Cloud Documentation](https://cloud.google.com/docs)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Documentation](https://docs.docker.com/)

For additional support, please refer to the project's issue tracker or contact the development team.
