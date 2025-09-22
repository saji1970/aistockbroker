#!/bin/bash

# AI Stock Trading - Cloud Run Deployment Script
# This script deploys the AI Stock Trading application to Google Cloud Run

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="aimodelfoundry"
REGION="us-central1"
SERVICE_NAME_BACKEND="ai-stock-trading-backend"
SERVICE_NAME_FRONTEND="ai-stock-trading-frontend"

echo -e "${BLUE}🚀 AI Stock Trading - Cloud Run Deployment${NC}"
echo "=============================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Google Cloud SDK is not installed. Please install it first.${NC}"
    echo "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${YELLOW}⚠️  You are not authenticated with Google Cloud.${NC}"
    echo "Please run: gcloud auth login"
    exit 1
fi

# Set project
echo -e "${GREEN}✅ Using project: $PROJECT_ID${NC}"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo -e "${BLUE}📋 Enabling required APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable aiplatform.googleapis.com

# Deploy backend to Cloud Run
echo -e "${BLUE}🚀 Deploying backend to Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME_BACKEND \
    --source . \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10 \
    --set-env-vars "FLASK_ENV=production"

# Get backend URL
BACKEND_URL=$(gcloud run services describe $SERVICE_NAME_BACKEND --region=$REGION --format="value(status.url)")
echo -e "${GREEN}✅ Backend deployed at: $BACKEND_URL${NC}"

# Deploy frontend to Cloud Run
echo -e "${BLUE}🚀 Deploying frontend to Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME_FRONTEND \
    --source . \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --port 3000 \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 5 \
    --set-env-vars "REACT_APP_API_URL=$BACKEND_URL" \
    --set-env-vars "NODE_ENV=production"

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe $SERVICE_NAME_FRONTEND --region=$REGION --format="value(status.url)")
echo -e "${GREEN}✅ Frontend deployed at: $FRONTEND_URL${NC}"

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo ""
echo -e "${BLUE}📊 Service URLs:${NC}"
echo -e "Frontend: ${GREEN}$FRONTEND_URL${NC}"
echo -e "Backend API: ${GREEN}$BACKEND_URL${NC}"
echo ""
echo -e "${BLUE}🔧 Health Checks:${NC}"
echo -e "Backend Health: ${GREEN}$BACKEND_URL/api/health${NC}"
echo ""
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo "1. Test the application by visiting the frontend URL"
echo "2. Monitor logs: gcloud logging tail"
echo "3. View services: gcloud run services list"
echo "4. Scale services as needed"
echo ""
echo -e "${GREEN}🎉 Your AI Stock Trading application is now live on Google Cloud Run!${NC}"
