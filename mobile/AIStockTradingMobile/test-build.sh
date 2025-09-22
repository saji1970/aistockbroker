#!/bin/bash

# AI Stock Trading Mobile - Test Build Script
# This script tests the build environment and provides helpful information

set -e

echo "🧪 Testing AI Stock Trading Mobile build environment..."

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
    print_error "Please run this script from the AIStockTradingMobile directory"
    exit 1
fi

print_status "Checking environment..."

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_success "Node.js: $NODE_VERSION"
else
    print_error "Node.js is not installed"
    exit 1
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    print_success "npm: $NPM_VERSION"
else
    print_error "npm is not installed"
    exit 1
fi

# Check Java
if command -v java &> /dev/null; then
    JAVA_VERSION=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2)
    print_success "Java: $JAVA_VERSION"
    
    # Check if Java 17 is needed
    if [[ "$JAVA_VERSION" == 17* ]]; then
        print_success "Java version is compatible with Android builds"
    else
        print_warning "Android builds require Java 17, but you have $JAVA_VERSION"
        print_warning "For Android builds, please install Java 17:"
        echo "  brew install openjdk@17"
        echo "  export JAVA_HOME=/opt/homebrew/opt/openjdk@17"
    fi
else
    print_error "Java is not installed"
    exit 1
fi

# Check React Native CLI
if command -v npx &> /dev/null; then
    print_success "npx is available"
else
    print_error "npx is not available"
    exit 1
fi

# Check if dependencies are installed
if [ -d "node_modules" ]; then
    print_success "Node.js dependencies are installed"
else
    print_warning "Node.js dependencies are not installed"
    print_status "Installing dependencies..."
    npm install
fi

# Check Android environment
if [ -d "android" ]; then
    print_success "Android project structure exists"
    
    if [ -z "$ANDROID_HOME" ]; then
        print_warning "ANDROID_HOME is not set"
        print_warning "Please set ANDROID_HOME to your Android SDK path"
    else
        print_success "ANDROID_HOME is set to: $ANDROID_HOME"
    fi
else
    print_error "Android project structure not found"
    exit 1
fi

# Check iOS environment (macOS only)
if [[ "$OSTYPE" == "darwin"* ]]; then
    if [ -d "ios" ]; then
        print_success "iOS project structure exists"
        
        if command -v xcodebuild &> /dev/null; then
            XCODE_VERSION=$(xcodebuild -version | head -n 1)
            print_success "Xcode: $XCODE_VERSION"
        else
            print_warning "Xcode is not installed"
        fi
        
        if command -v pod &> /dev/null; then
            POD_VERSION=$(pod --version)
            print_success "CocoaPods: $POD_VERSION"
        else
            print_warning "CocoaPods is not installed"
            print_warning "Please install CocoaPods: sudo gem install cocoapods"
        fi
    else
        print_error "iOS project structure not found"
    fi
else
    print_warning "iOS builds can only be done on macOS"
fi

print_status "Testing Metro bundler..."
if npx react-native start --help &> /dev/null; then
    print_success "Metro bundler is working"
else
    print_error "Metro bundler is not working"
fi

print_status "Testing TypeScript compilation..."
if npx tsc --noEmit; then
    print_success "TypeScript compilation passed"
else
    print_warning "TypeScript compilation has warnings"
fi

print_status "Running linting..."
if npm run lint; then
    print_success "Linting passed"
else
    print_warning "Linting has warnings"
fi

echo ""
print_success "Environment test completed!"
echo ""
print_status "Next steps:"
echo ""

if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "📱 For iOS development:"
    echo "  1. Install Xcode from the App Store"
    echo "  2. Install CocoaPods: sudo gem install cocoapods"
    echo "  3. Run: cd ios && pod install && cd .."
    echo "  4. Run: npm run ios"
    echo ""
fi

echo "🤖 For Android development:"
if [[ "$JAVA_VERSION" == 17* ]]; then
    echo "  1. Install Android Studio"
    echo "  2. Set up Android SDK"
    echo "  3. Set ANDROID_HOME environment variable"
    echo "  4. Run: npm run android"
else
    echo "  1. Install Java 17: brew install openjdk@17"
    echo "  2. Set JAVA_HOME: export JAVA_HOME=/opt/homebrew/opt/openjdk@17"
    echo "  3. Install Android Studio"
    echo "  4. Set up Android SDK"
    echo "  5. Set ANDROID_HOME environment variable"
    echo "  6. Run: npm run android"
fi

echo ""
print_status "For production builds, see DEPLOYMENT_GUIDE.md" 