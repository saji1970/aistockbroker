#!/bin/bash

# Deploy frontend with updated icons
echo "Building frontend..."
cd frontend
npm run build

echo "Deploying to Cloud Run..."
cd ..
gcloud run deploy ai-stock-trading-frontend \
  --source frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars "REACT_APP_API_URL=https://ai-stock-trading-api-o6i75igepq-uc.a.run.app" \
  --timeout 3600 \
  --cpu 1 \
  --memory 1Gi

echo "Deployment complete!"

