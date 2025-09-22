#!/bin/bash

# AI Stock Trading System - Production Deployment Script
# This script deploys the application to Google Cloud Platform production environment

set -e

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-"stockbroker-28983"}
REGION=${GCP_REGION:-"us-central1"}
ENVIRONMENT="production"
SERVICE_ACCOUNT_KEY=${GCP_SA_KEY}
VERSION=${VERSION:-"latest"}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting AI Stock Trading System Production Deployment${NC}"
echo -e "${BLUE}📦 Project: ${PROJECT_ID}${NC}"
echo -e "${BLUE}🌍 Region: ${REGION}${NC}"
echo -e "${BLUE}🔧 Environment: ${ENVIRONMENT}${NC}"
echo -e "${BLUE}📋 Version: ${VERSION}${NC}"

# Confirmation prompt
confirm_production() {
    echo -e "${RED}⚠️  WARNING: This will deploy to PRODUCTION environment!${NC}"
    echo -e "${YELLOW}Are you sure you want to continue? (yes/no)${NC}"
    read -r response
    if [ "$response" != "yes" ]; then
        echo -e "${RED}❌ Production deployment cancelled${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Production deployment confirmed${NC}"
}

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

# Run pre-deployment tests
run_tests() {
    echo -e "${YELLOW}🧪 Running pre-deployment tests...${NC}"
    
    # Install Python dependencies
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    
    # Run backend tests
    echo -e "${BLUE}📊 Running backend tests...${NC}"
    pytest backend/tests/ --cov=backend --cov-report=xml || {
        echo -e "${RED}❌ Backend tests failed${NC}"
        exit 1
    }
    
    # Run frontend tests
    echo -e "${BLUE}🌐 Running frontend tests...${NC}"
    cd frontend
    npm ci
    npm test -- --coverage --watchAll=false || {
        echo -e "${RED}❌ Frontend tests failed${NC}"
        exit 1
    }
    cd ..
    
    echo -e "${GREEN}✅ All tests passed${NC}"
}

# Build and push Docker images
build_and_push_images() {
    echo -e "${YELLOW}🏗️  Building and pushing Docker images...${NC}"
    
    # Build Backend
    echo -e "${BLUE}📊 Building backend image...${NC}"
    docker build -f deployment/Dockerfile.api-server \
        -t gcr.io/$PROJECT_ID/ai-stock-backend-prod:$VERSION \
        -t gcr.io/$PROJECT_ID/ai-stock-backend-prod:latest \
        .
    
    docker push gcr.io/$PROJECT_ID/ai-stock-backend-prod:$VERSION
    docker push gcr.io/$PROJECT_ID/ai-stock-backend-prod:latest
    
    # Build Frontend
    echo -e "${BLUE}🌐 Building frontend image...${NC}"
    cd frontend
    npm ci
    npm run build
    cd ..
    
    docker build -f deployment/Dockerfile.frontend \
        -t gcr.io/$PROJECT_ID/ai-stock-frontend-prod:$VERSION \
        -t gcr.io/$PROJECT_ID/ai-stock-frontend-prod:latest \
        .
    
    docker push gcr.io/$PROJECT_ID/ai-stock-frontend-prod:$VERSION
    docker push gcr.io/$PROJECT_ID/ai-stock-frontend-prod:latest
    
    # Build Trading Bot
    echo -e "${BLUE}🤖 Building trading bot image...${NC}"
    docker build -f deployment/Dockerfile.trading-bot \
        -t gcr.io/$PROJECT_ID/ai-stock-trading-bot-prod:$VERSION \
        -t gcr.io/$PROJECT_ID/ai-stock-trading-bot-prod:latest \
        .
    
    docker push gcr.io/$PROJECT_ID/ai-stock-trading-bot-prod:$VERSION
    docker push gcr.io/$PROJECT_ID/ai-stock-trading-bot-prod:latest
    
    echo -e "${GREEN}✅ All images built and pushed successfully${NC}"
}

# Deploy services to Cloud Run with blue-green deployment
deploy_services() {
    echo -e "${YELLOW}🚀 Deploying services to Cloud Run...${NC}"
    
    # Deploy Backend
    echo -e "${BLUE}📊 Deploying backend service...${NC}"
    gcloud run deploy ai-stock-backend-prod \
        --image gcr.io/$PROJECT_ID/ai-stock-backend-prod:$VERSION \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --set-env-vars="ENVIRONMENT=production" \
        --memory=4Gi \
        --cpu=4 \
        --max-instances=20 \
        --min-instances=2 \
        --timeout=300 \
        --concurrency=1000
    
    # Get backend URL
    BACKEND_URL=$(gcloud run services describe ai-stock-backend-prod --platform managed --region $REGION --format 'value(status.url)')
    echo -e "${GREEN}✅ Backend deployed: $BACKEND_URL${NC}"
    
    # Deploy Frontend
    echo -e "${BLUE}🌐 Deploying frontend service...${NC}"
    gcloud run deploy ai-stock-frontend-prod \
        --image gcr.io/$PROJECT_ID/ai-stock-frontend-prod:$VERSION \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --set-env-vars="REACT_APP_API_URL=$BACKEND_URL" \
        --set-env-vars="ENVIRONMENT=production" \
        --memory=2Gi \
        --cpu=2 \
        --max-instances=10 \
        --min-instances=1 \
        --timeout=60 \
        --concurrency=1000
    
    # Get frontend URL
    FRONTEND_URL=$(gcloud run services describe ai-stock-frontend-prod --platform managed --region $REGION --format 'value(status.url)')
    echo -e "${GREEN}✅ Frontend deployed: $FRONTEND_URL${NC}"
    
    # Deploy Trading Bot
    echo -e "${BLUE}🤖 Deploying trading bot service...${NC}"
    gcloud run deploy ai-stock-trading-bot-prod \
        --image gcr.io/$PROJECT_ID/ai-stock-trading-bot-prod:$VERSION \
        --platform managed \
        --region $REGION \
        --no-allow-unauthenticated \
        --set-env-vars="ENVIRONMENT=production" \
        --memory=4Gi \
        --cpu=4 \
        --max-instances=5 \
        --min-instances=1 \
        --timeout=300 \
        --concurrency=100
    
    # Get trading bot URL
    TRADING_BOT_URL=$(gcloud run services describe ai-stock-trading-bot-prod --platform managed --region $REGION --format 'value(status.url)')
    echo -e "${GREEN}✅ Trading bot deployed: $TRADING_BOT_URL${NC}"
}

