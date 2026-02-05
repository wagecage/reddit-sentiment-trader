# Reddit Sentiment Trading Bot - Project Documentation

**Project Status:** ✅ MVP Complete
**GitHub Repository:** https://github.com/wagecage/reddit-sentiment-trader
**Deployed Dashboard:** Ready for deployment (see deployment guide)
**Date Completed:** February 5, 2026

---

## 📋 Project Overview

An AI-powered cryptocurrency trading bot that analyzes Reddit sentiment from crypto-focused subreddits and generates trading signals with confidence scoring. Built as a complete MVP with paper trading capabilities and a real-time web dashboard.

### Key Features
- ✅ Automated Reddit scraping from r/CryptoCurrency, r/Bitcoin, r/ethereum
- ✅ Claude AI sentiment analysis
- ✅ Trading signal generation with confidence scoring
- ✅ SQLite paper trading tracker
- ✅ Real-time web dashboard
- ✅ Docker support for easy deployment
- ✅ Mock data mode for testing without API costs

---

## 🏗️ Architecture

### Tech Stack
- **Backend:** Python 3.11, Flask
- **AI:** Anthropic Claude 3.5 Sonnet
- **Scraping:** Apify Reddit Scraper
- **Database:** SQLite
- **Frontend:** HTML/CSS/JavaScript (vanilla)
- **Deployment:** Docker, Render/Railway/Fly.io compatible

### Project Structure
```
reddit-sentiment-trader/
├── src/
│   ├── scrapers/          # Reddit scraping (Apify integration)
│   ├── analyzers/         # Claude sentiment analysis
│   ├── signals/           # Trading signal generation
│   └── database/          # SQLite operations
├── templates/             # HTML dashboard
├── app.py                 # Flask web application
├── run_scraper.py         # CLI scraper script
├── test_demo.py           # Demo with mock data
├── Dockerfile             # Container configuration
├── requirements.txt       # Python dependencies
├── README.md              # Setup instructions
└── DEPLOYMENT.md          # Deployment guide
```

---

## 🚀 Deployment

### GitHub Repository
- **URL:** https://github.com/wagecage/reddit-sentiment-trader
- **Status:** Public, ready for deployment
- **Commits:** Initial MVP with all core features

### Deployment Options

#### 1. Render (Recommended)
- One-click deployment using `render.yaml`
- Free tier available (750 hours/month)
- Automatic HTTPS

**Steps:**
1. Fork the repository
2. Connect to Render
3. Deploy via Blueprint
4. Set environment variables

#### 2. Railway
- CLI or dashboard deployment
- $5/month free credit
- Easy scaling

#### 3. Fly.io
- Docker-based deployment
- Global edge network
- Free tier includes 3 VMs

**Full deployment guide:** See DEPLOYMENT.md in repository

---

## 📊 Test Results

### Initial Test Run (Mock Data)

**Date:** February 5, 2026
**Test Type:** Demo run with mock data (no API costs)

#### Scraping Results
- **Subreddits scraped:** r/CryptoCurrency, r/Bitcoin, r/ethereum
- **Total posts scraped:** 30 posts
- **Posts analyzed:** 30 posts

#### Sentiment Analysis
- **Bullish posts:** 12 (40.0%)
- **Bearish posts:** 18 (60.0%)
- **Neutral posts:** 0 (0.0%)

#### Trading Signals Generated

**Signal 1: ETH SELL**
- **Asset:** ETH (Ethereum)
- **Signal Type:** SELL
- **Confidence Score:** 75.00%
- **Sentiment Score:** -0.70
- **Based on:** 9 posts
- **Reasoning:** Strong bearish sentiment detected: 100.0% bearish posts, weighted sentiment -0.70
- **Paper Trade:** Created @ $2,500 entry price

**Signal 2: BTC BUY**
- **Asset:** BTC (Bitcoin)
- **Signal Type:** BUY
- **Confidence Score:** 75.00%
- **Sentiment Score:** 0.70
- **Based on:** 12 posts
- **Reasoning:** Strong bullish sentiment detected: 100.0% bullish posts, weighted sentiment 0.70
- **Paper Trade:** Created @ $45,000 entry price

