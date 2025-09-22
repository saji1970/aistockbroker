# 🚀 GCP Deployment Guide - AI Stock Trading

## 📋 **Prerequisites**

### **1. Google Cloud Account**
- Active Google Cloud Platform account
- Billing enabled
- Sufficient quota for Cloud Run and Container Registry

### **2. Local Setup**
- Google Cloud SDK installed
- Docker installed and running
- Git repository with your code

### **3. Required APIs**
- Cloud Build API
- Cloud Run API
- Container Registry API
- AI Platform API

## 🔧 **Setup Instructions**

### **Step 1: Install Google Cloud SDK**
```bash
# macOS (using Homebrew)
brew install google-cloud-sdk

# Or download from Google Cloud Console
# https://cloud.google.com/sdk/docs/install
```

### **Step 2: Authenticate with Google Cloud**
```bash
# Login to your Google account
gcloud auth login

# Set your project ID
gcloud config set project YOUR_PROJECT_ID

# Verify configuration
gcloud config list
```

### **Step 3: Enable Required APIs**
```bash
# Enable required services
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable aiplatform.googleapis.com
```

## 🚀 **Deployment Methods**

### **Method 1: Automated Script (Recommended)**

1. **Run the deployment script**
```bash
./deploy-gcp.sh
```

2. **Follow the prompts**
   - Enter your project ID if not set
   - Wait for the build and deployment process

3. **Get your service URLs**
   - The script will output the frontend and backend URLs

### **Method 2: Manual Deployment**

#### **Build and Push Docker Images**
```bash
# Set your project ID
PROJECT_ID="your-project-id"

# Build backend image
docker build -t gcr.io/$PROJECT_ID/ai-stock-trading-backend:latest -f Dockerfile .
docker push gcr.io/$PROJECT_ID/ai-stock-trading-backend:latest

# Build frontend image
docker build -t gcr.io/$PROJECT_ID/ai-stock-trading-frontend:latest -f Dockerfile.frontend .
docker push gcr.io/$PROJECT_ID/ai-stock-trading-frontend:latest
```

#### **Deploy to Cloud Run**
```bash
# Deploy backend
gcloud run deploy ai-stock-trading-backend \
    --image gcr.io/$PROJECT_ID/ai-stock-trading-backend:latest \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10

# Get backend URL
BACKEND_URL=$(gcloud run services describe ai-stock-trading-backend --region=us-central1 --format="value(status.url)")

# Deploy frontend
gcloud run deploy ai-stock-trading-frontend \
    --image gcr.io/$PROJECT_ID/ai-stock-trading-frontend:latest \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --port 80 \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 5 \
    --set-env-vars "REACT_APP_API_URL=$BACKEND_URL"
```

### **Method 3: Cloud Build (CI/CD)**

1. **Connect your repository to Cloud Build**
2. **Create a trigger for automatic deployment**
3. **Use the provided `cloudbuild.yaml`**

```bash
# Submit build to Cloud Build
gcloud builds submit --config cloudbuild.yaml .
```

## 📊 **Service Configuration**

### **Backend Service (Cloud Run)**
- **Memory**: 1GB
- **CPU**: 1 vCPU
- **Max Instances**: 10
- **Port**: 8080
- **Environment**: Production

### **Frontend Service (Cloud Run)**
- **Memory**: 512MB
- **CPU**: 1 vCPU
- **Max Instances**: 5
- **Port**: 80
- **Environment**: Production

## 🔍 **Monitoring and Logs**

### **View Service Logs**
```bash
# Backend logs
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=ai-stock-trading-backend"

# Frontend logs
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=ai-stock-trading-frontend"
```

### **Monitor Services**
```bash
# List all services
gcloud run services list

# Get service details
gcloud run services describe ai-stock-trading-backend --region=us-central1
gcloud run services describe ai-stock-trading-frontend --region=us-central1
```

### **Health Checks**
```bash
# Backend health
curl https://your-backend-url/api/health

# Frontend health
curl https://your-frontend-url/health
```

## 🔧 **Environment Variables**

### **Backend Environment Variables**
```bash
FLASK_ENV=production
PORT=8080
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

### **Frontend Environment Variables**
```bash
REACT_APP_API_URL=https://your-backend-url
NODE_ENV=production
```

## 🛡️ **Security Considerations**

### **1. Authentication**
- Consider enabling authentication for production
- Use service accounts for API access
- Implement proper CORS policies

### **2. API Keys**
- Store sensitive data in Secret Manager
- Use environment variables for configuration
- Never commit API keys to version control

### **3. Network Security**
- Use VPC connectors if needed
- Implement proper firewall rules
- Enable Cloud Armor for DDoS protection

## 📈 **Scaling and Performance**

### **Auto-scaling Configuration**
```bash
# Update scaling configuration
gcloud run services update ai-stock-trading-backend \
    --region us-central1 \
    --min-instances 0 \
    --max-instances 20 \
    --cpu-throttling
```

### **Performance Optimization**
- Enable Cloud CDN for static assets
- Use Cloud Storage for file storage
- Implement caching strategies

## 🔄 **Updates and Rollbacks**

### **Deploy New Version**
```bash
# Build and push new image
docker build -t gcr.io/$PROJECT_ID/ai-stock-trading-backend:v2 -f Dockerfile .
docker push gcr.io/$PROJECT_ID/ai-stock-trading-backend:v2

# Deploy new version
gcloud run deploy ai-stock-trading-backend \
    --image gcr.io/$PROJECT_ID/ai-stock-trading-backend:v2 \
    --region us-central1
```

### **Rollback to Previous Version**
```bash
# List revisions
gcloud run revisions list --service=ai-stock-trading-backend --region=us-central1

# Rollback to specific revision
gcloud run services update-traffic ai-stock-trading-backend \
    --region us-central1 \
    --to-revisions=REVISION_NAME=100
```

## 💰 **Cost Optimization**

### **Resource Optimization**
- Use appropriate memory and CPU allocations
- Set reasonable max instances
- Enable CPU throttling for non-critical services

### **Monitoring Costs**
```bash
# View billing information
gcloud billing accounts list
gcloud billing projects describe YOUR_PROJECT_ID
```

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Build Failures**
   - Check Dockerfile syntax
   - Verify dependencies in requirements.txt
   - Ensure proper file permissions

2. **Deployment Failures**
   - Check service account permissions
   - Verify API enablement
   - Review Cloud Build logs

3. **Runtime Errors**
   - Check application logs
   - Verify environment variables
   - Test locally with Docker

### **Debug Commands**
```bash
# Check service status
gcloud run services describe SERVICE_NAME --region=REGION

# View recent logs
gcloud logging read "resource.type=cloud_run_revision" --limit=50

# Test service connectivity
curl -v https://your-service-url/health
```

## 📞 **Support and Resources**

### **Useful Commands**
```bash
# Get help
gcloud help

# List all commands
gcloud help --all

# Get specific command help
gcloud run deploy --help
```

### **Documentation**
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Container Registry Documentation](https://cloud.google.com/container-registry/docs)

## 🎉 **Success Checklist**

- [ ] Google Cloud SDK installed and authenticated
- [ ] Required APIs enabled
- [ ] Docker images built and pushed
- [ ] Services deployed to Cloud Run
- [ ] Health checks passing
- [ ] Application accessible via URLs
- [ ] Monitoring and logging configured
- [ ] Security measures implemented
- [ ] Cost monitoring enabled

**🚀 Your AI Stock Trading application is now successfully deployed on Google Cloud Platform!**
