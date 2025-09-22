# AI Stock Trading System - Deployment Guide

This guide provides comprehensive instructions for deploying the AI Stock Trading System to Google Cloud Platform using CI/CD pipelines.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Manual Deployment](#manual-deployment)
5. [CI/CD Pipeline](#cicd-pipeline)
6. [Environment Configuration](#environment-configuration)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)
8. [Troubleshooting](#troubleshooting)

## Overview

The AI Stock Trading System is designed for deployment on Google Cloud Platform with the following architecture:

- **Backend**: Python FastAPI application on Cloud Run
- **Frontend**: React application on Cloud Run
- **Trading Bot**: Python trading bot on Cloud Run
- **Storage**: Cloud Storage for data persistence
- **Scheduling**: Cloud Scheduler for automated trading
- **Monitoring**: Cloud Monitoring and Logging

## Prerequisites

### Required Tools

- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
- [Docker](https://docs.docker.com/get-docker/)
- [Node.js 16+](https://nodejs.org/)
- [Python 3.8+](https://www.python.org/)
- [Git](https://git-scm.com/)

### Required Accounts

- Google Cloud Platform account with billing enabled
- GitHub account with repository access
- API keys for external services (optional)

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/saji1970/aistockbroker.git
cd aistockbroker
```

### 2. Set Up GCP Project

Follow the [GCP Setup Guide](GCP_SETUP_GUIDE.md) to:
- Create a GCP project
- Enable required APIs
- Create service account
- Configure GitHub secrets

### 3. Deploy to Staging

```bash
# Make scripts executable
chmod +x deployment/scripts/*.sh

# Deploy to staging
./deployment/scripts/deploy-staging.sh
```

### 4. Deploy to Production

```bash
# Deploy to production (requires confirmation)
./deployment/scripts/deploy-production.sh
```

## Manual Deployment

### Backend Deployment

```bash
# Build and push backend image
docker build -f deployment/Dockerfile.api-server \
  -t gcr.io/YOUR_PROJECT_ID/ai-stock-backend:latest .

docker push gcr.io/YOUR_PROJECT_ID/ai-stock-backend:latest

# Deploy to Cloud Run
gcloud run deploy ai-stock-backend \
  --image gcr.io/YOUR_PROJECT_ID/ai-stock-backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory=2Gi \
  --cpu=2 \
  --max-instances=10 \
  --min-instances=1
```

### Frontend Deployment

```bash
# Build frontend
cd frontend
npm ci
npm run build
cd ..

# Build and push frontend image
docker build -f deployment/Dockerfile.frontend \
  -t gcr.io/YOUR_PROJECT_ID/ai-stock-frontend:latest .

docker push gcr.io/YOUR_PROJECT_ID/ai-stock-frontend:latest

# Deploy to Cloud Run
gcloud run deploy ai-stock-frontend \
  --image gcr.io/YOUR_PROJECT_ID/ai-stock-frontend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory=1Gi \
  --cpu=1 \
  --max-instances=5 \
  --min-instances=0
```

### Trading Bot Deployment

```bash
# Build and push trading bot image
docker build -f deployment/Dockerfile.trading-bot \
  -t gcr.io/YOUR_PROJECT_ID/ai-stock-trading-bot:latest .

docker push gcr.io/YOUR_PROJECT_ID/ai-stock-trading-bot:latest

# Deploy to Cloud Run
gcloud run deploy ai-stock-trading-bot \
  --image gcr.io/YOUR_PROJECT_ID/ai-stock-trading-bot:latest \
  --platform managed \
  --region us-central1 \
  --no-allow-unauthenticated \
  --memory=2Gi \
  --cpu=2 \
  --max-instances=3 \
  --min-instances=0
```

## CI/CD Pipeline

### GitHub Actions Workflow

The system includes two main workflows:

1. **CI/CD Pipeline** (`.github/workflows/ci.yml`)
   - Runs on push to `master`/`main` branches
   - Executes tests, security scans, and staging deployment
   - Supports manual deployment with environment selection

2. **Production Deployment** (`.github/workflows/deploy-production.yml`)
   - Manual trigger only
   - Requires confirmation for production deployment
   - Includes comprehensive testing and validation

### Workflow Triggers

#### Automatic Deployment
- **Staging**: Push to `master` or `main` branch
- **Tests**: Push to any branch or pull request

#### Manual Deployment
- **Staging**: Use "Actions" tab → "CI/CD Pipeline" → "Run workflow"
- **Production**: Use "Actions" tab → "Production Deployment" → "Run workflow"

### Environment Variables

Configure the following GitHub secrets:

| Secret | Description | Required |
|--------|-------------|----------|
| `GCP_SA_KEY` | Base64 encoded service account key | Yes |
| `GCP_PROJECT_ID` | GCP project ID | Yes |
| `GCP_SA_EMAIL` | Service account email | Yes |
| `GOOGLE_API_KEY` | Google API key for Gemini | Optional |
| `ALPHA_VANTAGE_API_KEY` | Alpha Vantage API key | Optional |
| `FINNHUB_API_KEY` | Finnhub API key | Optional |
| `MARKETSTACK_API_KEY` | Marketstack API key | Optional |
| `CUSTOM_DOMAIN` | Custom domain for staging | Optional |
| `PRODUCTION_DOMAIN` | Custom domain for production | Optional |
| `ALERT_EMAIL` | Email for monitoring alerts | Optional |
| `SLACK_WEBHOOK` | Slack webhook for notifications | Optional |

## Environment Configuration

### Staging Environment

- **Purpose**: Development and testing
- **Resources**: Lower memory/CPU allocation
- **Security**: Relaxed CORS and authentication
- **Monitoring**: Basic monitoring enabled
- **Cost**: Optimized for cost efficiency

### Production Environment

- **Purpose**: Live trading system
- **Resources**: Higher memory/CPU allocation
- **Security**: Strict CORS and authentication
- **Monitoring**: Comprehensive monitoring and alerting
- **Cost**: Optimized for performance and reliability

### Configuration Files

- `deployment/config/staging.env`: Staging environment variables
- `deployment/config/production.env`: Production environment variables

## Monitoring and Maintenance

### Health Checks

The system includes comprehensive health checks:

- **Backend**: `/health` endpoint
- **Frontend**: Static file serving check
- **Trading Bot**: `/health` endpoint

### Monitoring

- **Cloud Run**: Service metrics and logs
- **Cloud Monitoring**: Custom metrics and dashboards
- **Cloud Logging**: Centralized log aggregation
- **Error Reporting**: Automatic error detection

### Maintenance Tasks

#### Daily
- Monitor service health
- Check error logs
- Review trading performance

#### Weekly
- Update dependencies
- Review security alerts
- Analyze performance metrics

#### Monthly
- Rotate service account keys
- Update base images
- Review and optimize costs

## Troubleshooting

### Common Issues

#### 1. Authentication Errors

**Problem**: Service account authentication fails

**Solution**:
```bash
# Verify service account key
gcloud auth activate-service-account --key-file=path/to/key.json

# Check project configuration
gcloud config set project YOUR_PROJECT_ID

# Verify permissions
gcloud projects get-iam-policy YOUR_PROJECT_ID
```

#### 2. Build Failures

**Problem**: Docker build fails

**Solution**:
```bash
# Check Dockerfile syntax
docker build --no-cache -f deployment/Dockerfile.api-server .

# Verify base image availability
docker pull python:3.8-slim

# Check build context
docker build --no-cache .
```

#### 3. Deployment Failures

**Problem**: Cloud Run deployment fails

**Solution**:
```bash
# Check service logs
gcloud run services logs read SERVICE_NAME --region=us-central1

# Verify resource limits
gcloud run services describe SERVICE_NAME --region=us-central1

# Check environment variables
gcloud run services describe SERVICE_NAME --region=us-central1 --format="value(spec.template.spec.template.spec.containers[0].env[].name,spec.template.spec.template.spec.containers[0].env[].value)"
```

#### 4. Performance Issues

**Problem**: Slow response times

**Solution**:
- Increase memory allocation
- Optimize database queries
- Implement caching
- Use CDN for static assets

### Debug Commands

```bash
# Check service status
gcloud run services list

# View service logs
gcloud run services logs read SERVICE_NAME --region=us-central1 --limit=100

# Update service configuration
gcloud run services update SERVICE_NAME --region=us-central1 --memory=4Gi

# Delete service
gcloud run services delete SERVICE_NAME --region=us-central1

# Check IAM permissions
gcloud projects get-iam-policy YOUR_PROJECT_ID

# View Cloud Build logs
gcloud builds list --limit=10
gcloud builds log BUILD_ID
```

### Support

For additional support:

1. Check the [GitHub Issues](https://github.com/saji1970/aistockbroker/issues)
2. Review the [GCP Documentation](https://cloud.google.com/docs)
3. Contact the development team

## Best Practices

### Security
- Use least privilege principle for service accounts
- Rotate keys regularly
- Enable audit logging
- Implement proper IAM policies

### Performance
- Use appropriate resource allocation
- Implement caching strategies
- Monitor and optimize database queries
- Use CDN for static assets

### Cost Optimization
- Use auto-scaling to match demand
- Implement proper resource limits
- Monitor usage and optimize accordingly
- Use committed use discounts for predictable workloads

### Reliability
- Implement proper error handling
- Use health checks and monitoring
- Implement graceful degradation
- Regular backup and disaster recovery testing
