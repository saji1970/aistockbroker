#!/bin/bash

# AI Stock Trading Mobile - Simplified Android Build Script
# This script builds a working APK with all enhanced functionality

set -e

echo "🚀 Starting simplified Android build for AI Stock Trading Mobile..."

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

print_status "Installing core dependencies..."
npm install

print_status "Cleaning previous builds..."
cd android
./gradlew clean
cd ..

print_status "Building Android APK (Debug) with simplified configuration..."
cd android

# Force use of compatible versions
export ANDROID_GRADLE_OPTS="-Dandroid.useAndroidX=true -Dandroid.enableJetifier=true"

# Build debug APK
./gradlew assembleDebug --no-daemon --stacktrace

cd ..

# Create output directory
mkdir -p build-outputs

# Copy APK file
print_status "Copying APK file..."
cp android/app/build/outputs/apk/debug/app-debug.apk build-outputs/AIStockTradingMobile-enhanced.apk

print_success "Simplified Android build completed successfully!"
echo ""
print_status "Generated files:"
echo "  📱 Enhanced APK: build-outputs/AIStockTradingMobile-enhanced.apk"
echo ""
print_status "Features included:"
echo "  ✅ Enhanced AI Assistant with multi-market support"
echo "  ✅ Improved stock symbol detection (US, UK, India)"
echo "  ✅ Smart market detection and validation"
echo "  ✅ Better error handling and user guidance"
echo "  ✅ All core functionality from web app"
echo ""
print_success "✅ The APK is ready for direct installation!"
print_success "✅ No Google Play Store required - users can install directly from the APK file."
echo ""
print_status "Installation instructions:"
echo "  1. Enable 'Install from Unknown Sources' on your Android device"
echo "  2. Transfer the APK file to your device"
echo "  3. Tap the APK file to install"
echo "  4. Enjoy the enhanced AI Stock Trading app!"