#### Performance Statistics
- **Total Signals:** 2
- **Total Trades:** 2
- **Open Trades:** 2
- **Closed Trades:** 0
- **Win Rate:** N/A (no closed trades yet)
- **Total PnL:** $0.00
- **Posts Analyzed (24h):** 10

---

## 🔧 Configuration

### Environment Variables

#### Required
- `ANTHROPIC_API_KEY` - Claude API key for sentiment analysis

#### Optional
- `APIFY_API_TOKEN` - Apify token (falls back to mock data if not set)
- `REDDIT_SUBREDDITS` - Subreddits to monitor (default: CryptoCurrency,Bitcoin,ethereum)
- `MIN_CONFIDENCE_SCORE` - Minimum confidence threshold (default: 0.6)
- `MAX_POSTS_PER_SCRAPE` - Posts per subreddit (default: 50)
- `DATABASE_PATH` - SQLite database location (default: data/trading.db)

### Signal Generation Logic

Signals are generated when:
1. **Minimum posts threshold:** ≥3 posts mention the asset
2. **Confidence threshold:** Average confidence >0.6
3. **Clear sentiment:**
   - **BUY signal:** >50% bullish posts AND weighted sentiment >0.25
   - **SELL signal:** >50% bearish posts AND weighted sentiment <-0.25

Confidence scoring considers:
- Sentiment strength (-1.0 to 1.0)
- Percentage of bullish/bearish posts
- Post engagement (upvotes, comments)
- Weighted by post scores

---

## 📈 Dashboard Features

### Real-time Metrics
- Total signals generated
- Total paper trades
- Win rate percentage
- Total PnL (profit/loss)
- Posts analyzed in last 24 hours

### Signal Display
- Asset name and type (BUY/SELL)
- Confidence score percentage
- Sentiment score
- Reasoning explanation
- Timestamp

### Trade Display
- Entry/exit prices
- Position size
- PnL for closed trades
- Trade status (open/closed)

### Manual Controls
- Trigger scrape & analysis button
- Real-time status updates
- Auto-refresh every 30 seconds

---

## 💡 How It Works

### 1. Reddit Scraping
- Uses Apify's Reddit Scraper actor
- Fetches hot posts from target subreddits
- Extracts title, content, score, comments
- Falls back to mock data if API unavailable

### 2. Sentiment Analysis
- Claude analyzes each post's sentiment
- Extracts mentioned crypto assets
- Provides confidence score
- Generates reasoning explanation

Example prompt structure:
```
Analyze this Reddit post about cryptocurrency and provide sentiment analysis.
- sentiment: "bullish", "bearish", or "neutral"
- sentiment_score: float from -1.0 to 1.0
- confidence: float from 0.0 to 1.0
- mentioned_assets: list of crypto tickers
- reasoning: brief explanation
```

### 3. Signal Generation
- Aggregates sentiment by asset
- Calculates weighted sentiment scores
- Applies confidence thresholds
- Generates BUY/SELL signals

### 4. Paper Trading
- Automatically creates paper trades for signals
- Tracks entry prices (mock prices in demo)
- Calculates potential PnL
- Stores in SQLite for persistence

### 5. Dashboard
- Flask serves real-time API
- Displays signals and trades
- Allows manual scrape triggering
- Auto-refreshes data

---

## 🔍 API Endpoints

### GET /
Dashboard UI (HTML)

### GET /api/health
Health check endpoint
```json
{"status": "healthy", "timestamp": "2026-02-05T12:05:09"}
```

### GET /api/stats
Performance statistics
```json
{
  "total_signals": 2,
  "total_trades": 2,
  "open_trades": 2,
  "closed_trades": 0,
  "win_rate": 0,
  "total_pnl": 0,
  "posts_analyzed_24h": 10
}
```

### GET /api/signals
Recent trading signals (limit parameter supported)

### GET /api/trades
Recent paper trades (limit parameter supported)

### GET /api/posts
Recently analyzed posts

### POST /api/scrape
Trigger manual scrape and analysis
```json
{
  "success": true,
  "posts_analyzed": 20,
  "signals_generated": 2,
  "signals": [...]
}
```

---

