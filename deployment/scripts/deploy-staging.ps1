# AI Stock Trading System - Staging Deployment Script (PowerShell)
# This script deploys the application to Google Cloud Platform staging environment

param(
    [string]$ProjectId = $env:GCP_PROJECT_ID,
    [string]$Region = "us-central1",
    [string]$Environment = "staging"
)

# Configuration
$PROJECT_ID = if ($ProjectId) { $ProjectId } else { "stockbroker-28983" }
$REGION = $Region
$ENVIRONMENT = $Environment
$SERVICE_ACCOUNT_KEY = $env:GCP_SA_KEY

Write-Host "🚀 Starting AI Stock Trading System Staging Deployment" -ForegroundColor Blue
Write-Host "📦 Project: $PROJECT_ID" -ForegroundColor Blue
Write-Host "🌍 Region: $REGION" -ForegroundColor Blue
Write-Host "🔧 Environment: $ENVIRONMENT" -ForegroundColor Blue

# Check if required tools are installed
function Check-Dependencies {
    Write-Host "🔍 Checking dependencies..." -ForegroundColor Yellow
    
    if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
        Write-Host "❌ gcloud CLI not found. Please install Google Cloud SDK." -ForegroundColor Red
        exit 1
    }
    
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Host "❌ Docker not found. Please install Docker." -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ All dependencies found" -ForegroundColor Green
}

# Authenticate with Google Cloud
function Authenticate-GCP {
    Write-Host "🔐 Authenticating with Google Cloud..." -ForegroundColor Yellow
    
    if ($SERVICE_ACCOUNT_KEY) {
        $SERVICE_ACCOUNT_KEY | Out-File -FilePath "temp-gcp-key.json" -Encoding UTF8
        gcloud auth activate-service-account --key-file="temp-gcp-key.json"
        Remove-Item "temp-gcp-key.json"
    } else {
        gcloud auth login
    }
    
    gcloud config set project $PROJECT_ID
    gcloud auth configure-docker
    
    Write-Host "✅ Authentication successful" -ForegroundColor Green
}

# Build and push Docker images
function Build-AndPush-Images {
    Write-Host "🏗️  Building and pushing Docker images..." -ForegroundColor Yellow
    
    # Build Backend
    Write-Host "📊 Building backend image..." -ForegroundColor Blue
    docker build -f deployment/Dockerfile.api-server `
        -t "gcr.io/$PROJECT_ID/ai-stock-backend-staging:latest" `
        -t "gcr.io/$PROJECT_ID/ai-stock-backend-staging:$(git rev-parse --short HEAD)" `
        .
    
    docker push "gcr.io/$PROJECT_ID/ai-stock-backend-staging:latest"
    docker push "gcr.io/$PROJECT_ID/ai-stock-backend-staging:$(git rev-parse --short HEAD)"
    
    # Build Frontend
    Write-Host "🌐 Building frontend image..." -ForegroundColor Blue
    Set-Location frontend
    npm ci
    npm run build
    Set-Location ..
    
    docker build -f deployment/Dockerfile.frontend `
        -t "gcr.io/$PROJECT_ID/ai-stock-frontend-staging:latest" `
        -t "gcr.io/$PROJECT_ID/ai-stock-frontend-staging:$(git rev-parse --short HEAD)" `
        .
    
    docker push "gcr.io/$PROJECT_ID/ai-stock-frontend-staging:latest"
    docker push "gcr.io/$PROJECT_ID/ai-stock-frontend-staging:$(git rev-parse --short HEAD)"
    
    # Build Trading Bot
    Write-Host "🤖 Building trading bot image..." -ForegroundColor Blue
    docker build -f deployment/Dockerfile.trading-bot `
        -t "gcr.io/$PROJECT_ID/ai-stock-trading-bot-staging:latest" `
        -t "gcr.io/$PROJECT_ID/ai-stock-trading-bot-staging:$(git rev-parse --short HEAD)" `
        .
    
    docker push "gcr.io/$PROJECT_ID/ai-stock-trading-bot-staging:latest"
    docker push "gcr.io/$PROJECT_ID/ai-stock-trading-bot-staging:$(git rev-parse --short HEAD)"
    
    Write-Host "✅ All images built and pushed successfully" -ForegroundColor Green
}

# Deploy services to Cloud Run
function Deploy-Services {
    Write-Host "🚀 Deploying services to Cloud Run..." -ForegroundColor Yellow
    
    # Deploy Backend
    Write-Host "📊 Deploying backend service..." -ForegroundColor Blue
    gcloud run deploy ai-stock-backend-staging `
        --image "gcr.io/$PROJECT_ID/ai-stock-backend-staging:latest" `
        --platform managed `
        --region $REGION `
        --allow-unauthenticated `
        --set-env-vars="ENVIRONMENT=staging" `
        --memory=2Gi `
        --cpu=2 `
        --max-instances=5 `
        --min-instances=0 `
        --timeout=300
    
    # Get backend URL
    $BACKEND_URL = gcloud run services describe ai-stock-backend-staging --platform managed --region $REGION --format 'value(status.url)'
    Write-Host "✅ Backend deployed: $BACKEND_URL" -ForegroundColor Green
    
    # Deploy Frontend
    Write-Host "🌐 Deploying frontend service..." -ForegroundColor Blue
    gcloud run deploy ai-stock-frontend-staging `
        --image "gcr.io/$PROJECT_ID/ai-stock-frontend-staging:latest" `
        --platform managed `
        --region $REGION `
        --allow-unauthenticated `
        --set-env-vars="REACT_APP_API_URL=$BACKEND_URL" `
        --set-env-vars="ENVIRONMENT=staging" `
        --memory=1Gi `
        --cpu=1 `
        --max-instances=3 `
        --min-instances=0 `
        --timeout=60
    
    # Get frontend URL
    $FRONTEND_URL = gcloud run services describe ai-stock-frontend-staging --platform managed --region $REGION --format 'value(status.url)'
    Write-Host "✅ Frontend deployed: $FRONTEND_URL" -ForegroundColor Green
    
    # Deploy Trading Bot
    Write-Host "🤖 Deploying trading bot service..." -ForegroundColor Blue
    gcloud run deploy ai-stock-trading-bot-staging `
        --image "gcr.io/$PROJECT_ID/ai-stock-trading-bot-staging:latest" `
        --platform managed `
        --region $REGION `
        --no-allow-unauthenticated `
        --set-env-vars="ENVIRONMENT=staging" `
        --memory=2Gi `
        --cpu=2 `
        --max-instances=2 `
        --min-instances=0 `
        --timeout=300
    
    # Get trading bot URL
    $TRADING_BOT_URL = gcloud run services describe ai-stock-trading-bot-staging --platform managed --region $REGION --format 'value(status.url)'
    Write-Host "✅ Trading bot deployed: $TRADING_BOT_URL" -ForegroundColor Green
    
    return @{
        BackendUrl = $BACKEND_URL
        FrontendUrl = $FRONTEND_URL
        TradingBotUrl = $TRADING_BOT_URL
    }
}

