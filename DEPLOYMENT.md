# Deployment Guide

## Quick Deploy to Render

The easiest way to deploy this application is using Render's Blueprint system.

### Step 1: Fork the Repository

1. Go to https://github.com/wagecage/reddit-sentiment-trader
2. Click "Fork" to create your own copy

### Step 2: Deploy to Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Blueprint"
3. Connect your GitHub account if not already connected
4. Select your forked repository
5. Render will automatically detect the `render.yaml` file
6. Set environment variables:
   - `ANTHROPIC_API_KEY`: Your Anthropic API key
   - `APIFY_API_TOKEN`: Your Apify token (optional, will use mock data if not set)
7. Click "Apply" to deploy

### Step 3: Access Your Dashboard

Once deployed, Render will provide a URL like:
```
https://reddit-sentiment-trader.onrender.com
```

## Alternative: Deploy to Railway

### Using Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Set environment variables
railway variables set ANTHROPIC_API_KEY=your_key_here
railway variables set APIFY_API_TOKEN=your_token_here

# Deploy
railway up
```

### Using Railway Dashboard

1. Go to [Railway](https://railway.app/)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Add environment variables in Settings
5. Deploy!

## Alternative: Deploy to Fly.io

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Launch app
fly launch --dockerfile Dockerfile

# Set secrets
fly secrets set ANTHROPIC_API_KEY=your_key_here
fly secrets set APIFY_API_TOKEN=your_token_here

# Deploy
fly deploy
```

## Environment Variables Required

### Required
- `ANTHROPIC_API_KEY`: Your Anthropic API key for Claude

### Optional
- `APIFY_API_TOKEN`: Apify token for Reddit scraping (will use mock data if not set)
- `REDDIT_SUBREDDITS`: Comma-separated subreddits (default: CryptoCurrency,Bitcoin,ethereum)
- `MIN_CONFIDENCE_SCORE`: Minimum confidence for signals (default: 0.6)
- `MAX_POSTS_PER_SCRAPE`: Max posts per subreddit (default: 50)

## Testing the Deployment

After deployment, test the endpoints:

```bash
# Health check
curl https://your-app-url.com/api/health

# Get stats
curl https://your-app-url.com/api/stats

# Get signals
curl https://your-app-url.com/api/signals

# Trigger a scrape (POST request)
curl -X POST https://your-app-url.com/api/scrape
```

## Monitoring

### Logs
- **Render**: View logs in the Render dashboard under your service
- **Railway**: Use `railway logs` or view in dashboard
- **Fly.io**: Use `fly logs` command

### Database
The SQLite database persists in the `/opt/render/project/src/data/` directory on Render (or equivalent on other platforms). Note that free tier deployments may lose data on restarts.

For production use, consider:
- Using a persistent volume
- Migrating to PostgreSQL
- Regular database backups

## Cost Considerations

### Free Tier Limits
- **Render**: 750 hours/month free, sleeps after inactivity
- **Railway**: $5/month credit, pay for usage
- **Fly.io**: Free tier includes 3 shared VMs

### API Costs
- **Anthropic Claude**: ~$0.003 per post analyzed (20 posts = ~$0.06)
- **Apify**: Free tier includes limited credits

### Optimization Tips
1. Limit `MAX_POSTS_PER_SCRAPE` to control costs
2. Use manual scraping instead of automated schedules
3. Start with mock data for testing
4. Monitor API usage carefully

## Scheduling Automated Scrapes

To run scrapes on a schedule, you can:

### Option 1: Add a cron job (Railway/Fly.io)
```python
# Add to app.py
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(func=run_scrape, trigger="interval", hours=6)
scheduler.start()
```

### Option 2: Use external cron service
- [cron-job.org](https://cron-job.org)
- [EasyCron](https://www.easycron.com)

Set up a cron job to call your `/api/scrape` endpoint every N hours.

## Security Notes

1. Never commit `.env` file or API keys to Git
2. Use environment variables for all secrets
3. Consider rate limiting the `/api/scrape` endpoint
4. Review Apify scraper settings to respect Reddit's ToS

## Troubleshooting

### App won't start
- Check logs for missing environment variables
- Verify all dependencies are in requirements.txt
- Check that PORT is set to 8080

### Scraping fails
- Verify APIFY_API_TOKEN is set correctly
- Check Apify dashboard for usage limits
- Fallback to mock data if needed

### Database errors
- Ensure data directory has write permissions
- Check disk space on hosting platform
- Consider migrating to PostgreSQL for production

## Next Steps

After deployment:
1. Test the dashboard by visiting your deployed URL
2. Run a manual scrape from the dashboard
3. Set up monitoring/alerts
4. Consider adding authentication for production use
5. Implement automated backtesting
6. Add email notifications for high-confidence signals
