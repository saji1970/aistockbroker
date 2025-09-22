# 🚀 AI Trading Bot - GCP Deployment Guide

This guide will help you deploy the AI Trading Bot to Google Cloud Platform (GCP).

## 📋 Prerequisites

### 1. GCP Setup
- Google Cloud Project with billing enabled
- `gcloud` CLI installed and configured
- Docker installed (for local testing)

### 2. Required APIs
- Cloud Run API
- Cloud Build API
- Container Registry API

## 🎯 Deployment Options

### Option 1: Deploy Trading Bot as Separate Service (Recommended)

This deploys the trading bot as a standalone Cloud Run service that can be accessed independently.

#### Step 1: Deploy the Trading Bot
```bash
# Make the deployment script executable
chmod +x deploy-trading-bot.sh

# Deploy to GCP
./deploy-trading-bot.sh
```

#### Step 2: Update Frontend Configuration
After deployment, update your frontend to use the new trading bot API:

```javascript
// In src/services/tradingBotAPI.js
const API_BASE_URL = 'https://ai-trading-bot-ccrwk2lv6q-uc.a.run.app';
```

### Option 2: Integrate with Existing Backend

This integrates the trading bot functionality into your existing backend service.

#### Step 1: Update Existing Backend
Add the trading bot routes to your existing `api_server.py`:

```python
# Add to api_server.py
from trading_dashboard import app as trading_app

# Mount trading bot routes
app.mount("/trading-bot", trading_app)
```

#### Step 2: Update Dockerfile
Update your existing Dockerfile to include trading bot dependencies:

```dockerfile
# Add to existing Dockerfile
COPY trading_bot_requirements.txt .
RUN pip install -r trading_bot_requirements.txt

COPY shadow_trading_bot.py .
COPY advanced_trading_bot.py .
COPY trading_bot_config.json .
```

## 🔧 Configuration

### Environment Variables
The trading bot uses these environment variables:

```bash
# Production settings
FLASK_ENV=production
PYTHONPATH=/app
PORT=5000

# Optional: Custom configuration
TRADING_BOT_CONFIG_PATH=/app/trading_bot_config.json
```

### Trading Bot Configuration
Edit `trading_bot_config.json` to customize:

```json
{
  "bot_settings": {
    "initial_capital": 100000.0,
    "trading_interval": 300,
    "max_position_size": 0.1,
    "max_daily_loss": 0.05
  },
  "strategies": {
    "momentum": {
      "enabled": true,
      "parameters": {
        "lookback_period": 20,
        "momentum_threshold": 0.02
      }
    }
  }
}
```

## 🌐 API Endpoints

Once deployed, the trading bot will be available at:

### Base URL
```
https://ai-trading-bot-ccrwk2lv6q-uc.a.run.app
```

### Available Endpoints
- `GET /api/status` - Bot status and watchlist
- `POST /api/start` - Start trading bot
- `POST /api/stop` - Stop trading bot
- `GET /api/portfolio` - Current portfolio data
- `GET /api/orders` - Recent orders
- `GET /api/performance` - Performance metrics
- `GET /api/watchlist` - Current watchlist
- `POST /api/watchlist` - Add/remove symbols
- `GET /api/strategies` - Available strategies

## 🔗 Frontend Integration

### Update API Configuration
Update your frontend to use the deployed trading bot:

```javascript
// src/services/tradingBotAPI.js
const API_BASE_URL = process.env.REACT_APP_TRADING_BOT_URL || 
  'https://ai-trading-bot-ccrwk2lv6q-uc.a.run.app';
```

### Environment Variables
Add to your frontend environment:

```bash
# .env.production
REACT_APP_TRADING_BOT_URL=https://ai-trading-bot-ccrwk2lv6q-uc.a.run.app
```

## 🧪 Testing the Deployment

### 1. Health Check
```bash
curl https://ai-trading-bot-ccrwk2lv6q-uc.a.run.app/api/status
```

### 2. Start Trading Bot
```bash
curl -X POST https://ai-trading-bot-ccrwk2lv6q-uc.a.run.app/api/start \
  -H "Content-Type: application/json" \
  -d '{"initial_capital": 100000}'
```

