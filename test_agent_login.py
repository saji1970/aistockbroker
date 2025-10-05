#!/usr/bin/env python3
"""
Test agent login functionality
"""

import requests
import json
import sys

def test_agent_login():
    """Test agent login with unified auth system"""
    try:
        # Test data
        login_data = {
            "email_or_username": "saji@aitrader.com",
            "password": "password123"
        }
        
        # Make request to unified auth endpoint
        response = requests.post(
            "http://localhost:5000/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Agent login successful!")
                print(f"User role: {data.get('user', {}).get('role')}")
                print(f"User ID: {data.get('user', {}).get('id')}")
                
                # Test agent endpoint access
                token = data.get('token')
                if token:
                    headers = {"Authorization": f"Bearer {token}"}
                    agent_response = requests.get(
                        "http://localhost:5000/api/agent/profile",
                        headers=headers
                    )
                    print(f"\nAgent profile endpoint status: {agent_response.status_code}")
                    print(f"Agent profile response: {agent_response.text}")
            else:
                print("❌ Login failed:", data.get('message'))
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the backend server is running on port 5000.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_agent_login()
