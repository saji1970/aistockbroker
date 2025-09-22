#!/bin/bash

# AI Stock Trading System - Project Setup Script
# This script sets up the GCP project for deployment

set -e

# Configuration
PROJECT_ID="stockbroker-28983"
USER_EMAIL="saji651970@gmail.com"
REGION="us-central1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Setting up AI Stock Trading System for GCP Project: ${PROJECT_ID}${NC}"
echo -e "${BLUE}👤 User: ${USER_EMAIL}${NC}"

# Check if gcloud is installed
check_gcloud() {
    echo -e "${YELLOW}🔍 Checking Google Cloud SDK...${NC}"
    
    if ! command -v gcloud &> /dev/null; then
        echo -e "${RED}❌ gcloud CLI not found. Please install Google Cloud SDK.${NC}"
        echo -e "${YELLOW}📥 Install from: https://cloud.google.com/sdk/docs/install${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Google Cloud SDK found${NC}"
}

# Authenticate with Google Cloud
authenticate() {
    echo -e "${YELLOW}🔐 Authenticating with Google Cloud...${NC}"
    
    gcloud auth login --account=$USER_EMAIL
    gcloud config set project $PROJECT_ID
    
    echo -e "${GREEN}✅ Authentication successful${NC}"
}

# Enable required APIs
enable_apis() {
    echo -e "${YELLOW}🔧 Enabling required APIs...${NC}"
    
    # Core APIs
    gcloud services enable run.googleapis.com
    gcloud services enable containerregistry.googleapis.com
    gcloud services enable cloudbuild.googleapis.com
    
    # Additional APIs
    gcloud services enable cloudscheduler.googleapis.com
    gcloud services enable storage.googleapis.com
    gcloud services enable monitoring.googleapis.com
    gcloud services enable logging.googleapis.com
    
    echo -e "${GREEN}✅ All APIs enabled successfully${NC}"
}

# Create service account
create_service_account() {
    echo -e "${YELLOW}👤 Creating service account...${NC}"
    
    # Create service account
    gcloud iam service-accounts create ai-stock-trading-deployer \
        --display-name="AI Stock Trading Deployer" \
        --description="Service account for AI Stock Trading System deployment" \
        --project=$PROJECT_ID || echo -e "${YELLOW}⚠️  Service account may already exist${NC}"
    
    # Grant required roles
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:ai-stock-trading-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
        --role="roles/run.admin"
    
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:ai-stock-trading-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
        --role="roles/storage.admin"
    
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:ai-stock-trading-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
        --role="roles/cloudbuild.builds.editor"
    
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:ai-stock-trading-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
        --role="roles/cloudscheduler.admin"
    
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:ai-stock-trading-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
        --role="roles/monitoring.admin"
    
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:ai-stock-trading-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
        --role="roles/logging.admin"
    
    echo -e "${GREEN}✅ Service account created and configured${NC}"
}

# Generate service account key
generate_key() {
    echo -e "${YELLOW}🔑 Generating service account key...${NC}"
    
    # Create key file
    gcloud iam service-accounts keys create ai-stock-trading-key.json \
        --iam-account=ai-stock-trading-deployer@$PROJECT_ID.iam.gserviceaccount.com \
        --project=$PROJECT_ID
    
    echo -e "${GREEN}✅ Service account key generated: ai-stock-trading-key.json${NC}"
    echo -e "${YELLOW}⚠️  Keep this file secure and add it to GitHub secrets${NC}"
}

# Configure Docker
configure_docker() {
    echo -e "${YELLOW}🐳 Configuring Docker for GCR...${NC}"
    
    gcloud auth configure-docker
    
    echo -e "${GREEN}✅ Docker configured for Google Container Registry${NC}"
}

# Create storage buckets
create_buckets() {
    echo -e "${YELLOW}📦 Creating Cloud Storage buckets...${NC}"
    
    # Create staging bucket
    gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$PROJECT_ID-ai-stock-staging-data || echo -e "${YELLOW}⚠️  Staging bucket may already exist${NC}"
    
    # Create production bucket
    gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$PROJECT_ID-ai-stock-prod-data || echo -e "${YELLOW}⚠️  Production bucket may already exist${NC}"
    
    echo -e "${GREEN}✅ Storage buckets created${NC}"
}

# Display next steps
display_next_steps() {
    echo -e "${GREEN}🎉 Project setup completed successfully!${NC}"
    echo -e "${BLUE}📋 Next steps:${NC}"
    echo -e "${BLUE}1. Add GitHub secrets:${NC}"
    echo -e "${BLUE}   - GCP_SA_KEY: $(base64 -i ai-stock-trading-key.json)${NC}"
    echo -e "${BLUE}   - GCP_PROJECT_ID: $PROJECT_ID${NC}"
    echo -e "${BLUE}   - GCP_SA_EMAIL: ai-stock-trading-deployer@$PROJECT_ID.iam.gserviceaccount.com${NC}"
    echo -e "${BLUE}2. Go to GitHub repository settings${NC}"
    echo -e "${BLUE}3. Navigate to Secrets and variables → Actions${NC}"
    echo -e "${BLUE}4. Add the secrets listed above${NC}"
    echo -e "${BLUE}5. Push to master branch to trigger deployment${NC}"
    echo -e "${BLUE}6. Monitor deployment in GitHub Actions tab${NC}"
    echo -e "${YELLOW}⚠️  Remember to delete the key file after adding to GitHub secrets${NC}"
}

# Main setup function
main() {
    check_gcloud
    authenticate
    enable_apis
    create_service_account
    generate_key
    configure_docker
    create_buckets
    display_next_steps
}

# Run main function
main "$@"
