# Reddit Sentiment Trading Bot

AI-powered cryptocurrency trading signals based on Reddit sentiment analysis. This MVP scrapes posts from crypto-related subreddits, uses Claude to analyze sentiment, and generates trading signals with confidence scoring.

## Features

- **Reddit Scraping**: Automatically scrapes r/CryptoCurrency, r/Bitcoin, and r/ethereum
- **AI Sentiment Analysis**: Uses Claude 3.5 Sonnet to analyze post sentiment
- **Signal Generation**: Generates BUY/SELL signals with confidence scores
- **Paper Trading**: Tracks hypothetical trades in SQLite database
- **Web Dashboard**: Real-time dashboard to monitor signals and performance
- **Docker Support**: Easy deployment with Docker

## Tech Stack

- **Backend**: Python 3.11+, Flask
- **AI**: Anthropic Claude API
- **Scraping**: Apify (Reddit Scraper actor)
- **Database**: SQLite
- **Deployment**: Docker, Render/Railway/Fly.io compatible

## Quick Start

### Prerequisites

- Python 3.11+
- Anthropic API key
- Apify API token (optional, mock data available)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/wagecage/reddit-sentiment-trader.git
cd reddit-sentiment-trader
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

Required environment variables:
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `APIFY_API_TOKEN`: Your Apify token (optional, will use mock data if not provided)

### Running Locally

1. Run the scraper to generate initial signals:
```bash
python run_scraper.py
```

2. Start the web dashboard:
```bash
python app.py
```

3. Open your browser to `http://localhost:8080`

### Running with Docker

1. Build the image:
```bash
docker build -t reddit-sentiment-trader .
```

2. Run the container:
```bash
docker run -p 8080:8080 \
  -e ANTHROPIC_API_KEY=your_key \
  -e APIFY_API_TOKEN=your_token \
  reddit-sentiment-trader
```

## Configuration

Edit `.env` to customize:

- `REDDIT_SUBREDDITS`: Comma-separated list of subreddits (default: CryptoCurrency,Bitcoin,ethereum)
- `MAX_POSTS_PER_SCRAPE`: Maximum posts to scrape per subreddit (default: 50)
- `MIN_CONFIDENCE_SCORE`: Minimum confidence for signal generation (default: 0.6)
- `DATABASE_PATH`: Path to SQLite database (default: data/trading.db)

## Project Structure

```
reddit-sentiment-trader/
├── src/
│   ├── scrapers/          # Reddit scraping logic
│   ├── analyzers/         # Sentiment analysis with Claude
│   ├── signals/           # Signal generation
│   └── database/          # SQLite database operations
├── templates/             # HTML templates
├── app.py                 # Flask web application
├── run_scraper.py         # CLI scraper script
├── Dockerfile             # Docker configuration
└── requirements.txt       # Python dependencies
```

## API Endpoints

- `GET /`: Dashboard UI
- `GET /api/stats`: Performance statistics
- `GET /api/signals`: Recent trading signals
- `GET /api/trades`: Recent paper trades
- `GET /api/posts`: Recently analyzed posts
- `POST /api/scrape`: Trigger scrape and analysis
- `GET /api/health`: Health check

## How It Works

1. **Scraping**: Fetches recent posts from crypto subreddits using Apify
2. **Analysis**: Claude analyzes each post for sentiment (bullish/bearish/neutral)
3. **Aggregation**: Aggregates sentiment by asset (BTC, ETH, etc.)
4. **Signal Generation**: Generates trading signals based on:
   - Weighted sentiment score
   - Percentage of bullish/bearish posts
   - Average confidence
   - Minimum post threshold
5. **Storage**: Stores signals and posts in SQLite
6. **Dashboard**: Displays signals, trades, and performance metrics

## Signal Confidence Scoring

Signals are generated when:
- Minimum 3 posts mention the asset
- Average confidence > 0.6
- Clear bullish (>50% bullish posts, sentiment > 0.25) or bearish sentiment

Confidence score considers:
- Sentiment strength
- Percentage of bullish/bearish posts
- Post engagement (upvotes, comments)

## Deployment

### Deploy to Render

1. Fork this repository
2. Create new Web Service on Render
3. Connect your repository
4. Set environment variables in Render dashboard
5. Deploy!

### Deploy to Railway

1. Install Railway CLI: `npm i -g @railway/cli`
2. Login: `railway login`
3. Initialize: `railway init`
4. Add environment variables: `railway variables`
5. Deploy: `railway up`

### Deploy to Fly.io

1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Login: `fly auth login`
3. Launch: `fly launch`
4. Set secrets: `fly secrets set ANTHROPIC_API_KEY=your_key`
5. Deploy: `fly deploy`

## Limitations & Future Improvements

**Current Limitations:**
- Paper trading only (no real trades)
- Limited to 20 posts analyzed per run (API cost control)
- No automated scheduling (manual trigger required)
- Basic sentiment analysis (no price data integration)

**Future Improvements:**
- Integration with exchange APIs for real trading
- Automated scheduling with cron/celery
- Price data integration for backtesting
- More sophisticated signal algorithms
- Position management and risk controls
- Email/SMS notifications for high-confidence signals

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Disclaimer

This is an educational project for demonstration purposes only. Do not use for actual trading without proper risk management and testing. Cryptocurrency trading carries significant risk.

## Author

Built with Claude Code
