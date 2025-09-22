# AI Stock Trading Mobile - Deployment Guide

This guide provides step-by-step instructions for building and deploying the AI Stock Trading Mobile app for both Android and iOS platforms.

## 📋 Prerequisites

### For Android Development
- **Java Development Kit (JDK) 17** - Required for Android Gradle Plugin
- **Android Studio** - Latest version recommended
- **Android SDK** - API level 23+ (Android 6.0)
- **Android NDK** - For native code compilation

### For iOS Development
- **macOS** - Required for iOS development
- **Xcode 14+** - Latest version recommended
- **CocoaPods** - For dependency management
- **Apple Developer Account** - For App Store distribution

### General Requirements
- **Node.js 18+** - JavaScript runtime
- **npm or yarn** - Package manager
- **React Native CLI** - For React Native development

## 🚀 Quick Setup

### 1. Environment Setup

```bash
# Clone the repository (if not already done)
cd AIStockTradingMobile

# Install Node.js dependencies
npm install

# Install iOS dependencies (macOS only)
cd ios && pod install && cd ..
```

### 2. Environment Variables

Create a `.env` file in the root directory:

```env
API_BASE_URL=https://ai-stock-trading-1024040140027.us-central1.run.app
GOOGLE_API_KEY=your_google_api_key_here
```

## 📱 Android Deployment

### Step 1: Install Java 17

#### On macOS:
```bash
# Using Homebrew
brew install openjdk@17

# Set JAVA_HOME
export JAVA_HOME=/opt/homebrew/opt/openjdk@17
export PATH=$JAVA_HOME/bin:$PATH
```

#### On Windows:
1. Download OpenJDK 17 from https://adoptium.net/
2. Install and set JAVA_HOME environment variable

#### On Linux:
```bash
sudo apt update
sudo apt install openjdk-17-jdk
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
```

### Step 2: Configure Android SDK

1. Open Android Studio
2. Go to SDK Manager
3. Install:
   - Android SDK Platform 34 (Android 14)
   - Android SDK Build-Tools 34.0.0
   - Android NDK
   - Android SDK Command-line Tools

### Step 3: Set Environment Variables

Add to your shell profile (`.bashrc`, `.zshrc`, etc.):

```bash
export ANDROID_HOME=$HOME/Library/Android/sdk
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/tools/bin
export PATH=$PATH:$ANDROID_HOME/platform-tools
```

### Step 4: Build Android App

```bash
# Clean previous builds
cd android && ./gradlew clean && cd ..

# Build debug APK
npm run build:android

# Build release APK
cd android && ./gradlew assembleRelease && cd ..

# Build release AAB (for Google Play Store)
cd android && ./gradlew bundleRelease && cd ..
```

### Step 5: Sign the Release Build

1. Generate a keystore:
```bash
keytool -genkey -v -keystore android/app/release.keystore -alias aistocktrading -keyalg RSA -keysize 2048 -validity 10000
```

2. Add to `android/gradle.properties`:
```properties
MYAPP_RELEASE_STORE_FILE=release.keystore
MYAPP_RELEASE_KEY_ALIAS=aistocktrading
MYAPP_RELEASE_STORE_PASSWORD=your_keystore_password
MYAPP_RELEASE_KEY_PASSWORD=your_key_password
```

3. Update `android/app/build.gradle`:
```gradle
android {
    ...
    signingConfigs {
        release {
            storeFile file(MYAPP_RELEASE_STORE_FILE)
            storePassword MYAPP_RELEASE_STORE_PASSWORD
            keyAlias MYAPP_RELEASE_KEY_ALIAS
            keyPassword MYAPP_RELEASE_KEY_PASSWORD
        }
    }
    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}
```

### Step 6: Generate Final APK/AAB

```bash
# Signed release APK
cd android && ./gradlew assembleRelease && cd ..

# Signed release AAB
cd android && ./gradlew bundleRelease && cd ..
```

## 🍎 iOS Deployment

### Step 1: Install Xcode

1. Download Xcode from the Mac App Store
2. Install Command Line Tools:
```bash
xcode-select --install
```

### Step 2: Install CocoaPods

```bash
sudo gem install cocoapods
```

### Step 3: Configure iOS Project

1. Open `ios/AIStockTradingMobile.xcworkspace` in Xcode
2. Select the project in the navigator
3. Go to "Signing & Capabilities"
4. Select your development team
5. Update Bundle Identifier if needed

### Step 4: Build iOS App

