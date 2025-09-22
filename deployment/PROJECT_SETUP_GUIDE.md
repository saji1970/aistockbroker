# AI Stock Trading System - Project Setup Guide

## Project Configuration

**GCP Project ID**: `stockbroker-28983`  
**GCP User**: `saji651970@gmail.com`  
**GitHub Repository**: `https://github.com/saji1970/aistockbroker`

## Quick Setup Instructions

### Step 1: Enable Required APIs

Run these commands to enable the necessary APIs in your GCP project:

```bash
# Set your project
gcloud config set project stockbroker-28983

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable monitoring.googleapis.com
gcloud services enable logging.googleapis.com
```

### Step 2: Create Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select project `stockbroker-28983`
3. Navigate to **IAM & Admin** → **Service Accounts**
4. Click **Create Service Account**
5. Enter details:
   - **Name**: `ai-stock-trading-deployer`
   - **Description**: `Service account for AI Stock Trading System deployment`
6. Click **Create and Continue**
7. Grant these roles:
   - `Cloud Run Admin`
   - `Storage Admin`
   - `Cloud Build Editor`
   - `Cloud Scheduler Admin`
   - `Monitoring Admin`
   - `Logging Admin`
8. Click **Done**

### Step 3: Generate Service Account Key

1. Find your service account: `ai-stock-trading-deployer@stockbroker-28983.iam.gserviceaccount.com`
2. Click on the service account name
3. Go to **Keys** tab
4. Click **Add Key** → **Create new key**
5. Select **JSON** format
6. Click **Create**
7. Save the downloaded JSON file securely

### Step 4: Configure GitHub Secrets

Go to your GitHub repository: `https://github.com/saji1970/aistockbroker`

Navigate to **Settings** → **Secrets and variables** → **Actions**

Add these secrets:

#### Required Secrets

1. **GCP_SA_KEY**
   - Value: Base64 encoded service account JSON key
   - Command: `base64 -i path/to/service-account-key.json`

2. **GCP_PROJECT_ID**
   - Value: `stockbroker-28983`

3. **GCP_SA_EMAIL**
   - Value: `ai-stock-trading-deployer@stockbroker-28983.iam.gserviceaccount.com`

#### Optional API Keys

4. **GOOGLE_API_KEY**
   - Value: Your Google API key for Gemini

5. **ALPHA_VANTAGE_API_KEY**
   - Value: Your Alpha Vantage API key

6. **FINNHUB_API_KEY**
   - Value: Your Finnhub API key

7. **MARKETSTACK_API_KEY**
   - Value: Your Marketstack API key

8. **HUGGINGFACE_API_KEY**
   - Value: Your Hugging Face API key

### Step 5: Set Up GitHub Environments

1. Go to **Settings** → **Environments**
2. Create these environments:

#### Staging Environment
- **Name**: `staging`
- **Protection rules**: None

#### Production Environment
- **Name**: `production`
- **Protection rules**:
  - Required reviewers: Add team members
  - Wait timer: 5 minutes

### Step 6: Test Deployment

#### Automatic Staging Deployment
```bash
# Push to master branch to trigger automatic staging deployment
git push origin master
```

#### Manual Deployment
1. Go to **Actions** tab in GitHub
2. Select **AI Stock Trading System - CI/CD Pipeline**
3. Click **Run workflow**
4. Choose environment and service
5. Click **Run workflow**

## Deployment URLs

After successful deployment, your services will be available at:

### Staging Environment
- **Backend**: `https://ai-stock-backend-staging-xxxxx-uc.a.run.app`
- **Frontend**: `https://ai-stock-frontend-staging-xxxxx-uc.a.run.app`
- **Trading Bot**: `https://ai-stock-trading-bot-staging-xxxxx-uc.a.run.app`

### Production Environment
- **Backend**: `https://ai-stock-backend-prod-xxxxx-uc.a.run.app`
- **Frontend**: `https://ai-stock-frontend-prod-xxxxx-uc.a.run.app`
- **Trading Bot**: `https://ai-stock-trading-bot-prod-xxxxx-uc.a.run.app`

## Local Development Setup

### Install Google Cloud SDK

```bash
# Authenticate with your account
gcloud auth login

# Set project
gcloud config set project stockbroker-28983

# Configure Docker
gcloud auth configure-docker
```

### Test Local Deployment

```bash
# Make scripts executable (Linux/macOS)
chmod +x deployment/scripts/*.sh

# Deploy to staging
./deployment/scripts/deploy-staging.sh

# Or use PowerShell (Windows)
./deployment/scripts/deploy-staging.ps1
```

## Monitoring and Management

### Cloud Console
- **Project**: [stockbroker-28983](https://console.cloud.google.com/home/dashboard?project=stockbroker-28983)
- **Cloud Run**: [Services](https://console.cloud.google.com/run?project=stockbroker-28983)
- **Cloud Storage**: [Buckets](https://console.cloud.google.com/storage/browser?project=stockbroker-28983)
- **Cloud Scheduler**: [Jobs](https://console.cloud.google.com/cloudscheduler?project=stockbroker-28983)

### Useful Commands

```bash
# Check service status
gcloud run services list --project=stockbroker-28983

# View service logs
gcloud run services logs read ai-stock-backend-staging --region=us-central1 --project=stockbroker-28983

# Update service configuration
gcloud run services update ai-stock-backend-staging --region=us-central1 --project=stockbroker-28983

# Check IAM permissions
gcloud projects get-iam-policy stockbroker-28983
```

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

### Support

- **GitHub Issues**: [Repository Issues](https://github.com/saji1970/aistockbroker/issues)
- **GCP Support**: [Cloud Console Support](https://console.cloud.google.com/support?project=stockbroker-28983)
- **Documentation**: [Deployment Guide](DEPLOYMENT_GUIDE.md)

## Cost Optimization

### Estimated Monthly Costs (Staging)
- **Cloud Run**: ~$10-20 (low traffic)
- **Cloud Storage**: ~$1-5 (minimal data)
- **Cloud Scheduler**: ~$1-2 (basic scheduling)
- **Total**: ~$12-27/month

### Estimated Monthly Costs (Production)
- **Cloud Run**: ~$50-200 (moderate traffic)
- **Cloud Storage**: ~$5-20 (moderate data)
- **Cloud Scheduler**: ~$2-5 (frequent scheduling)
- **Total**: ~$57-225/month

### Cost Optimization Tips
1. Use auto-scaling to match demand
2. Implement proper resource limits
3. Monitor usage and optimize accordingly
4. Use committed use discounts for predictable workloads

## Security Checklist

- [ ] Service account has minimal required permissions
- [ ] API keys are stored as GitHub secrets
- [ ] Environment variables are properly configured
- [ ] CORS settings are appropriate for each environment
- [ ] Monitoring and alerting are enabled
- [ ] Regular security updates are planned
- [ ] Access logs are monitored

## Next Steps

1. **Complete Setup**: Follow all steps above
2. **Test Deployment**: Deploy to staging environment
3. **Configure Monitoring**: Set up alerts and dashboards
4. **Production Deployment**: Deploy to production when ready
5. **Monitor and Maintain**: Regular monitoring and updates

Your AI Stock Trading System is now ready for deployment on Google Cloud Platform! 🚀
