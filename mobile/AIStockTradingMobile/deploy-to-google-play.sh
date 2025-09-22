#!/bin/bash

# AI Stock Trading Mobile - Google Play Store Deployment Script
# This script builds and prepares the app for Google Play Store deployment

set -e

echo "🚀 Preparing AI Stock Trading Mobile for Google Play Store deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "package.json" ] || [ ! -d "android" ]; then
    print_error "Please run this script from the AIStockTradingMobile directory"
    exit 1
fi

# Check Java version
JAVA_VERSION=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2)
if [[ "$JAVA_VERSION" != 17* ]]; then
    print_error "Java 17 is required for Android builds. Current version: $JAVA_VERSION"
    print_warning "Please install Java 17: brew install openjdk@17"
    exit 1
fi

print_success "Java version: $JAVA_VERSION"

# Clean previous builds
print_status "Cleaning previous builds..."
cd android
./gradlew clean
cd ..

# Install dependencies
print_status "Installing dependencies..."
npm install

# Build Android App Bundle
print_status "Building Android App Bundle (AAB)..."
cd android
./gradlew bundleRelease
cd ..

# Check if AAB was created
AAB_PATH="android/app/build/outputs/bundle/release/app-release.aab"
if [ -f "$AAB_PATH" ]; then
    AAB_SIZE=$(du -h "$AAB_PATH" | cut -f1)
    print_success "Android App Bundle created successfully!"
    print_success "File: $AAB_PATH"
    print_success "Size: $AAB_SIZE"
else
    print_error "Failed to create Android App Bundle"
    exit 1
fi

# Create deployment package
print_status "Creating deployment package..."
DEPLOY_DIR="google-play-deployment"
mkdir -p "$DEPLOY_DIR"

# Copy AAB file
cp "$AAB_PATH" "$DEPLOY_DIR/"

# Create deployment info
cat > "$DEPLOY_DIR/DEPLOYMENT_INFO.txt" << EOF
AI Stock Trading Mobile - Google Play Store Deployment

Generated: $(date)
AAB File: app-release.aab
Size: $AAB_SIZE

NEXT STEPS:
1. Go to Google Play Console: https://play.google.com/console
2. Create a new app or update existing app
3. Upload the AAB file: app-release.aab
4. Complete app information (description, screenshots, etc.)
5. Submit for review

APP INFORMATION:
- App Name: AI Stock Trading
- Version: 1.0.0
- Package: com.aistocktradingmobile
- Minimum SDK: 23 (Android 6.0)
- Target SDK: 34 (Android 14)

FEATURES:
- Real-time stock data and charts
- AI-powered predictions
- Portfolio management
- Multi-market support (8 countries)
- Technical analysis
- Natural language AI assistant

For detailed instructions, see: GOOGLE_PLAY_DEPLOYMENT.md
EOF

print_success "Deployment package created in: $DEPLOY_DIR"
print_success "Files created:"
echo "  📦 $DEPLOY_DIR/app-release.aab"
echo "  📄 $DEPLOY_DIR/DEPLOYMENT_INFO.txt"

echo ""
print_status "Google Play Store Deployment Summary:"
echo "  ✅ Android App Bundle (AAB) created successfully"
echo "  ✅ Deployment package prepared"
echo "  ✅ All files ready for upload"
echo ""
print_status "Next steps:"
echo "  1. 📱 Go to Google Play Console: https://play.google.com/console"
echo "  2. 💳 Pay $25 registration fee (if not already done)"
echo "  3. 📤 Upload the AAB file from: $DEPLOY_DIR/app-release.aab"
echo "  4. 📝 Complete app information and store listing"
echo "  5. 🔍 Submit for Google review (2-5 business days)"
echo ""
print_warning "Important: You'll need to create app screenshots and graphics assets"
print_warning "See GOOGLE_PLAY_DEPLOYMENT.md for detailed instructions"
echo ""
print_success "Your app is ready for Google Play Store! 🎉" 