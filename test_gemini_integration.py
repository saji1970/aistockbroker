#!/usr/bin/env python3
"""
Test script for Gemini integration in AI Stock Trading Platform
"""

import os
import sys
import requests
import json
from datetime import datetime

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_gemini_api_endpoint():
    """Test the Gemini API endpoint"""
    print("🧪 Testing Gemini API Integration...")
    
    # Test data
    test_queries = [
        "What's the current price of AAPL?",
        "Predict TSLA direction for tomorrow",
        "Analyze the tech sector performance",
        "Give me a day trading strategy for MSFT",
        "What are the market trends today?"
    ]
    
    base_url = "http://localhost:5000"  # Adjust if your server runs on different port
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        
        try:
            response = requests.post(
                f"{base_url}/api/ai/gemini-query",
                headers={'Content-Type': 'application/json'},
                json={
                    'query': query,
                    'temperature': 0.3,
                    'maxTokens': 2048,
                    'market': 'US'
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Status: Success")
                print(f"📊 Model Used: {data.get('model_used', 'Unknown')}")
                print(f"🎯 Confidence: {data.get('confidence', 'N/A')}")
                print(f"📝 Response Preview: {data.get('response', 'No response')[:200]}...")
            else:
                print(f"❌ Status: Error {response.status_code}")
                print(f"📝 Error: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Make sure the backend server is running on port 5000")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def test_gemini_predictor_direct():
    """Test Gemini predictor directly"""
    print("\n🔬 Testing Gemini Predictor Direct Integration...")
    
    try:
        from backend.gemini_predictor import GeminiStockPredictor
        from backend.config import Config
        
        print(f"📋 Config Status:")
        print(f"   - Google API Key: {'✅ Set' if Config.GOOGLE_API_KEY and Config.GOOGLE_API_KEY != 'your_google_api_key_here' else '❌ Not Set'}")
        print(f"   - Gemini Model: {Config.GEMINI_MODEL}")
        print(f"   - Temperature: {Config.TEMPERATURE}")
        print(f"   - Max Tokens: {Config.MAX_TOKENS}")
        
        # Initialize predictor
        predictor = GeminiStockPredictor()
        
        if predictor.model:
            print("✅ Gemini predictor initialized successfully")
            
            # Test a simple query
            test_query = "What's the current price of AAPL?"
            print(f"\n📝 Testing query: {test_query}")
            
            result = predictor.process_natural_language_query(test_query)
            print(f"✅ Query processed successfully")
            print(f"📊 Query Type: {result.get('query_type', 'Unknown')}")
            print(f"🎯 Confidence: {result.get('confidence', 'N/A')}")
            print(f"📝 Response Preview: {result.get('response', 'No response')[:200]}...")
            
        else:
            print("❌ Gemini predictor not initialized - check API key configuration")
            
    except ImportError as e:
        print(f"❌ Import Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

def check_environment_setup():
    """Check environment setup"""
    print("🔧 Checking Environment Setup...")
    
    # Check for .env file
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        print("✅ .env file found")
        
        # Read .env file
        with open(env_file, 'r') as f:
            content = f.read()
            if 'GOOGLE_API_KEY' in content:
                print("✅ GOOGLE_API_KEY found in .env file")
            else:
                print("❌ GOOGLE_API_KEY not found in .env file")
    else:
        print("❌ .env file not found")
        print("💡 Create a .env file with your GOOGLE_API_KEY")
    
    # Check environment variables
    google_key = os.getenv('GOOGLE_API_KEY')
    if google_key and google_key != 'your_google_api_key_here':
        print("✅ GOOGLE_API_KEY environment variable is set")
    else:
        print("❌ GOOGLE_API_KEY environment variable not set or using default value")

def main():
    """Main test function"""
    print("🚀 Gemini Integration Test Suite")
    print("=" * 50)
    
    # Check environment setup first
    check_environment_setup()
    
    # Test direct predictor integration
    test_gemini_predictor_direct()
    
    # Test API endpoint
    print("\n" + "=" * 50)
    print("🌐 Testing API Endpoint Integration")
    test_gemini_api_endpoint()
    
    print("\n" + "=" * 50)
    print("✅ Test Suite Complete")
    print("\n💡 Tips:")
    print("   - Make sure your GOOGLE_API_KEY is properly configured")
    print("   - Start the backend server with: python backend/api_server.py")
    print("   - The AI Assistant will use Gemini when 'Gemini 1.5 Pro (Stock Expert)' is selected")

if __name__ == "__main__":
    main()
