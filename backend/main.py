#!/usr/bin/env python3
"""
Main entry point for App Engine deployment
"""

import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app from api_server
from api_server import app

if __name__ == '__main__':
    # This is used when running locally
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