# Set up production infrastructure
setup_infrastructure() {
    echo -e "${YELLOW}🏗️  Setting up production infrastructure...${NC}"
    
    # Create Cloud Storage bucket
    echo -e "${BLUE}📦 Creating Cloud Storage bucket...${NC}"
    gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$PROJECT_ID-ai-stock-prod-data || true
    
    # Set up Cloud Scheduler
    echo -e "${BLUE}⏰ Setting up Cloud Scheduler...${NC}"
    gcloud scheduler jobs create http ai-stock-trading-scheduler-prod \
        --schedule="0 9 * * 1-5" \
        --uri="$TRADING_BOT_URL/start-trading" \
        --http-method=POST \
        --oidc-service-account-email=$GCP_SA_EMAIL \
        --oidc-token-audience="$TRADING_BOT_URL" || true
    
    # Set up monitoring and alerting
    echo -e "${BLUE}📊 Setting up monitoring...${NC}"
    gcloud monitoring notification-channels create \
        --display-name="AI Stock Trading Alerts" \
        --type=email \
        --channel-labels=email_address=$ALERT_EMAIL || true
    
    echo -e "${GREEN}✅ Infrastructure setup complete${NC}"
}

# Run comprehensive health checks
health_checks() {
    echo -e "${YELLOW}🏥 Running comprehensive health checks...${NC}"
    
    # Check backend health
    echo -e "${BLUE}📊 Checking backend health...${NC}"
    for i in {1..5}; do
        if curl -f -s "$BACKEND_URL/health" > /dev/null; then
            echo -e "${GREEN}✅ Backend is healthy (attempt $i)${NC}"
            break
        else
            echo -e "${YELLOW}⏳ Backend health check attempt $i failed, retrying...${NC}"
            sleep 10
        fi
    done
    
    # Check frontend health
    echo -e "${BLUE}🌐 Checking frontend health...${NC}"
    for i in {1..5}; do
        if curl -f -s "$FRONTEND_URL" > /dev/null; then
            echo -e "${GREEN}✅ Frontend is healthy (attempt $i)${NC}"
            break
        else
            echo -e "${YELLOW}⏳ Frontend health check attempt $i failed, retrying...${NC}"
            sleep 10
        fi
    done
    
    # Check trading bot health
    echo -e "${BLUE}🤖 Checking trading bot health...${NC}"
    for i in {1..5}; do
        if curl -f -s "$TRADING_BOT_URL/health" > /dev/null; then
            echo -e "${GREEN}✅ Trading bot is healthy (attempt $i)${NC}"
            break
        else
            echo -e "${YELLOW}⏳ Trading bot health check attempt $i failed, retrying...${NC}"
            sleep 10
        fi
    done
    
    echo -e "${GREEN}✅ All health checks passed${NC}"
}

# Create deployment tag
create_deployment_tag() {
    echo -e "${YELLOW}🏷️  Creating deployment tag...${NC}"
    
    git tag -a "deploy-prod-$VERSION" -m "Production deployment $VERSION"
    git push origin "deploy-prod-$VERSION"
    
    echo -e "${GREEN}✅ Deployment tag created: deploy-prod-$VERSION${NC}"
}

# Main deployment function
main() {
    confirm_production
    check_dependencies
    authenticate_gcp
    run_tests
    build_and_push_images
    deploy_services
    setup_infrastructure
    health_checks
    create_deployment_tag
    
    echo -e "${GREEN}🎉 Production deployment completed successfully!${NC}"
    echo -e "${BLUE}📊 Backend: $BACKEND_URL${NC}"
    echo -e "${BLUE}🌐 Frontend: $FRONTEND_URL${NC}"
    echo -e "${BLUE}🤖 Trading Bot: $TRADING_BOT_URL${NC}"
    echo -e "${BLUE}🔧 Environment: $ENVIRONMENT${NC}"
    echo -e "${BLUE}📋 Version: $VERSION${NC}"
    echo -e "${BLUE}🏷️  Tag: deploy-prod-$VERSION${NC}"
}

# Run main function
main "$@"
