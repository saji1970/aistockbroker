#!/bin/bash
# Deploy AI Stock Trading Platform to Railway

set -e  # Exit on error

echo "🚀 Deploying AI Stock Trading Platform to Railway..."
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found."
    echo "📦 Install it with: npm i -g @railway/cli"
    echo "📖 Or visit: https://docs.railway.com/develop/cli"
    exit 1
fi

echo "✅ Railway CLI found"
echo ""

# Check if user is logged in
if ! railway whoami &> /dev/null; then
    echo "🔐 Not logged in to Railway. Logging in..."
    railway login
else
    echo "✅ Already logged in to Railway"
fi

echo ""

# Link to Railway project (or create new one)
echo "🔗 Linking to Railway project..."
if [ ! -f ".railway" ] && [ ! -d ".railway" ]; then
    echo "Creating new Railway project or linking to existing one..."
    railway link
else
    echo "✅ Already linked to Railway project"
fi

echo ""

# Display current environment variables (optional)
echo "📋 Current environment variables:"
railway variables
echo ""

# Prompt user to set required variables if not set
echo "⚙️  Checking required environment variables..."
REQUIRED_VARS=("AI_PROVIDER" "HF_API_TOKEN" "DATABASE_URL")

for var in "${REQUIRED_VARS[@]}"; do
    if railway variables get "$var" &> /dev/null; then
        echo "✅ $var is set"
    else
        echo "⚠️  $var is not set"
        if [ "$var" == "DATABASE_URL" ]; then
            echo "   Add PostgreSQL database: Railway Dashboard → New → Database → PostgreSQL"
        elif [ "$var" == "HF_API_TOKEN" ]; then
            echo "   Get token from: https://huggingface.co/settings/tokens"
            read -p "   Enter HF_API_TOKEN: " token
            railway variables set HF_API_TOKEN="$token"
        elif [ "$var" == "AI_PROVIDER" ]; then
            railway variables set AI_PROVIDER=huggingface
            echo "   Set AI_PROVIDER=huggingface"
        fi
    fi
done

echo ""

# Deploy to Railway
echo "🚀 Deploying to Railway..."
railway up

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Check deployment status:"
echo "   Railway Dashboard: https://railway.app"
echo "   Or run: railway logs"
echo ""
echo "🌐 Your app will be available at:"
railway status | grep "URL" || echo "   Check Railway dashboard for deployment URL"
echo ""
echo "🧪 Test the deployment:"
echo "   Health check: curl https://your-app.up.railway.app/api/health"
echo "   AI endpoint: curl -X POST https://your-app.up.railway.app/api/ai/gemini-query \\"
echo "                  -H 'Content-Type: application/json' \\"
echo "                  -d '{\"query\": \"What is AAPL price?\"}'"
echo ""
echo "📖 Full deployment guide: RAILWAY_DEPLOYMENT.md"
