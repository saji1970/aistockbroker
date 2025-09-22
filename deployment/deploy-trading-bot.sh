#!/bin/bash

# Deploy AI Trading Bot to Google Cloud Platform
# This script deploys the trading bot as a separate Cloud Run service

set -e

# Configuration
PROJECT_ID="aimodelfoundry"
REGION="us-central1"
SERVICE_NAME="ai-trading-bot"
IMAGE_NAME="gcr.io/$PROJECT_ID/ai-trading-bot"

echo "🚀 Deploying AI Trading Bot to Google Cloud Platform..."
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"
echo "=================================="

# Set the project
echo "📋 Setting project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build and deploy using Cloud Build
echo "🏗️ Building and deploying trading bot..."
gcloud builds submit --config cloudbuild-trading-bot.yaml

# Get the service URL
echo "🔗 Getting service URL..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')

echo "=================================="
echo "✅ Trading Bot deployed successfully!"
echo "🌐 Service URL: $SERVICE_URL"
echo "📊 API Endpoints:"
echo "   - Status: $SERVICE_URL/api/status"
echo "   - Portfolio: $SERVICE_URL/api/portfolio"
echo "   - Orders: $SERVICE_URL/api/orders"
echo "   - Performance: $SERVICE_URL/api/performance"
echo "   - Watchlist: $SERVICE_URL/api/watchlist"
echo "   - Strategies: $SERVICE_URL/api/strategies"
echo "=================================="

# Test the deployment
echo "🧪 Testing deployment..."
curl -f "$SERVICE_URL/api/status" && echo "✅ Health check passed!" || echo "❌ Health check failed!"

echo ""
echo "🎯 Next steps:"
echo "1. Update your frontend to use the new trading bot API URL"
echo "2. Test the trading bot functionality"
echo "3. Configure your watchlist and start trading!"
echo ""
echo "📚 Documentation: TRADING_BOT_INTEGRATION.md"
