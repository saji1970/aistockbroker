#!/bin/bash

# AI Stock Trading - GCP Deployment Script
# This script deploys the AI Stock Trading application to Google Cloud Platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="stockadvisor-463716"
REGION="us-central1"
SERVICE_NAME_BACKEND="ai-stock-trading-backend"
SERVICE_NAME_FRONTEND="ai-stock-trading-frontend"
IMAGE_NAME_BACKEND="gcr.io/${PROJECT_ID}/ai-stock-trading-backend"
IMAGE_NAME_FRONTEND="gcr.io/${PROJECT_ID}/ai-stock-trading-frontend"

echo -e "${BLUE}🚀 AI Stock Trading - GCP Deployment${NC}"
echo "=================================="

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

# Get or set project ID
if [ -z "$PROJECT_ID" ]; then
    CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)
    if [ -z "$CURRENT_PROJECT" ]; then
        echo -e "${YELLOW}⚠️  No project ID set.${NC}"
        echo "Available projects:"
        gcloud projects list --format="table(projectId,name)"
        echo ""
        read -p "Enter your project ID: " PROJECT_ID
        gcloud config set project $PROJECT_ID
    else
        PROJECT_ID=$CURRENT_PROJECT
        echo -e "${GREEN}✅ Using project: $PROJECT_ID${NC}"
    fi
fi

# Enable required APIs
echo -e "${BLUE}📋 Enabling required APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable aiplatform.googleapis.com

# Build and push Docker images
echo -e "${BLUE}🐳 Building and pushing Docker images...${NC}"

# Build backend image
echo "Building backend image..."
docker build -t $IMAGE_NAME_BACKEND:latest -f Dockerfile .
docker push $IMAGE_NAME_BACKEND:latest

# Build frontend image
echo "Building frontend image..."
docker build -t $IMAGE_NAME_FRONTEND:latest -f Dockerfile.frontend .
docker push $IMAGE_NAME_FRONTEND:latest

# Deploy to Cloud Run
echo -e "${BLUE}🚀 Deploying to Cloud Run...${NC}"

# Deploy backend
echo "Deploying backend service..."
gcloud run deploy $SERVICE_NAME_BACKEND \
    --image $IMAGE_NAME_BACKEND:latest \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10 \
    --set-env-vars "FLASK_ENV=production" \
    --set-env-vars "PORT=8080"

# Get backend URL
BACKEND_URL=$(gcloud run services describe $SERVICE_NAME_BACKEND --region=$REGION --format="value(status.url)")

# Deploy frontend
echo "Deploying frontend service..."
gcloud run deploy $SERVICE_NAME_FRONTEND \
    --image $IMAGE_NAME_FRONTEND:latest \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --port 80 \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 5 \
    --set-env-vars "REACT_APP_API_URL=$BACKEND_URL"

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe $SERVICE_NAME_FRONTEND --region=$REGION --format="value(status.url)")

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo ""
echo -e "${BLUE}📊 Service URLs:${NC}"
echo -e "Frontend: ${GREEN}$FRONTEND_URL${NC}"
echo -e "Backend API: ${GREEN}$BACKEND_URL${NC}"
echo ""
echo -e "${BLUE}🔧 Health Checks:${NC}"
echo -e "Frontend Health: ${GREEN}$FRONTEND_URL/health${NC}"
echo -e "Backend Health: ${GREEN}$BACKEND_URL/api/health${NC}"
echo ""
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo "1. Test the application by visiting the frontend URL"
echo "2. Monitor logs: gcloud logging tail"
echo "3. View services: gcloud run services list"
echo "4. Scale services as needed"
echo ""
echo -e "${GREEN}🎉 Your AI Stock Trading application is now live on GCP!${NC}"