```bash
# Install dependencies
cd ios && pod install && cd ..

# Clean previous builds
cd ios && xcodebuild clean -workspace AIStockTradingMobile.xcworkspace -scheme AIStockTradingMobile && cd ..

# Build for simulator
cd ios && xcodebuild -workspace AIStockTradingMobile.xcworkspace -scheme AIStockTradingMobile -configuration Debug -destination 'platform=iOS Simulator,name=iPhone 15,OS=latest' build && cd ..

# Build for device
cd ios && xcodebuild -workspace AIStockTradingMobile.xcworkspace -scheme AIStockTradingMobile -configuration Release -destination generic/platform=iOS -archivePath AIStockTradingMobile.xcarchive archive && cd ..
```

### Step 5: Create IPA for Distribution

1. Open Xcode
2. Go to Product > Archive
3. Select "Distribute App"
4. Choose distribution method:
   - App Store Connect (for App Store)
   - Ad Hoc (for specific devices)
   - Enterprise (for enterprise distribution)

## 📦 Automated Build Scripts

### Android Build Script

```bash
# Make script executable
chmod +x deploy-android.sh

# Run Android build
./deploy-android.sh
```

### iOS Build Script

```bash
# Make script executable
chmod +x deploy-ios.sh

# Run iOS build
./deploy-ios.sh
```

## 🚀 Distribution

### Android Distribution

#### Google Play Store:
1. Create a Google Play Console account
2. Upload the AAB file (`app-release.aab`)
3. Fill in app details, screenshots, and description
4. Submit for review

#### Direct Distribution:
1. Share the APK file (`app-release.apk`)
2. Users need to enable "Install from Unknown Sources"
3. Install directly on Android devices

### iOS Distribution

#### App Store:
1. Create an App Store Connect account
2. Upload the IPA through Xcode Organizer
3. Fill in app details, screenshots, and description
4. Submit for review

#### TestFlight:
1. Upload the IPA through Xcode Organizer
2. Add testers in App Store Connect
3. Distribute through TestFlight

#### Ad Hoc Distribution:
1. Register device UDIDs in Apple Developer Portal
2. Create Ad Hoc provisioning profile
3. Build and distribute IPA file

## 🔧 Troubleshooting

### Common Android Issues

1. **Java version error**:
   ```bash
   java -version  # Should show Java 17
   echo $JAVA_HOME  # Should point to Java 17
   ```

2. **SDK not found**:
   ```bash
   echo $ANDROID_HOME  # Should point to Android SDK
   ```

3. **Build fails**:
   ```bash
   cd android && ./gradlew clean && cd ..
   npm run android
   ```

### Common iOS Issues

1. **CocoaPods not found**:
   ```bash
   sudo gem install cocoapods
   cd ios && pod install && cd ..
   ```

2. **Signing issues**:
   - Check your Apple Developer account
   - Verify provisioning profiles
   - Update certificates if expired

3. **Build fails**:
   ```bash
   cd ios && xcodebuild clean && cd ..
   npm run ios
   ```

### General Issues

1. **Metro bundler issues**:
   ```bash
   npm start -- --reset-cache
   ```

2. **Dependencies issues**:
   ```bash
   rm -rf node_modules
   npm install
   ```

3. **iOS simulator issues**:
   ```bash
   xcrun simctl erase all
   ```

## 📱 Testing

### Android Testing

```bash
# Run on connected device
npm run android

# Run on emulator
# Start Android emulator first, then:
npm run android
```

### iOS Testing

```bash
# Run on simulator
npm run ios

# Run on connected device
# Open Xcode and select your device, then:
npm run ios
```

## 🔍 Debugging

### React Native Debugging

1. Enable Developer Menu (shake device or Cmd+D on simulator)
2. Enable Remote Debugging
3. Use React Native Debugger or Chrome DevTools

### Native Debugging

#### Android:
1. Use Android Studio's debugger
2. Check Logcat for native logs
3. Use Android Profiler for performance

#### iOS:
1. Use Xcode's debugger
2. Check Console for native logs
3. Use Instruments for performance

## 📊 Performance Optimization

### React Native

1. Enable Hermes engine
2. Use React Native Flipper for debugging
3. Optimize images and assets
4. Implement proper error boundaries

### Native

1. Optimize bundle size
2. Use ProGuard for Android
3. Enable code splitting
4. Optimize startup time

## 🔐 Security

### Android Security

1. Enable ProGuard/R8 code obfuscation
2. Use secure storage for sensitive data
3. Implement certificate pinning
4. Validate all inputs

### iOS Security

1. Enable App Transport Security
2. Use Keychain for sensitive data
3. Implement certificate pinning
4. Validate all inputs

## 📈 Monitoring

### Crash Reporting

1. Integrate Firebase Crashlytics
2. Set up error boundaries
3. Monitor app performance
4. Track user analytics

### Analytics

1. Integrate Firebase Analytics
2. Track user engagement
3. Monitor app performance
4. Analyze user behavior

---

**Note**: This deployment guide assumes you have the necessary developer accounts and certificates. For production deployment, ensure you have valid Apple Developer and Google Play Console accounts. 