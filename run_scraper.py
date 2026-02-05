#!/usr/bin/env python3
"""CLI script to run the scraper and generate signals."""

import os
import sys
from dotenv import load_dotenv

from src.database import TradingDatabase
from src.scrapers import RedditScraper
from src.analyzers import SentimentAnalyzer
from src.signals import SignalGenerator

# Load environment variables
load_dotenv()


def main():
    """Run the scraper and generate signals."""
    print("=" * 60)
    print("Reddit Sentiment Trading Bot - Scraper")
    print("=" * 60)

    # Configuration
    subreddits = os.getenv('REDDIT_SUBREDDITS', 'CryptoCurrency,Bitcoin,ethereum').split(',')
    max_posts = int(os.getenv('MAX_POSTS_PER_SCRAPE', 50))
    min_confidence = float(os.getenv('MIN_CONFIDENCE_SCORE', 0.6))

    print(f"\nConfiguration:")
    print(f"  Subreddits: {', '.join(subreddits)}")
    print(f"  Max posts per subreddit: {max_posts}")
    print(f"  Min confidence score: {min_confidence}")

    # Initialize components
    print("\nInitializing components...")
    db = TradingDatabase(os.getenv('DATABASE_PATH', 'data/trading.db'))
    scraper = RedditScraper()
    analyzer = SentimentAnalyzer()
    signal_gen = SignalGenerator(min_confidence=min_confidence)

    # Scrape posts
    print("\n" + "=" * 60)
    print("Step 1: Scraping Reddit")
    print("=" * 60)

    all_posts = []
    for subreddit in subreddits:
        subreddit = subreddit.strip()
        print(f"\nScraping r/{subreddit}...")
        posts = scraper.scrape_subreddit(subreddit, max_posts)
        all_posts.extend(posts)
        print(f"  ✓ Scraped {len(posts)} posts")

    print(f"\nTotal posts scraped: {len(all_posts)}")

    # Analyze sentiment
    print("\n" + "=" * 60)
    print("Step 2: Analyzing Sentiment")
    print("=" * 60)

    # Limit to avoid high API costs in testing
    posts_to_analyze = all_posts[:20]
    print(f"\nAnalyzing {len(posts_to_analyze)} posts with Claude...")

    analyzed_posts = analyzer.analyze_batch(posts_to_analyze)

    print(f"  ✓ Analyzed {len(analyzed_posts)} posts")

    # Store analyzed posts
    print("\nStoring analyzed posts in database...")
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
    print("\n" + "=" * 60)
    print("Step 3: Generating Trading Signals")
    print("=" * 60)

    signals = signal_gen.generate_signals_from_posts(analyzed_posts)

    print(f"\nGenerated {len(signals)} trading signals:")

    for i, signal in enumerate(signals, 1):
        print(f"\n  Signal {i}:")
        print(f"    Asset: {signal['asset']}")
        print(f"    Type: {signal['signal_type']}")
        print(f"    Confidence: {signal['confidence_score']:.2%}")
        print(f"    Sentiment Score: {signal['sentiment_score']:.2f}")
        print(f"    Based on: {signal['post_count']} posts")
        print(f"    Reasoning: {signal['reasoning']}")

        # Store signal
        signal_id = db.add_signal(
            asset=signal['asset'],
            signal_type=signal['signal_type'],
            confidence_score=signal['confidence_score'],
            sentiment_score=signal['sentiment_score'],
            source_subreddit=','.join(subreddits),
            post_count=signal['post_count'],
            reasoning=signal['reasoning']
        )
        print(f"    ✓ Stored as signal ID: {signal_id}")

    # Display stats
    print("\n" + "=" * 60)
    print("Performance Statistics")
    print("=" * 60)

    stats = db.get_performance_stats()
    print(f"\n  Total Signals: {stats['total_signals']}")
    print(f"  Total Trades: {stats['total_trades']}")
    print(f"  Open Trades: {stats['open_trades']}")
    print(f"  Closed Trades: {stats['closed_trades']}")
    print(f"  Win Rate: {stats['win_rate']:.1f}%")
    print(f"  Total PnL: ${stats['total_pnl']:.2f}")
    print(f"  Posts Analyzed (24h): {stats['posts_analyzed_24h']}")

    print("\n" + "=" * 60)
    print("Scraping Complete!")
    print("=" * 60)
    print("\nView your dashboard at: http://localhost:8080")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