# Set up infrastructure
function Setup-Infrastructure {
    param($TradingBotUrl)
    
    Write-Host "🏗️  Setting up infrastructure..." -ForegroundColor Yellow
    
    # Create Cloud Storage bucket
    Write-Host "📦 Creating Cloud Storage bucket..." -ForegroundColor Blue
    gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION "gs://$PROJECT_ID-ai-stock-staging-data" 2>$null
    
    # Set up Cloud Scheduler
    Write-Host "⏰ Setting up Cloud Scheduler..." -ForegroundColor Blue
    gcloud scheduler jobs create http ai-stock-trading-scheduler-staging `
        --schedule="0 9 * * 1-5" `
        --uri="$TradingBotUrl/start-trading" `
        --http-method=POST `
        --oidc-service-account-email=$env:GCP_SA_EMAIL `
        --oidc-token-audience="$TradingBotUrl" 2>$null
    
    Write-Host "✅ Infrastructure setup complete" -ForegroundColor Green
}

# Run health checks
function Test-HealthChecks {
    param($BackendUrl, $FrontendUrl)
    
    Write-Host "🏥 Running health checks..." -ForegroundColor Yellow
    
    # Check backend health
    Write-Host "📊 Checking backend health..." -ForegroundColor Blue
    try {
        $response = Invoke-WebRequest -Uri "$BackendUrl/health" -UseBasicParsing -TimeoutSec 30
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Backend is healthy" -ForegroundColor Green
        } else {
            Write-Host "❌ Backend health check failed" -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "❌ Backend health check failed: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
    
    # Check frontend health
    Write-Host "🌐 Checking frontend health..." -ForegroundColor Blue
    try {
        $response = Invoke-WebRequest -Uri $FrontendUrl -UseBasicParsing -TimeoutSec 30
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Frontend is healthy" -ForegroundColor Green
        } else {
            Write-Host "❌ Frontend health check failed" -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "❌ Frontend health check failed: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ All health checks passed" -ForegroundColor Green
}

# Main deployment function
function Main {
    Check-Dependencies
    Authenticate-GCP
    Build-AndPush-Images
    $urls = Deploy-Services
    Setup-Infrastructure -TradingBotUrl $urls.TradingBotUrl
    Test-HealthChecks -BackendUrl $urls.BackendUrl -FrontendUrl $urls.FrontendUrl
    
    Write-Host "🎉 Staging deployment completed successfully!" -ForegroundColor Green
    Write-Host "📊 Backend: $($urls.BackendUrl)" -ForegroundColor Blue
    Write-Host "🌐 Frontend: $($urls.FrontendUrl)" -ForegroundColor Blue
    Write-Host "🤖 Trading Bot: $($urls.TradingBotUrl)" -ForegroundColor Blue
    Write-Host "🔧 Environment: $ENVIRONMENT" -ForegroundColor Blue
}

# Run main function
Main
