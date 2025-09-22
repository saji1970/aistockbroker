#!/bin/bash

# AI Stock Trading System - Staging Deployment Script
# This script deploys the application to Google Cloud Platform staging environment

set -e

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-"your-project-id"}
REGION=${GCP_REGION:-"us-central1"}
ENVIRONMENT="staging"
SERVICE_ACCOUNT_KEY=${GCP_SA_KEY}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting AI Stock Trading System Staging Deployment${NC}"
echo -e "${BLUE}📦 Project: ${PROJECT_ID}${NC}"
echo -e "${BLUE}🌍 Region: ${REGION}${NC}"
echo -e "${BLUE}🔧 Environment: ${ENVIRONMENT}${NC}"

# Check if required tools are installed
check_dependencies() {
    echo -e "${YELLOW}🔍 Checking dependencies...${NC}"
    
    if ! command -v gcloud &> /dev/null; then
        echo -e "${RED}❌ gcloud CLI not found. Please install Google Cloud SDK.${NC}"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker not found. Please install Docker.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ All dependencies found${NC}"
}

# Authenticate with Google Cloud
authenticate_gcp() {
    echo -e "${YELLOW}🔐 Authenticating with Google Cloud...${NC}"
    
    if [ -n "$SERVICE_ACCOUNT_KEY" ]; then
        echo "$SERVICE_ACCOUNT_KEY" | base64 -d > /tmp/gcp-key.json
        gcloud auth activate-service-account --key-file=/tmp/gcp-key.json
        rm /tmp/gcp-key.json
    else
        gcloud auth login
    fi
    
    gcloud config set project $PROJECT_ID
    gcloud auth configure-docker
    
    echo -e "${GREEN}✅ Authentication successful${NC}"
}

# Build and push Docker images
build_and_push_images() {
    echo -e "${YELLOW}🏗️  Building and pushing Docker images...${NC}"
    
    # Build Backend
    echo -e "${BLUE}📊 Building backend image...${NC}"
    docker build -f deployment/Dockerfile.api-server \
        -t gcr.io/$PROJECT_ID/ai-stock-backend-staging:latest \
        -t gcr.io/$PROJECT_ID/ai-stock-backend-staging:$(git rev-parse --short HEAD) \
        .
    
    docker push gcr.io/$PROJECT_ID/ai-stock-backend-staging:latest
    docker push gcr.io/$PROJECT_ID/ai-stock-backend-staging:$(git rev-parse --short HEAD)
    
    # Build Frontend
    echo -e "${BLUE}🌐 Building frontend image...${NC}"
    cd frontend
    npm ci
    npm run build
    cd ..
    
    docker build -f deployment/Dockerfile.frontend \
        -t gcr.io/$PROJECT_ID/ai-stock-frontend-staging:latest \
        -t gcr.io/$PROJECT_ID/ai-stock-frontend-staging:$(git rev-parse --short HEAD) \
        .
    
    docker push gcr.io/$PROJECT_ID/ai-stock-frontend-staging:latest
    docker push gcr.io/$PROJECT_ID/ai-stock-frontend-staging:$(git rev-parse --short HEAD)
    
    # Build Trading Bot
    echo -e "${BLUE}🤖 Building trading bot image...${NC}"
    docker build -f deployment/Dockerfile.trading-bot \
        -t gcr.io/$PROJECT_ID/ai-stock-trading-bot-staging:latest \
        -t gcr.io/$PROJECT_ID/ai-stock-trading-bot-staging:$(git rev-parse --short HEAD) \
        .
    
    docker push gcr.io/$PROJECT_ID/ai-stock-trading-bot-staging:latest
    docker push gcr.io/$PROJECT_ID/ai-stock-trading-bot-staging:$(git rev-parse --short HEAD)
    
    echo -e "${GREEN}✅ All images built and pushed successfully${NC}"
}

