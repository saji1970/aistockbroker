#!/usr/bin/env python3
"""
Setup script for the Gemini Pro Stock Predictor.
This script helps users install dependencies and configure the system.
"""

import os
import sys
import subprocess
import platform

def print_banner():
    """Print the application banner."""
    print("🤖 Gemini Pro Stock Predictor - Setup")
    print("=" * 40)
    print("Setting up your AI-powered stock prediction system...\n")

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required.")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing Dependencies...")
    print("-" * 30)
    
    try:
        # Check if pip is available
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ pip is not available. Please install pip first.")
        return False
    
    try:
        # Install requirements
        print("Installing packages from requirements.txt...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            print("❌ Failed to install dependencies")
            print("Error output:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def create_env_file():
    """Create .env file template."""
    env_file = ".env"
    
    if os.path.exists(env_file):
        print(f"⚠️ {env_file} already exists. Skipping creation.")
        return True
    
    print("\n🔧 Creating Environment File...")
    print("-" * 30)
    
    try:
        with open(env_file, 'w') as f:
            f.write("# Gemini Pro Stock Predictor Configuration\n")
            f.write("# Replace 'your_gemini_api_key_here' with your actual API key\n\n")
            f.write("# Required: Google Gemini Pro API Key\n")
            f.write("GOOGLE_API_KEY=your_gemini_api_key_here\n\n")
            f.write("# Optional: Alpha Vantage API Key for additional data\n")
            f.write("# ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here\n")
        
        print(f"✅ Created {env_file} template")
        print("💡 Please edit this file and add your Gemini Pro API key")
        return True
        
    except Exception as e:
        print(f"❌ Error creating {env_file}: {e}")
        return False

def get_gemini_api_key():
    """Guide user to get Gemini API key."""
    print("\n🔑 Getting Gemini Pro API Key...")
    print("-" * 30)
    print("To use the AI prediction features, you need a Gemini Pro API key:")
    print()
    print("1. Visit: https://makersuite.google.com/app/apikey")
    print("2. Sign in with your Google account")
    print("3. Click 'Create API Key'")
    print("4. Copy the generated key")
    print("5. Edit the .env file and replace 'your_gemini_api_key_here' with your key")
    print()
    print("💡 The API key is free and includes generous usage limits")

def run_tests():
    """Run installation tests."""
    print("\n🧪 Running Installation Tests...")
    print("-" * 30)
    
    try:
        result = subprocess.run([sys.executable, "test_installation.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Installation tests completed")
            print("📊 Test Results:")
            print(result.stdout)
        else:
            print("⚠️ Some tests failed:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")

def print_next_steps():
    """Print next steps for the user."""
    print("\n🚀 Next Steps:")
    print("-" * 30)
    print("1. Get your Gemini Pro API key (see instructions above)")
    print("2. Edit the .env file with your API key")
    print("3. Run the application:")
    print("   streamlit run app.py")
    print()
    print("4. Open your browser to: http://localhost:8501")
    print()
    print("📚 For more information, see README.md")
    print("💡 For help, run: python example_usage.py")

def main():
    """Main setup function."""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)
    
    # Create environment file
    if not create_env_file():
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)
    
    # Guide user to get API key
    get_gemini_api_key()
    
    # Run tests
    run_tests()
    
    # Print next steps
    print_next_steps()
    
    print("\n🎉 Setup completed successfully!")
    print("Happy trading! 📈")

if __name__ == "__main__":
    main() 