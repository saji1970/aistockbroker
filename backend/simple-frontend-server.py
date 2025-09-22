from flask import Flask, redirect, request
import os

app = Flask(__name__)

# Cloud Storage URL for the frontend
FRONTEND_URL = "https://storage.googleapis.com/ai-stock-trading-frontend-aimodelfoundry/index.html"

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Redirect all requests to the Cloud Storage hosted frontend"""
    if path.startswith('api/'):
        # API requests should go to the backend
        backend_url = "https://ai-stock-trading-backend-ccrwk2lv6q-uc.a.run.app"
        return redirect(f"{backend_url}/{path}")
    else:
        # All other requests go to the frontend
        return redirect(FRONTEND_URL)

@app.route('/health')
def health():
    """Health check endpoint"""
    return {"status": "healthy", "frontend_url": FRONTEND_URL}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
