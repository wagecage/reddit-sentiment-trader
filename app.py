"""Flask web application for Reddit Sentiment Trading Bot."""

import os
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv

from src.database import TradingDatabase
from src.scrapers import RedditScraper
from src.analyzers import SentimentAnalyzer
from src.signals import SignalGenerator

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-prod')

# Initialize components
db = TradingDatabase(os.getenv('DATABASE_PATH', 'data/trading.db'))


@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')


@app.route('/api/stats')
def get_stats():
    """Get performance statistics."""
    stats = db.get_performance_stats()
    return jsonify(stats)


@app.route('/api/signals')
def get_signals():
    """Get recent trading signals."""
    limit = request.args.get('limit', 20, type=int)
    signals = db.get_recent_signals(limit)
    return jsonify(signals)


@app.route('/api/trades')
def get_trades():
    """Get recent paper trades."""
    limit = request.args.get('limit', 20, type=int)
    trades = db.get_recent_trades(limit)
    return jsonify(trades)


@app.route('/api/posts')
def get_posts():
    """Get recently analyzed posts."""
    limit = request.args.get('limit', 50, type=int)
    posts = db.get_recent_posts(limit)
    return jsonify(posts)


@app.route('/api/scrape', methods=['POST'])
def trigger_scrape():
    """Manually trigger a scrape and analysis."""
    try:
        subreddits = os.getenv('REDDIT_SUBREDDITS', 'CryptoCurrency,Bitcoin,ethereum').split(',')
        max_posts = int(os.getenv('MAX_POSTS_PER_SCRAPE', 50))

        # Initialize scraper
        scraper = RedditScraper()

        # Scrape posts
        all_posts = []
        for subreddit in subreddits:
            posts = scraper.scrape_subreddit(subreddit.strip(), max_posts)
            all_posts.extend(posts)

        # Analyze sentiment
        analyzer = SentimentAnalyzer()
        analyzed_posts = analyzer.analyze_batch(all_posts[:20])  # Limit to avoid high API costs

        # Store analyzed posts
        for post in analyzed_posts:
            db.add_analyzed_post(
                post_id=post['id'],
                subreddit=post['subreddit'],
                title=post['title'],
                content=post['content'],
                sentiment=post['sentiment'],
                sentiment_score=post['sentiment_score'],
                mentioned_assets=','.join(post.get('mentioned_assets', [])),
                url=post.get('url', '')
            )

        # Generate signals
        signal_gen = SignalGenerator(
            min_confidence=float(os.getenv('MIN_CONFIDENCE_SCORE', 0.6))
        )
        signals = signal_gen.generate_signals_from_posts(analyzed_posts)

        # Store signals
        stored_signals = []
        for signal in signals:
            signal_id = db.add_signal(
                asset=signal['asset'],
                signal_type=signal['signal_type'],
                confidence_score=signal['confidence_score'],
                sentiment_score=signal['sentiment_score'],
                source_subreddit=','.join(subreddits),
                post_count=signal['post_count'],
                reasoning=signal['reasoning']
            )
            stored_signals.append({**signal, 'id': signal_id})

        return jsonify({
            'success': True,
            'posts_analyzed': len(analyzed_posts),
            'signals_generated': len(signals),
            'signals': stored_signals
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
