# 🚀 AI Stock Trading System - Quick Start Guide

## Your Project Configuration

- **GCP Project**: `stockbroker-28983`
- **GCP User**: `saji651970@gmail.com`
- **GitHub Repository**: `https://github.com/saji1970/aistockbroker`

## 🎯 Quick Setup (5 Minutes)

### Step 1: Run Setup Script

**Windows (PowerShell):**
```powershell
.\deployment\scripts\setup-project.ps1
```

**Linux/macOS (Bash):**
```bash
chmod +x deployment/scripts/setup-project.sh
./deployment/scripts/setup-project.sh
```

### Step 2: Add GitHub Secrets

1. Go to: `https://github.com/saji1970/aistockbroker/settings/secrets/actions`
2. Add these secrets:

| Secret Name | Value |
|-------------|-------|
| `GCP_SA_KEY` | Base64 encoded key from `ai-stock-trading-key.json` |
| `GCP_PROJECT_ID` | `stockbroker-28983` |
| `GCP_SA_EMAIL` | `ai-stock-trading-deployer@stockbroker-28983.iam.gserviceaccount.com` |

### Step 3: Deploy to Staging

**Option A: Automatic (Recommended)**
```bash
git push origin master
```

**Option B: Manual**
1. Go to [GitHub Actions](https://github.com/saji1970/aistockbroker/actions)
2. Select "AI Stock Trading System - CI/CD Pipeline"
3. Click "Run workflow"
4. Choose "staging" environment
5. Click "Run workflow"

### Step 4: Monitor Deployment

1. Go to [GitHub Actions](https://github.com/saji1970/aistockbroker/actions)
2. Watch the deployment progress
3. Check the logs for any issues

## 🎉 Success!

After successful deployment, your services will be available at:

- **Backend**: `https://ai-stock-backend-staging-xxxxx-uc.a.run.app`
- **Frontend**: `https://ai-stock-frontend-staging-xxxxx-uc.a.run.app`
- **Trading Bot**: `https://ai-stock-trading-bot-staging-xxxxx-uc.a.run.app`

## 🔧 Production Deployment

When ready for production:

1. Go to [GitHub Actions](https://github.com/saji1970/aistockbroker/actions)
2. Select "Production Deployment"
3. Click "Run workflow"
4. Type "DEPLOY TO PRODUCTION" to confirm
5. Click "Run workflow"

## 📊 Monitor Your Deployment

- **GCP Console**: [stockbroker-28983](https://console.cloud.google.com/home/dashboard?project=stockbroker-28983)
- **Cloud Run**: [Services](https://console.cloud.google.com/run?project=stockbroker-28983)
- **GitHub Actions**: [Workflows](https://github.com/saji1970/aistockbroker/actions)

## 🆘 Need Help?

- **Setup Issues**: Check [PROJECT_SETUP_GUIDE.md](deployment/PROJECT_SETUP_GUIDE.md)
- **Deployment Issues**: Check [DEPLOYMENT_GUIDE.md](deployment/DEPLOYMENT_GUIDE.md)
- **GitHub Issues**: [Create an issue](https://github.com/saji1970/aistockbroker/issues)

## 🎯 What's Next?

1. **Test the Application**: Visit your frontend URL
2. **Configure API Keys**: Add your trading API keys
3. **Set Up Monitoring**: Configure alerts and dashboards
4. **Deploy to Production**: When ready for live trading

Your AI Stock Trading System is ready to revolutionize trading! 🚀📈