### 3. Add to Watchlist
```bash
curl -X POST https://ai-trading-bot-ccrwk2lv6q-uc.a.run.app/api/watchlist \
  -H "Content-Type: application/json" \
  -d '{"action": "add", "symbol": "AAPL"}'
```

## 📊 Monitoring and Logs

### View Logs
```bash
# View recent logs
gcloud logs read --service=ai-trading-bot --limit=50

# Follow logs in real-time
gcloud logs tail --service=ai-trading-bot
```

### Monitor Performance
```bash
# Check service status
gcloud run services describe ai-trading-bot --region=us-central1

# View metrics
gcloud monitoring metrics list --filter="resource.type=cloud_run_revision"
```

## 🔒 Security Considerations

### 1. Authentication (Optional)
For production use, consider adding authentication:

```python
# Add to trading_dashboard.py
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    return username == 'admin' and password == 'your-secure-password'

# Protect endpoints
@app.route('/api/start', methods=['POST'])
@auth.login_required
def start_bot():
    # ... existing code
```

### 2. Rate Limiting
Add rate limiting to prevent abuse:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/start', methods=['POST'])
@limiter.limit("5 per minute")
def start_bot():
    # ... existing code
```

## 🚀 Deployment Commands

### Quick Deploy
```bash
# Deploy trading bot
./deploy-trading-bot.sh

# Update frontend (if needed)
npm run build
gcloud builds submit --config cloudbuild-static.yaml
```

### Manual Deploy
```bash
# Build image
docker build -t gcr.io/aimodelfoundry/ai-trading-bot -f Dockerfile.trading-bot .

# Push image
docker push gcr.io/aimodelfoundry/ai-trading-bot

# Deploy to Cloud Run
gcloud run deploy ai-trading-bot \
  --image gcr.io/aimodelfoundry/ai-trading-bot \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --port 5000 \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10
```

## 🔄 Updates and Maintenance

### Update Trading Bot
```bash
# Make changes to trading bot code
# Then redeploy
./deploy-trading-bot.sh
```

### Scale Service
```bash
# Scale up for high traffic
gcloud run services update ai-trading-bot \
  --region us-central1 \
  --max-instances 50 \
  --memory 2Gi \
  --cpu 2
```

### Rollback
```bash
# List revisions
gcloud run revisions list --service=ai-trading-bot --region=us-central1

# Rollback to previous revision
gcloud run services update-traffic ai-trading-bot \
  --region us-central1 \
  --to-revisions=ai-trading-bot-00001-abc=100
```

## 📈 Performance Optimization

### 1. Caching
Add Redis for caching:

```python
import redis
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@app.route('/api/portfolio')
@cache.cached(timeout=30)
def get_portfolio():
    # ... existing code
```

### 2. Database
For persistent storage, add a database:

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    total_value = db.Column(db.Float)
    # ... other fields
```

## 🎯 Next Steps

1. **Deploy the trading bot** using the provided script
2. **Update your frontend** to use the new API endpoints
3. **Test the functionality** with the provided test commands
4. **Configure your watchlist** and start trading
5. **Monitor performance** using GCP monitoring tools

## 🆘 Troubleshooting

### Common Issues

#### 1. Build Fails
```bash
# Check build logs
gcloud builds log [BUILD_ID]

# Common fixes:
# - Check Dockerfile syntax
# - Verify all files are copied
# - Check Python dependencies
```

#### 2. Service Won't Start
```bash
# Check service logs
gcloud logs read --service=ai-trading-bot --limit=100

# Common fixes:
# - Check port configuration
# - Verify environment variables
# - Check Python imports
```

#### 3. API Not Responding
```bash
# Test health endpoint
curl -v https://ai-trading-bot-ccrwk2lv6q-uc.a.run.app/api/status

# Check service status
gcloud run services describe ai-trading-bot --region=us-central1
```

## 📞 Support

For deployment issues:
1. Check the troubleshooting section
2. Review GCP logs and monitoring
3. Verify configuration files
4. Test locally first

---

**🚀 Ready to deploy! Run `./deploy-trading-bot.sh` to get started!**
