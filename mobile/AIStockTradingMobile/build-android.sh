#!/bin/bash

# AI Stock Trading Mobile App - Android Build Script
# This script builds the complete Android app with all features

set -e

echo "🚀 Starting AI Stock Trading Mobile App Build..."

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
if [ ! -f "package.json" ]; then
    print_error "package.json not found. Please run this script from the AIStockTradingMobile directory."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed. Please install npm."
    exit 1
fi

# Check if React Native CLI is installed
if ! command -v npx &> /dev/null; then
    print_error "npx is not installed. Please install npx."
    exit 1
fi

print_status "Installing dependencies..."
npm install

print_status "Installing React Native dependencies..."
npx react-native install

print_status "Cleaning previous builds..."
cd android
./gradlew clean
cd ..

print_status "Generating release keystore if not exists..."
if [ ! -f "android/app/release.keystore" ]; then
    print_warning "Release keystore not found. Generating new one..."
    keytool -genkey -v -keystore android/app/release.keystore -alias aistocktrading -keyalg RSA -keysize 2048 -validity 10000 -storepass aistocktrading -keypass aistocktrading -dname "CN=AI Stock Trading, OU=Mobile, O=AI Stock Trading, L=San Francisco, S=CA, C=US"
    print_success "Release keystore generated successfully."
fi

print_status "Building Android APK..."
cd android
./gradlew assembleRelease
cd ..

print_status "Building Android App Bundle (AAB)..."
cd android
./gradlew bundleRelease
cd ..

print_status "Copying build outputs..."
mkdir -p build-outputs
cp android/app/build/outputs/apk/release/app-release.apk build-outputs/AIStockTrading.apk
cp android/app/build/outputs/bundle/release/app-release.aab build-outputs/AIStockTrading.aab

print_status "Creating deployment info..."
cat > build-outputs/DEPLOYMENT_INFO.txt << EOF
AI Stock Trading Mobile App - Build Information
==============================================

Build Date: $(date)
Build Type: Release
Platform: Android
Version: 1.0.0

Files Generated:
- AIStockTrading.apk (Android Package)
- AIStockTrading.aab (Android App Bundle)

APK Size: $(du -h build-outputs/AIStockTrading.apk | cut -f1)
AAB Size: $(du -h build-outputs/AIStockTrading.aab | cut -f1)

Features Included:
✅ Trading Bot Management
✅ Real-time Stock Data
✅ AI Assistant
✅ Portfolio Management
✅ Technical Analysis
✅ Charts and Visualizations
✅ Push Notifications
✅ Offline Support
✅ Material Design UI

API Endpoints:
- Main API: https://ai-stock-trading-api-1024040140027.us-central1.run.app
- Trading Bot: https://ai-stock-trading-backend-1024040140027.us-central1.run.app

Installation:
1. Enable "Install from Unknown Sources" on your Android device
2. Transfer the APK file to your device
3. Install the APK file
4. Launch the app and enjoy!

For Google Play Store:
- Use the AAB file for Google Play Console upload
- The AAB file is optimized for Play Store distribution

Support:
- GitHub: https://github.com/your-repo/ai-stock-trading
- Documentation: README.md
- Issues: GitHub Issues

EOF

print_success "Build completed successfully!"
print_status "Build outputs are available in the 'build-outputs' directory:"
print_status "  - AIStockTrading.apk (for direct installation)"
print_status "  - AIStockTrading.aab (for Google Play Store)"
print_status "  - DEPLOYMENT_INFO.txt (build information)"

print_status "APK file size: $(du -h build-outputs/AIStockTrading.apk | cut -f1)"
print_status "AAB file size: $(du -h build-outputs/AIStockTrading.aab | cut -f1)"

print_success "🎉 AI Stock Trading Mobile App is ready for deployment!"
print_status "You can now install the APK on Android devices or upload the AAB to Google Play Store."
