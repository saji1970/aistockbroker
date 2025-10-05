#!/bin/bash

# AI Stock Trading - Clean Deployment Script
# This script removes deployed application services from GCP while keeping GCP services intact
# Allows for clean redeployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="stockbroker-28983"
REGION="us-central1"
SERVICE_NAME_BACKEND="ai-stock-trading-backend"
SERVICE_NAME_FRONTEND="ai-stock-trading-frontend"
SERVICE_NAME_API="ai-stock-trading-api"
SERVICE_NAME_TRADING_BOT="ai-stock-trading-bot"
IMAGE_NAME_BACKEND="gcr.io/${PROJECT_ID}/ai-stock-trading-backend"
IMAGE_NAME_FRONTEND="gcr.io/${PROJECT_ID}/ai-stock-trading-frontend"
IMAGE_NAME_API="gcr.io/${PROJECT_ID}/ai-stock-trading-api"
IMAGE_NAME_TRADING_BOT="gcr.io/${PROJECT_ID}/ai-stock-trading-bot"

echo -e "${BLUE}🧹 AI Stock Trading - Clean Deployment${NC}"
echo "======================================"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Google Cloud SDK is not installed.${NC}"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${RED}❌ You are not authenticated with Google Cloud.${NC}"
    echo "Please run: gcloud auth login"
    exit 1
fi

# Set project
echo -e "${BLUE}📋 Setting project to: $PROJECT_ID${NC}"
gcloud config set project $PROJECT_ID

echo -e "${YELLOW}⚠️  This will remove the following application services:${NC}"
echo "   - Cloud Run services"
echo "   - Container images"
echo "   - Application-specific storage buckets"
echo "   - Application-specific IAM resources"
echo ""
read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}❌ Operation cancelled.${NC}"
    exit 1
fi

# 1. Remove Cloud Run Services
echo -e "${BLUE}🚀 Removing Cloud Run services...${NC}"

# List and remove backend services
echo "Removing backend services..."
for service in $SERVICE_NAME_BACKEND $SERVICE_NAME_API $SERVICE_NAME_TRADING_BOT; do
    if gcloud run services describe $service --region=$REGION --quiet 2>/dev/null; then
        echo "  - Removing $service"
        gcloud run services delete $service --region=$REGION --quiet
    else
        echo "  - $service not found (already removed)"
    fi
done

# List and remove frontend services
echo "Removing frontend services..."
for service in $SERVICE_NAME_FRONTEND; do
    if gcloud run services describe $service --region=$REGION --quiet 2>/dev/null; then
        echo "  - Removing $service"
        gcloud run services delete $service --region=$REGION --quiet
    else
        echo "  - $service not found (already removed)"
    fi
done

# 2. Remove Container Images
echo -e "${BLUE}🐳 Removing container images...${NC}"

# Remove backend images
echo "Removing backend images..."
for image in $IMAGE_NAME_BACKEND $IMAGE_NAME_API $IMAGE_NAME_TRADING_BOT; do
    if gcloud container images describe $image:latest --quiet 2>/dev/null; then
        echo "  - Removing $image:latest"
        gcloud container images delete $image:latest --quiet
    else
        echo "  - $image:latest not found (already removed)"
    fi
done

# Remove frontend images
echo "Removing frontend images..."
for image in $IMAGE_NAME_FRONTEND; do
    if gcloud container images describe $image:latest --quiet 2>/dev/null; then
        echo "  - Removing $image:latest"
        gcloud container images delete $image:latest --quiet
    else
        echo "  - $image:latest not found (already removed)"
    fi
done

# 3. Remove Application-specific Storage Buckets
echo -e "${BLUE}📦 Removing application storage buckets...${NC}"

# List of potential bucket names
BUCKETS=(
    "${PROJECT_ID}-ai-stock-trading-data"
    "${PROJECT_ID}-ai-stock-trading-logs"
    "${PROJECT_ID}-ai-stock-trading-backups"
    "ai-stock-trading-data-${PROJECT_ID}"
    "ai-stock-trading-logs-${PROJECT_ID}"
    "ai-stock-trading-backups-${PROJECT_ID}"
)

for bucket in "${BUCKETS[@]}"; do
    if gsutil ls gs://$bucket/ >/dev/null 2>&1; then
        echo "  - Removing bucket: $bucket"
        gsutil rm -r gs://$bucket/
    else
        echo "  - Bucket $bucket not found (already removed)"
    fi
done

# 4. Remove Application-specific IAM Resources
echo -e "${BLUE}🔐 Cleaning up application IAM resources...${NC}"

# Remove service account if it exists
SERVICE_ACCOUNT="ai-stock-trading-deployer@${PROJECT_ID}.iam.gserviceaccount.com"
if gcloud iam service-accounts describe $SERVICE_ACCOUNT --quiet 2>/dev/null; then
    echo "  - Removing service account: $SERVICE_ACCOUNT"
    gcloud iam service-accounts delete $SERVICE_ACCOUNT --quiet
else
    echo "  - Service account $SERVICE_ACCOUNT not found (already removed)"
fi

# 5. Remove any Cloud Build triggers
echo -e "${BLUE}🔨 Removing Cloud Build triggers...${NC}"

# List and remove build triggers
TRIGGERS=$(gcloud builds triggers list --format="value(name)" --filter="name~ai-stock-trading" 2>/dev/null || true)
if [ ! -z "$TRIGGERS" ]; then
    for trigger in $TRIGGERS; do
        echo "  - Removing trigger: $trigger"
        gcloud builds triggers delete $trigger --quiet
    done
else
    echo "  - No build triggers found"
fi

# 6. Clean up any remaining resources
echo -e "${BLUE}🧽 Final cleanup...${NC}"

# Remove any remaining container images with the project prefix
echo "Checking for remaining container images..."
REMAINING_IMAGES=$(gcloud container images list --repository=gcr.io/$PROJECT_ID --format="value(name)" --filter="name~ai-stock-trading" 2>/dev/null || true)
if [ ! -z "$REMAINING_IMAGES" ]; then
    for image in $REMAINING_IMAGES; do
        echo "  - Removing remaining image: $image"
        gcloud container images delete $image --quiet --force-delete-tags
    done
else
    echo "  - No remaining images found"
fi

echo -e "${GREEN}✅ Cleanup completed successfully!${NC}"
echo ""
echo -e "${BLUE}📊 Summary:${NC}"
echo "  ✅ Cloud Run services removed"
echo "  ✅ Container images removed"
echo "  ✅ Storage buckets removed"
echo "  ✅ IAM resources cleaned up"
echo "  ✅ Build triggers removed"
echo ""
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo "1. You can now redeploy with a clean build"
echo "2. Run your deployment script to create fresh services"
echo "3. All GCP services (APIs) remain enabled for redeployment"
echo ""
echo -e "${GREEN}🎉 Your GCP project is now clean and ready for redeployment!${NC}"