# Deploy services to Cloud Run
deploy_services() {
    echo -e "${YELLOW}🚀 Deploying services to Cloud Run...${NC}"
    
    # Deploy Backend
    echo -e "${BLUE}📊 Deploying backend service...${NC}"
    gcloud run deploy ai-stock-backend-staging \
        --image gcr.io/$PROJECT_ID/ai-stock-backend-staging:latest \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --set-env-vars="ENVIRONMENT=staging" \
        --memory=2Gi \
        --cpu=2 \
        --max-instances=5 \
        --min-instances=0 \
        --timeout=300
    
    # Get backend URL
    BACKEND_URL=$(gcloud run services describe ai-stock-backend-staging --platform managed --region $REGION --format 'value(status.url)')
    echo -e "${GREEN}✅ Backend deployed: $BACKEND_URL${NC}"
    
    # Deploy Frontend
    echo -e "${BLUE}🌐 Deploying frontend service...${NC}"
    gcloud run deploy ai-stock-frontend-staging \
        --image gcr.io/$PROJECT_ID/ai-stock-frontend-staging:latest \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --set-env-vars="REACT_APP_API_URL=$BACKEND_URL" \
        --set-env-vars="ENVIRONMENT=staging" \
        --memory=1Gi \
        --cpu=1 \
        --max-instances=3 \
        --min-instances=0 \
        --timeout=60
    
    # Get frontend URL
    FRONTEND_URL=$(gcloud run services describe ai-stock-frontend-staging --platform managed --region $REGION --format 'value(status.url)')
    echo -e "${GREEN}✅ Frontend deployed: $FRONTEND_URL${NC}"
    
    # Deploy Trading Bot
    echo -e "${BLUE}🤖 Deploying trading bot service...${NC}"
    gcloud run deploy ai-stock-trading-bot-staging \
        --image gcr.io/$PROJECT_ID/ai-stock-trading-bot-staging:latest \
        --platform managed \
        --region $REGION \
        --no-allow-unauthenticated \
        --set-env-vars="ENVIRONMENT=staging" \
        --memory=2Gi \
        --cpu=2 \
        --max-instances=2 \
        --min-instances=0 \
        --timeout=300
    
    # Get trading bot URL
    TRADING_BOT_URL=$(gcloud run services describe ai-stock-trading-bot-staging --platform managed --region $REGION --format 'value(status.url)')
    echo -e "${GREEN}✅ Trading bot deployed: $TRADING_BOT_URL${NC}"
}

# Set up infrastructure
setup_infrastructure() {
    echo -e "${YELLOW}🏗️  Setting up infrastructure...${NC}"
    
    # Create Cloud Storage bucket
    echo -e "${BLUE}📦 Creating Cloud Storage bucket...${NC}"
    gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$PROJECT_ID-ai-stock-staging-data || true
    
    # Set up Cloud Scheduler
    echo -e "${BLUE}⏰ Setting up Cloud Scheduler...${NC}"
    gcloud scheduler jobs create http ai-stock-trading-scheduler-staging \
        --schedule="0 9 * * 1-5" \
        --uri="$TRADING_BOT_URL/start-trading" \
        --http-method=POST \
        --oidc-service-account-email=$GCP_SA_EMAIL \
        --oidc-token-audience="$TRADING_BOT_URL" || true
    
    echo -e "${GREEN}✅ Infrastructure setup complete${NC}"
}

# Run health checks
health_checks() {
    echo -e "${YELLOW}🏥 Running health checks...${NC}"
    
    # Check backend health
    echo -e "${BLUE}📊 Checking backend health...${NC}"
    if curl -f -s "$BACKEND_URL/health" > /dev/null; then
        echo -e "${GREEN}✅ Backend is healthy${NC}"
    else
        echo -e "${RED}❌ Backend health check failed${NC}"
        exit 1
    fi
    
    # Check frontend health
    echo -e "${BLUE}🌐 Checking frontend health...${NC}"
    if curl -f -s "$FRONTEND_URL" > /dev/null; then
        echo -e "${GREEN}✅ Frontend is healthy${NC}"
    else
        echo -e "${RED}❌ Frontend health check failed${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ All health checks passed${NC}"
}

# Main deployment function
main() {
    check_dependencies
    authenticate_gcp
    build_and_push_images
    deploy_services
    setup_infrastructure
    health_checks
    
    echo -e "${GREEN}🎉 Staging deployment completed successfully!${NC}"
    echo -e "${BLUE}📊 Backend: $BACKEND_URL${NC}"
    echo -e "${BLUE}🌐 Frontend: $FRONTEND_URL${NC}"
    echo -e "${BLUE}🤖 Trading Bot: $TRADING_BOT_URL${NC}"
    echo -e "${BLUE}🔧 Environment: $ENVIRONMENT${NC}"
}

# Run main function
main "$@"
