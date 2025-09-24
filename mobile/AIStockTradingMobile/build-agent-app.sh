#!/bin/bash

# AI Stock Trading Mobile App - Agent Build Script
# This script builds the mobile app with agent functionality

set -e

echo "🚀 Building AI Stock Trading Mobile App with Agent Functionality"
echo "================================================================"

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Please run this script from the mobile app directory"
    exit 1
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
./gradlew clean || true
rm -rf android/app/build || true
rm -rf android/build || true

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Install iOS dependencies if on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 Installing iOS dependencies..."
    cd ios && pod install && cd ..
fi

# Build Android APK
echo "🤖 Building Android APK..."
cd android
./gradlew assembleRelease

# Check if build was successful
if [ -f "app/build/outputs/apk/release/app-release.apk" ]; then
    echo "✅ Android APK built successfully!"
    
    # Copy APK to public downloads
    mkdir -p ../public/downloads
    cp app/build/outputs/apk/release/app-release.apk ../public/downloads/AIStockTradingAgent.apk
    
    echo "📱 APK copied to: public/downloads/AIStockTradingAgent.apk"
    
    # Get APK info
    APK_SIZE=$(du -h app/build/outputs/apk/release/app-release.apk | cut -f1)
    echo "📊 APK Size: $APK_SIZE"
    
    # Create deployment info
    cat > ../public/downloads/AGENT_APP_INFO.txt << EOF
AI Stock Trading Agent Mobile App
=================================

Build Date: $(date)
APK Size: $APK_SIZE
Version: 1.0.0

Features:
- Agent Login & Authentication
- Customer Management
- Trade Suggestions Review
- AI-Powered Recommendations
- Portfolio Overview
- Learning Insights
- Real-time Dashboard

Installation:
1. Download the APK file
2. Enable "Install from unknown sources" on your Android device
3. Install the APK
4. Launch the app and login with your agent credentials

Backend Requirements:
- Backend API server running on http://localhost:8080
- Agent system enabled
- Database initialized

For support, contact: support@aistockbroker.com
EOF
    
    echo "📄 Deployment info created: public/downloads/AGENT_APP_INFO.txt"
    
else
    echo "❌ Android APK build failed!"
    exit 1
fi

cd ..

# Build Android Bundle (AAB) for Google Play Store
echo "📦 Building Android Bundle (AAB)..."
cd android
./gradlew bundleRelease

if [ -f "app/build/outputs/bundle/release/app-release.aab" ]; then
    echo "✅ Android Bundle built successfully!"
    
    # Copy AAB to public downloads
    cp app/build/outputs/bundle/release/app-release.aab ../public/downloads/AIStockTradingAgent.aab
    
    echo "📱 AAB copied to: public/downloads/AIStockTradingAgent.aab"
else
    echo "❌ Android Bundle build failed!"
fi

cd ..

# Create build summary
cat > BUILD_SUMMARY.md << EOF
# AI Stock Trading Agent Mobile App - Build Summary

## Build Information
- **Build Date**: $(date)
- **Version**: 1.0.0
- **Platform**: Android
- **Features**: Agent Management, Customer Portfolio, AI Suggestions

## Generated Files
- **APK**: public/downloads/AIStockTradingAgent.apk
- **AAB**: public/downloads/AIStockTradingAgent.aab
- **Info**: public/downloads/AGENT_APP_INFO.txt

## Features Included
✅ Agent Authentication
✅ Customer Management
✅ Trade Suggestions Review
✅ AI-Powered Recommendations
✅ Portfolio Overview
✅ Learning Insights
✅ Real-time Dashboard
✅ Offline Support
✅ Push Notifications (Ready)

## Installation Instructions
1. Download the APK file to your Android device
2. Enable "Install from unknown sources" in device settings
3. Install the APK
4. Launch the app and login with agent credentials

## Backend Requirements
- Backend API server running on http://localhost:8080
- Agent system enabled
- Database initialized
- CORS configured for mobile app

## Testing
- Unit tests: npm test
- Integration tests: npm run test:integration
- E2E tests: npm run test:e2e

## Deployment
- Local testing: Use APK file
- Production: Use AAB file for Google Play Store
- Enterprise: Use APK file for internal distribution

## Support
- Documentation: README.md
- Issues: GitHub Issues
- Contact: support@aistockbroker.com
EOF

echo "📋 Build summary created: BUILD_SUMMARY.md"

echo ""
echo "🎉 Build completed successfully!"
echo "=================================="
echo "📱 APK: public/downloads/AIStockTradingAgent.apk"
echo "📦 AAB: public/downloads/AIStockTradingAgent.aab"
echo "📄 Info: public/downloads/AGENT_APP_INFO.txt"
echo "📋 Summary: BUILD_SUMMARY.md"
echo ""
echo "🚀 Ready for deployment!"
