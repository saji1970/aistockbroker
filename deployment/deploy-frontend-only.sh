#!/bin/bash

# Deploy frontend to Cloud Run with correct configuration

set -e

PROJECT_ID="aimodelfoundry"
REGION="us-central1"
SERVICE_NAME_FRONTEND="ai-stock-trading-frontend"
BACKEND_URL="https://ai-stock-trading-backend-ccrwk2lv6q-uc.a.run.app"

echo "🚀 Deploying frontend to Cloud Run..."

# Deploy frontend using the frontend Dockerfile
gcloud run deploy $SERVICE_NAME_FRONTEND \
    --image gcr.io/$PROJECT_ID/ai-stock-trading-frontend:latest \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --port 80 \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 5 \
    --set-env-vars "REACT_APP_API_URL=$BACKEND_URL" \
    --set-env-vars "NODE_ENV=production"

echo "✅ Frontend deployment completed!"
echo "Frontend URL: $(gcloud run services describe $SERVICE_NAME_FRONTEND --region=$REGION --format='value(status.url)')"
