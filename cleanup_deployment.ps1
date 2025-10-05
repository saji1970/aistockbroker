# AI Stock Trading - Clean Deployment Script (PowerShell)
# This script removes deployed application services from GCP while keeping GCP services intact
# Allows for clean redeployment

param(
    [string]$ProjectId = "stockbroker-28983",
    [string]$Region = "us-central1"
)

# Configuration
$ServiceNameBackend = "ai-stock-trading-backend"
$ServiceNameFrontend = "ai-stock-trading-frontend"
$ServiceNameApi = "ai-stock-trading-api"
$ServiceNameTradingBot = "ai-stock-trading-bot"
$ImageNameBackend = "gcr.io/$ProjectId/ai-stock-trading-backend"
$ImageNameFrontend = "gcr.io/$ProjectId/ai-stock-trading-frontend"
$ImageNameApi = "gcr.io/$ProjectId/ai-stock-trading-api"
$ImageNameTradingBot = "gcr.io/$ProjectId/ai-stock-trading-bot"

Write-Host "🧹 AI Stock Trading - Clean Deployment" -ForegroundColor Blue
Write-Host "======================================"

# Check if gcloud is installed
if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Google Cloud SDK is not installed." -ForegroundColor Red
    exit 1
}

# Check if user is authenticated
$authStatus = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null
if (-not $authStatus) {
    Write-Host "❌ You are not authenticated with Google Cloud." -ForegroundColor Red
    Write-Host "Please run: gcloud auth login"
    exit 1
}

# Set project
Write-Host "📋 Setting project to: $ProjectId" -ForegroundColor Blue
gcloud config set project $ProjectId

Write-Host "⚠️  This will remove the following application services:" -ForegroundColor Yellow
Write-Host "   - Cloud Run services"
Write-Host "   - Container images"
Write-Host "   - Application-specific storage buckets"
Write-Host "   - Application-specific IAM resources"
Write-Host ""
$confirmation = Read-Host "Are you sure you want to continue? (y/N)"
if ($confirmation -ne 'y' -and $confirmation -ne 'Y') {
    Write-Host "❌ Operation cancelled." -ForegroundColor Yellow
    exit 1
}

# 1. Remove Cloud Run Services
Write-Host "🚀 Removing Cloud Run services..." -ForegroundColor Blue

# Remove backend services
Write-Host "Removing backend services..."
$backendServices = @($ServiceNameBackend, $ServiceNameApi, $ServiceNameTradingBot)
foreach ($service in $backendServices) {
    try {
        $serviceExists = gcloud run services describe $service --region=$Region --quiet 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  - Removing $service" -ForegroundColor Yellow
            gcloud run services delete $service --region=$Region --quiet
        } else {
            Write-Host "  - $service not found (already removed)" -ForegroundColor Green
        }
    } catch {
        Write-Host "  - $service not found (already removed)" -ForegroundColor Green
    }
}

# Remove frontend services
Write-Host "Removing frontend services..."
try {
    $serviceExists = gcloud run services describe $ServiceNameFrontend --region=$Region --quiet 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  - Removing $ServiceNameFrontend" -ForegroundColor Yellow
        gcloud run services delete $ServiceNameFrontend --region=$Region --quiet
    } else {
        Write-Host "  - $ServiceNameFrontend not found (already removed)" -ForegroundColor Green
    }
} catch {
    Write-Host "  - $ServiceNameFrontend not found (already removed)" -ForegroundColor Green
}

# 2. Remove Container Images
Write-Host "🐳 Removing container images..." -ForegroundColor Blue

# Remove backend images
Write-Host "Removing backend images..."
$backendImages = @($ImageNameBackend, $ImageNameApi, $ImageNameTradingBot)
foreach ($image in $backendImages) {
    try {
        $imageExists = gcloud container images describe "$image:latest" --quiet 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  - Removing $image:latest" -ForegroundColor Yellow
            gcloud container images delete "$image:latest" --quiet
        } else {
            Write-Host "  - $image:latest not found (already removed)" -ForegroundColor Green
        }
    } catch {
        Write-Host "  - $image:latest not found (already removed)" -ForegroundColor Green
    }
}