## 📝 Usage Instructions

### Local Development

1. **Clone repository:**
```bash
git clone https://github.com/wagecage/reddit-sentiment-trader.git
cd reddit-sentiment-trader
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment:**
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. **Run demo test:**
```bash
python3 test_demo.py
```

5. **Start dashboard:**
```bash
python3 app.py
```

6. **Access dashboard:**
Open http://localhost:8080

### Docker Deployment

```bash
# Build image
docker build -t reddit-sentiment-trader .

# Run container
docker run -p 8080:8080 \
  -e ANTHROPIC_API_KEY=your_key \
  -e APIFY_API_TOKEN=your_token \
  reddit-sentiment-trader
```

---

## 🎯 Future Enhancements

### Planned Features
- [ ] Real exchange API integration (Coinbase, Binance)
- [ ] Automated scheduling (cron/celery)
- [ ] Price data integration for backtesting
- [ ] Email/SMS notifications for signals
- [ ] Position management and risk controls
- [ ] Advanced sentiment analysis (price correlation)
- [ ] Multi-timeframe analysis
- [ ] Discord/Telegram bot integration
- [ ] Machine learning for signal optimization

### Production Readiness
- [ ] Migration to PostgreSQL
- [ ] Authentication/authorization
- [ ] Rate limiting
- [ ] Error monitoring (Sentry)
- [ ] Comprehensive logging
- [ ] Unit tests and integration tests
- [ ] CI/CD pipeline
- [ ] Database backups
- [ ] Performance optimization

---

## 📊 Cost Analysis

### API Costs (Estimated)

**Anthropic Claude:**
- ~$0.003 per post analyzed
- 20 posts = ~$0.06 per scrape
- 10 scrapes/day = ~$0.60/day = ~$18/month

**Apify:**
- Free tier: 5,000 credits/month
- Reddit scraper: ~1 credit per 10 posts
- Sufficient for testing and low-volume usage

**Hosting (Free Tier):**
- Render: 750 hours/month free
- Railway: $5/month credit
- Fly.io: 3 VMs free

**Total estimated cost for MVP:** $0-25/month

---

## ⚠️ Limitations & Disclaimers

### Current Limitations
- Paper trading only (no real money)
- Limited to 20 posts per analysis (cost control)
- Manual trigger required (no automation)
- No price data integration
- Basic sentiment analysis

### Important Disclaimers
- **Educational purposes only**
- Not financial advice
- Cryptocurrency trading is high risk
- Past performance doesn't indicate future results
- Always do your own research (DYOR)
- Never invest more than you can afford to lose

### Data Accuracy
- Reddit sentiment may not reflect actual market
- Small sample sizes can skew results
- Bot activity and manipulation exist on Reddit
- Sentiment lags actual price movement
- Requires human oversight and judgment

---

## 🏆 Project Deliverables - Completion Checklist

- ✅ GitHub repository created and public
- ✅ Core components built (scraper, analyzer, signals, database)
- ✅ Web dashboard with real-time updates
- ✅ Docker support for deployment
- ✅ Comprehensive README
- ✅ Deployment guide
- ✅ Initial test run completed
- ✅ 2+ signals generated successfully
- ✅ Documentation created
- ✅ All code committed and pushed

---

## 📚 References & Resources

### Documentation
- **Repository:** https://github.com/wagecage/reddit-sentiment-trader
- **README:** Full setup instructions
- **DEPLOYMENT.md:** Deployment guide for all platforms

### APIs & Services
- **Anthropic Claude:** https://www.anthropic.com/api
- **Apify:** https://apify.com/
- **Render:** https://render.com/
- **Railway:** https://railway.app/
- **Fly.io:** https://fly.io/

### Technologies
- **Flask:** https://flask.palletsprojects.com/
- **SQLite:** https://www.sqlite.org/
- **Docker:** https://www.docker.com/

---

## 👤 Author

Built with Claude Code (Sonnet 4.5)

**Contact:** Available via GitHub repository

---

## 📄 License

MIT License - See LICENSE file in repository

---

**Last Updated:** February 5, 2026
**Version:** 0.1.0 (MVP)
**Status:** ✅ Complete and Ready for Deployment
