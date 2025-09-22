#!/bin/bash

# AI Stock Trading Mobile - iOS Deployment Script
# This script builds the iOS app and generates IPA files

set -e

echo "🚀 Starting iOS deployment for AI Stock Trading Mobile..."

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
if [ ! -f "package.json" ] || [ ! -d "ios" ]; then
    print_error "Please run this script from the AIStockTradingMobile directory"
    exit 1
fi

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "iOS builds can only be done on macOS"
    exit 1
fi

# Check if Xcode is installed
if ! command -v xcodebuild &> /dev/null; then
    print_error "Xcode is not installed. Please install Xcode from the App Store."
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

# Check if CocoaPods is installed
if ! command -v pod &> /dev/null; then
    print_error "CocoaPods is not installed. Please install CocoaPods first:"
    echo "  sudo gem install cocoapods"
    exit 1
fi

print_status "Installing dependencies..."
npm install

print_status "Installing iOS dependencies..."
cd ios
pod install
cd ..

print_status "Cleaning previous builds..."
cd ios
xcodebuild clean -workspace AIStockTradingMobile.xcworkspace -scheme AIStockTradingMobile
cd ..

print_status "Building iOS app for simulator..."
cd ios
xcodebuild -workspace AIStockTradingMobile.xcworkspace -scheme AIStockTradingMobile -configuration Debug -destination 'platform=iOS Simulator,name=iPhone 15,OS=latest' build
cd ..

print_status "Building iOS app for device..."
cd ios
xcodebuild -workspace AIStockTradingMobile.xcworkspace -scheme AIStockTradingMobile -configuration Release -destination generic/platform=iOS -archivePath AIStockTradingMobile.xcarchive archive
cd ..

# Create output directory
mkdir -p build-outputs

print_success "iOS build completed successfully!"
echo ""
print_status "Generated files:"
echo "  📱 iOS App: ios/build/Build/Products/Release-iphoneos/AIStockTradingMobile.app"
echo "  📦 iOS Archive: ios/AIStockTradingMobile.xcarchive"
echo ""
print_status "Next steps:"
echo "  1. Open Xcode and open ios/AIStockTradingMobile.xcworkspace"
echo "  2. Select your development team in project settings"
echo "  3. Archive the project for distribution"
echo "  4. Upload to App Store Connect or export for ad-hoc distribution"
echo ""
print_warning "Note: You need an Apple Developer account to distribute the app."
print_warning "For App Store distribution, use Xcode's Organizer to upload the archive."
print_warning "For TestFlight, archive the project and upload through Xcode." 