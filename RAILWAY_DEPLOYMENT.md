# Railway Deployment Guide

Complete guide for deploying the AI Stock Trading Platform to Railway with HuggingFace AI provider.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Your code pushed to GitHub
3. **HuggingFace Account**: Sign up at [huggingface.co](https://huggingface.co) for free AI access
4. **Railway CLI** (Optional): `npm install -g @railway/cli`

## Step 1: Get HuggingFace API Token

1. Go to [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Click **New token**
3. Name it (e.g., "AI Stock Trading App")
4. Select **Read** access
5. Copy the token (starts with `hf_...`)

## Step 2: Create Railway Project

### Option A: Via Railway Dashboard

1. Go to [railway.app/new](https://railway.app/new)
2. Click **Deploy from GitHub repo**
3. Authorize Railway to access your GitHub account
4. Select your `AIStockbroker` repository
5. Click **Deploy Now**

### Option B: Via Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
cd /path/to/AIStockbroker
railway init

# Link to existing project or create new one
railway link
```

## Step 3: Add PostgreSQL Database

1. In your Railway project dashboard, click **New** → **Database** → **PostgreSQL**
2. Railway will automatically create the database and set `DATABASE_URL` environment variable
3. Wait for the database to provision (takes ~30 seconds)

## Step 4: Configure Environment Variables

In Railway project settings → **Variables**, add the following:

### Required Variables

```bash
# AI Provider Configuration
AI_PROVIDER=huggingface
HF_API_TOKEN=hf_xxxxxxxxxxxxx  # Your token from Step 1
HF_MODEL=meta-llama/Meta-Llama-3-8B-Instruct

# Database (Auto-set by Railway, verify it exists)
DATABASE_URL=postgresql://...  # Should already be set

# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your_random_secret_key_here  # Generate with: python -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET_KEY=your_random_jwt_secret_here  # Generate with: python -c "import secrets; print(secrets.token_hex(32))"

# Port (Auto-set by Railway, verify it exists)
PORT=8080  # Should already be set
```

### Optional Variables

```bash
# For Gemini fallback (if you have a Google API key)
GOOGLE_API_KEY=AIzaSyBG...

# External market data APIs (optional)
ALPHA_VANTAGE_API_KEY=your_key
FINNHUB_API_KEY=your_key
MARKETSTACK_API_KEY=your_key
```

## Step 5: Deploy

Railway will automatically deploy when you push to GitHub. For manual deployment:

### Via GitHub (Automatic)

```bash
git add .
git commit -m "Configure for Railway deployment"
git push origin main
```

Railway automatically detects the push and deploys.

### Via Railway CLI

```bash
railway up
```

## Step 6: Verify Deployment

1. **Check Build Logs**: Railway Dashboard → **Deployments** → View logs
2. **Check Health Endpoint**: Once deployed, visit `https://your-app.up.railway.app/api/health`
3. **Test AI Endpoint**:

```bash
curl -X POST https://your-app.up.railway.app/api/ai/gemini-query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the current price of AAPL?"}'
```

Expected response:
```json
{
  "response": "📊 AAPL Current Price...",
  "query_type": "price_quote",
  "confidence": 0.9,
  "model_used": "meta-llama/Meta-Llama-3-8B-Instruct",
  "provider": "huggingface"
}
```

## Step 7: Database Migration (If needed)

If migrating from existing database:

```bash
# Export from existing database
pg_dump $OLD_DATABASE_URL > backup.sql

# Import to Railway PostgreSQL
psql $RAILWAY_DATABASE_URL < backup.sql
```

## Troubleshooting

### Build Fails

**Issue**: `ModuleNotFoundError: No module named 'huggingface_hub'`

**Solution**: Ensure `huggingface-hub>=0.20.0` is in `backend/requirements.txt`

### Database Connection Errors

**Issue**: `Could not connect to database`

**Solution**:
1. Check that PostgreSQL service is running in Railway
2. Verify `DATABASE_URL` environment variable is set
3. Check Railway logs for database connection errors

### AI Model Not Working

**Issue**: `AI model not initialized properly`

**Solution**:
1. Verify `HF_API_TOKEN` is set correctly in Railway
2. Check token has **Read** permissions on HuggingFace
3. Try switching model: Set `HF_MODEL=mistralai/Mistral-7B-Instruct-v0.3`

### Port Binding Issues

**Issue**: `Address already in use`

**Solution**: Railway automatically sets `PORT` variable. Ensure `backend/main.py` uses:
```python
port = int(os.getenv('PORT', 8080))
app.run(host='0.0.0.0', port=port)
```

## Monitoring

### View Logs

**Railway Dashboard**:
- Go to your project → **Deployments** → **View Logs**

**Railway CLI**:
```bash
railway logs
```

### Metrics

Railway provides automatic metrics:
- **CPU usage**
- **Memory usage**
- **Network traffic**
- **Request counts**

Access via Railway Dashboard → **Metrics** tab

## Scaling

### Vertical Scaling (More Resources)

Railway automatically scales resources based on your plan:
- **Starter Plan**: $5/month - 512MB RAM, 1 vCPU
- **Developer Plan**: $20/month - 8GB RAM, 8 vCPUs

### Horizontal Scaling (Multiple Instances)

Railway Pro plan supports multiple replicas:

```bash
railway scale --replicas 3
```

## Cost Estimates

### Railway Costs

- **Starter Plan**: ~$5-10/month
  - 500MB RAM
  - PostgreSQL database included
  - $0.000231/GB egress after 100GB

- **Developer Plan**: ~$20/month
  - Up to 8GB RAM
  - PostgreSQL database included
  - More generous limits

### HuggingFace Costs

- **Free Tier**: ~1000 requests/day
  - Perfect for development and light usage
  - No credit card required

- **Pro Tier**: $9/month
  - ~10,000 requests/day
  - Faster inference
  - Priority support

### Total Estimated Cost

- **Development**: $5-10/month (Railway Starter + HuggingFace Free)
- **Production**: $20-30/month (Railway Developer + HuggingFace Pro)

## Switching Between Providers

The app supports both Gemini and HuggingFace. To switch:

### Switch to Gemini

Set in Railway variables:
```bash
AI_PROVIDER=gemini
GOOGLE_API_KEY=AIzaSyBG...
```

### Switch to HuggingFace

Set in Railway variables:
```bash
AI_PROVIDER=huggingface
HF_API_TOKEN=hf_xxxxx
HF_MODEL=meta-llama/Meta-Llama-3-8B-Instruct
```

Railway will automatically redeploy with new settings.

## Custom Domain

1. Railway Dashboard → Project → **Settings** → **Domains**
2. Click **Add Custom Domain**
3. Enter your domain (e.g., `api.mystockapp.com`)
4. Add CNAME record in your DNS:
   - Name: `api`
   - Value: `your-app.up.railway.app`
5. Wait for DNS propagation (~5-30 minutes)

## Security Best Practices

1. **Never commit secrets**: Use Railway environment variables
2. **Use strong keys**: Generate with `python -c "import secrets; print(secrets.token_hex(32))"`
3. **Enable HTTPS**: Railway provides automatic SSL certificates
4. **Limit CORS**: Update `backend/api_server.py` CORS origins for production
5. **Monitor logs**: Check for suspicious activity

## Backup Strategy

### Database Backups

Railway automatically backs up PostgreSQL databases.

**Manual Backup**:
```bash
# Using Railway CLI
railway run pg_dump > backup_$(date +%Y%m%d).sql
```

### Configuration Backups

Keep environment variables documented in `.env.railway.template` (without actual values).

## Rolling Back

### Via Railway Dashboard

1. Go to **Deployments**
2. Find previous successful deployment
3. Click **...** → **Redeploy**

### Via Railway CLI

```bash
railway rollback
```

## Advanced Configuration

### Custom Build Command

Edit `railway.toml`:
```toml
[build]
buildCommand = "pip install --upgrade pip && pip install -r backend/requirements.txt"
```

### Custom Start Command

Edit `railway.toml`:
```toml
[deploy]
startCommand = "cd backend && gunicorn -w 4 -b 0.0.0.0:$PORT main:app"
```

### Health Check Tuning

Edit `railway.toml`:
```toml
[deploy]
healthcheckPath = "/api/health"
healthcheckTimeout = 300
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 10
```

## Support

- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Railway Discord**: [discord.gg/railway](https://discord.gg/railway)
- **HuggingFace Docs**: [huggingface.co/docs](https://huggingface.co/docs)
- **Project Issues**: [github.com/your-repo/issues](https://github.com/your-repo/issues)

## Next Steps

1. **Test the API**: Use Postman or curl to test endpoints
2. **Deploy Frontend**: Deploy the React frontend separately or to Vercel/Netlify
3. **Set Up CI/CD**: Configure GitHub Actions for automated testing
4. **Monitor Performance**: Use Railway metrics to track app performance
5. **Scale as Needed**: Upgrade Railway plan when ready for production traffic

---

**Congratulations!** Your AI Stock Trading Platform is now deployed on Railway with HuggingFace AI. 🎉
