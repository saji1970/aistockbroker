# AI Stock Trading System - Simple Project Setup Script
# This script sets up the GCP project for deployment

$PROJECT_ID = "stockbroker-28983"
$USER_EMAIL = "saji651970@gmail.com"
$REGION = "us-central1"

Write-Host "🚀 Setting up AI Stock Trading System for GCP Project: $PROJECT_ID" -ForegroundColor Blue
Write-Host "👤 User: $USER_EMAIL" -ForegroundColor Blue

# Check if gcloud is installed
Write-Host "🔍 Checking Google Cloud SDK..." -ForegroundColor Yellow
if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Host "❌ gcloud CLI not found. Please install Google Cloud SDK." -ForegroundColor Red
    Write-Host "📥 Install from: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Google Cloud SDK found" -ForegroundColor Green

# Authenticate with Google Cloud
Write-Host "🔐 Authenticating with Google Cloud..." -ForegroundColor Yellow
gcloud auth login --account=$USER_EMAIL
gcloud config set project $PROJECT_ID
Write-Host "✅ Authentication successful" -ForegroundColor Green

# Enable required APIs
Write-Host "🔧 Enabling required APIs..." -ForegroundColor Yellow
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable monitoring.googleapis.com
gcloud services enable logging.googleapis.com
Write-Host "✅ All APIs enabled successfully" -ForegroundColor Green

# Create service account
Write-Host "👤 Creating service account..." -ForegroundColor Yellow
try {
    gcloud iam service-accounts create ai-stock-trading-deployer --display-name="AI Stock Trading Deployer" --description="Service account for AI Stock Trading System deployment" --project=$PROJECT_ID
    Write-Host "✅ Service account created" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Service account may already exist" -ForegroundColor Yellow
}

# Grant required roles
Write-Host "🔑 Granting permissions..." -ForegroundColor Yellow
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:ai-stock-trading-deployer@$PROJECT_ID.iam.gserviceaccount.com" --role="roles/run.admin"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:ai-stock-trading-deployer@$PROJECT_ID.iam.gserviceaccount.com" --role="roles/storage.admin"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:ai-stock-trading-deployer@$PROJECT_ID.iam.gserviceaccount.com" --role="roles/cloudbuild.builds.editor"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:ai-stock-trading-deployer@$PROJECT_ID.iam.gserviceaccount.com" --role="roles/cloudscheduler.admin"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:ai-stock-trading-deployer@$PROJECT_ID.iam.gserviceaccount.com" --role="roles/monitoring.admin"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:ai-stock-trading-deployer@$PROJECT_ID.iam.gserviceaccount.com" --role="roles/logging.admin"
Write-Host "✅ Permissions granted" -ForegroundColor Green

# Generate service account key
Write-Host "🔑 Generating service account key..." -ForegroundColor Yellow
gcloud iam service-accounts keys create ai-stock-trading-key.json --iam-account="ai-stock-trading-deployer@$PROJECT_ID.iam.gserviceaccount.com" --project=$PROJECT_ID
Write-Host "✅ Service account key generated: ai-stock-trading-key.json" -ForegroundColor Green

# Configure Docker
Write-Host "🐳 Configuring Docker for GCR..." -ForegroundColor Yellow
gcloud auth configure-docker
Write-Host "✅ Docker configured for Google Container Registry" -ForegroundColor Green

# Create storage buckets
Write-Host "📦 Creating Cloud Storage buckets..." -ForegroundColor Yellow
try {
    gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION "gs://$PROJECT_ID-ai-stock-staging-data"
    Write-Host "✅ Staging bucket created" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Staging bucket may already exist" -ForegroundColor Yellow
}

try {
    gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION "gs://$PROJECT_ID-ai-stock-prod-data"
    Write-Host "✅ Production bucket created" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Production bucket may already exist" -ForegroundColor Yellow
}

# Display next steps
Write-Host "🎉 Project setup completed successfully!" -ForegroundColor Green
Write-Host "📋 Next steps:" -ForegroundColor Blue
Write-Host "1. Add GitHub secrets:" -ForegroundColor Blue
Write-Host "   - GCP_SA_KEY: [Base64 encoded key from ai-stock-trading-key.json]" -ForegroundColor Blue
Write-Host "   - GCP_PROJECT_ID: $PROJECT_ID" -ForegroundColor Blue
Write-Host "   - GCP_SA_EMAIL: ai-stock-trading-deployer@$PROJECT_ID.iam.gserviceaccount.com" -ForegroundColor Blue
Write-Host "2. Go to GitHub repository settings" -ForegroundColor Blue
Write-Host "3. Navigate to Secrets and variables → Actions" -ForegroundColor Blue
Write-Host "4. Add the secrets listed above" -ForegroundColor Blue
Write-Host "5. Push to master branch to trigger deployment" -ForegroundColor Blue
Write-Host "6. Monitor deployment in GitHub Actions tab" -ForegroundColor Blue
Write-Host "⚠️  Remember to delete the key file after adding to GitHub secrets" -ForegroundColor Yellow

# Show base64 encoded key
if (Test-Path "ai-stock-trading-key.json") {
    $keyContent = Get-Content "ai-stock-trading-key.json" -Raw
    $base64Key = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($keyContent))
    Write-Host "🔑 Base64 encoded key:" -ForegroundColor Yellow
    Write-Host $base64Key -ForegroundColor Cyan
}