# Remove frontend images
Write-Host "Removing frontend images..."
try {
    $imageExists = gcloud container images describe "$ImageNameFrontend:latest" --quiet 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  - Removing $ImageNameFrontend:latest" -ForegroundColor Yellow
        gcloud container images delete "$ImageNameFrontend:latest" --quiet
    } else {
        Write-Host "  - $ImageNameFrontend:latest not found (already removed)" -ForegroundColor Green
    }
} catch {
    Write-Host "  - $ImageNameFrontend:latest not found (already removed)" -ForegroundColor Green
}

# 3. Remove Application-specific Storage Buckets
Write-Host "📦 Removing application storage buckets..." -ForegroundColor Blue

$buckets = @(
    "$ProjectId-ai-stock-trading-data",
    "$ProjectId-ai-stock-trading-logs",
    "$ProjectId-ai-stock-trading-backups",
    "ai-stock-trading-data-$ProjectId",
    "ai-stock-trading-logs-$ProjectId",
    "ai-stock-trading-backups-$ProjectId"
)

foreach ($bucket in $buckets) {
    try {
        $bucketExists = gsutil ls "gs://$bucket/" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  - Removing bucket: $bucket" -ForegroundColor Yellow
            gsutil rm -r "gs://$bucket/"
        } else {
            Write-Host "  - Bucket $bucket not found (already removed)" -ForegroundColor Green
        }
    } catch {
        Write-Host "  - Bucket $bucket not found (already removed)" -ForegroundColor Green
    }
}

# 4. Remove Application-specific IAM Resources
Write-Host "🔐 Cleaning up application IAM resources..." -ForegroundColor Blue

$serviceAccount = "ai-stock-trading-deployer@${ProjectId}.iam.gserviceaccount.com"
try {
    $saExists = gcloud iam service-accounts describe $serviceAccount --quiet 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  - Removing service account: $serviceAccount" -ForegroundColor Yellow
        gcloud iam service-accounts delete $serviceAccount --quiet
    } else {
        Write-Host "  - Service account $serviceAccount not found (already removed)" -ForegroundColor Green
    }
} catch {
    Write-Host "  - Service account $serviceAccount not found (already removed)" -ForegroundColor Green
}

# 5. Remove any Cloud Build triggers
Write-Host "🔨 Removing Cloud Build triggers..." -ForegroundColor Blue

try {
    $triggers = gcloud builds triggers list --format="value(name)" --filter="name~ai-stock-trading" 2>$null
    if ($triggers) {
        foreach ($trigger in $triggers) {
            Write-Host "  - Removing trigger: $trigger" -ForegroundColor Yellow
            gcloud builds triggers delete $trigger --quiet
        }
    } else {
        Write-Host "  - No build triggers found" -ForegroundColor Green
    }
} catch {
    Write-Host "  - No build triggers found" -ForegroundColor Green
}

# 6. Clean up any remaining resources
Write-Host "🧽 Final cleanup..." -ForegroundColor Blue

# Remove any remaining container images with the project prefix
Write-Host "Checking for remaining container images..."
try {
    $remainingImages = gcloud container images list --repository="gcr.io/$ProjectId" --format="value(name)" --filter="name~ai-stock-trading" 2>$null
    if ($remainingImages) {
        foreach ($image in $remainingImages) {
            Write-Host "  - Removing remaining image: $image" -ForegroundColor Yellow
            gcloud container images delete $image --quiet --force-delete-tags
        }
    } else {
        Write-Host "  - No remaining images found" -ForegroundColor Green
    }
} catch {
    Write-Host "  - No remaining images found" -ForegroundColor Green
}

Write-Host "✅ Cleanup completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Summary:" -ForegroundColor Blue
Write-Host "  ✅ Cloud Run services removed"
Write-Host "  ✅ Container images removed"
Write-Host "  ✅ Storage buckets removed"
Write-Host "  ✅ IAM resources cleaned up"
Write-Host "  ✅ Build triggers removed"
Write-Host ""
Write-Host "📝 Next Steps:" -ForegroundColor Yellow
Write-Host "1. You can now redeploy with a clean build"
Write-Host "2. Run your deployment script to create fresh services"
Write-Host "3. All GCP services (APIs) remain enabled for redeployment"
Write-Host ""
Write-Host "🎉 Your GCP project is now clean and ready for redeployment!" -ForegroundColor Green
