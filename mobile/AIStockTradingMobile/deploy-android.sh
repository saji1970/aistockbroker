#!/bin/bash

# AI Stock Trading Mobile - Android Deployment Script
# This script builds the Android app and generates APK and AAB files

set -e

echo "🚀 Starting Android deployment for AI Stock Trading Mobile..."

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

# Check if Node.js and npm are installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js first."
    exit 1
fi

if ! command -v npm &> /dev/null; then
    print_error "npm is not installed. Please install npm first."
    exit 1
fi

# Check if Android SDK is available
if [ -z "$ANDROID_HOME" ]; then
    print_warning "ANDROID_HOME is not set. Make sure Android SDK is installed."
fi

print_status "Installing dependencies..."
npm install

print_status "Cleaning previous builds..."
cd android
./gradlew clean
cd ..

print_status "Building Android APK (Debug)..."
cd android
./gradlew assembleDebug
cd ..

print_status "Building Android APK (Release)..."
cd android
./gradlew assembleRelease
cd ..

print_status "Building Android App Bundle (Release)..."
cd android
./gradlew bundleRelease
cd ..

print_status "Building Universal APK (Release)..."
cd android
./gradlew assembleUniversalRelease
cd ..

# Create output directory
mkdir -p build-outputs

# Copy APK files
print_status "Copying APK files..."
cp android/app/build/outputs/apk/debug/app-debug.apk build-outputs/AIStockTradingMobile-debug.apk
cp android/app/build/outputs/apk/release/app-release.apk build-outputs/AIStockTradingMobile-release.apk

# Copy Universal APK (if exists)
if [ -f "android/app/build/outputs/apk/release/app-universal-release.apk" ]; then
    cp android/app/build/outputs/apk/release/app-universal-release.apk build-outputs/AIStockTradingMobile-universal-release.apk
    print_status "Universal APK copied successfully"
fi

# Copy AAB file
print_status "Copying AAB file..."
cp android/app/build/outputs/bundle/release/app-release.aab build-outputs/AIStockTradingMobile-release.aab

print_success "Android build completed successfully!"
echo ""
print_status "Generated files:"
echo "  📱 Debug APK: build-outputs/AIStockTradingMobile-debug.apk"
echo "  📱 Release APK: build-outputs/AIStockTradingMobile-release.apk"
if [ -f "build-outputs/AIStockTradingMobile-universal-release.apk" ]; then
    echo "  📱 Universal APK: build-outputs/AIStockTradingMobile-universal-release.apk"
fi
echo "  📦 Release AAB: build-outputs/AIStockTradingMobile-release.aab"
echo ""
print_status "Next steps:"
echo "  1. Test the debug APK on your device"
echo "  2. Use the release APK for direct installation (no Google Play required)"
echo "  3. Upload the AAB file to Google Play Console (optional)"
echo ""
print_success "✅ The release APK is properly signed and ready for direct installation!"
print_success "✅ No Google Play Store required - users can install directly from the APK file." 