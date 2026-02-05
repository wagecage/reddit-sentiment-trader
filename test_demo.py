#!/usr/bin/env python3
"""Demo script to test the system with mock data (no API keys required)."""

import os
import sys
import time
from datetime import datetime

from src.database import TradingDatabase
from src.scrapers import RedditScraper

# Mock sentiment analyzer for testing without API key
class MockSentimentAnalyzer:
    """Mock analyzer for testing."""

    def analyze_post(self, title, content, score=0, num_comments=0):
        # Simple keyword-based sentiment
        text = (title + " " + content).lower()

        if any(word in text for word in ['moon', 'bullish', 'buy', 'rally', 'pump', 'ath', 'surge']):
            sentiment = 'bullish'
            sentiment_score = 0.7
        elif any(word in text for word in ['crash', 'bearish', 'sell', 'dump', 'concern', 'risk', 'bear']):
            sentiment = 'bearish'
            sentiment_score = -0.7
        else:
            sentiment = 'neutral'
            sentiment_score = 0.0

        # Extract assets
        mentioned_assets = []
        if 'bitcoin' in text or 'btc' in text:
            mentioned_assets.append('BTC')
        if 'ethereum' in text or 'eth' in text:
            mentioned_assets.append('ETH')
        if 'doge' in text or 'dogecoin' in text:
            mentioned_assets.append('DOGE')

        return {
            'sentiment': sentiment,
            'sentiment_score': sentiment_score,
            'confidence': 0.75,
            'mentioned_assets': mentioned_assets,
            'key_themes': ['cryptocurrency', 'trading'],
            'reasoning': f'Keyword-based analysis detected {sentiment} sentiment'
        }

    def analyze_batch(self, posts):
        analyzed = []
        for post in posts:
            analysis = self.analyze_post(
                post.get('title', ''),
                post.get('content', ''),
                post.get('score', 0),
                post.get('num_comments', 0)
            )
            analyzed.append({**post, **analysis})
        return analyzed

    def aggregate_sentiment(self, analyzed_posts, asset=None):
        if asset:
            relevant_posts = [
                p for p in analyzed_posts
                if asset.upper() in [a.upper() for a in p.get('mentioned_assets', [])]
            ]
        else:
            relevant_posts = analyzed_posts

        if not relevant_posts:
            return {
                'asset': asset or 'ALL',
                'post_count': 0,
                'avg_sentiment_score': 0.0,
                'bullish_count': 0,
                'bearish_count': 0,
                'neutral_count': 0,
                'avg_confidence': 0.0,
                'weighted_sentiment': 0.0
            }

        total_posts = len(relevant_posts)
        bullish_count = sum(1 for p in relevant_posts if p['sentiment'] == 'bullish')
        bearish_count = sum(1 for p in relevant_posts if p['sentiment'] == 'bearish')
        neutral_count = sum(1 for p in relevant_posts if p['sentiment'] == 'neutral')

        avg_sentiment_score = sum(p['sentiment_score'] for p in relevant_posts) / total_posts
        avg_confidence = sum(p['confidence'] for p in relevant_posts) / total_posts

        total_weight = sum(max(p.get('score', 1), 1) for p in relevant_posts)
        weighted_sentiment = sum(
            p['sentiment_score'] * max(p.get('score', 1), 1)
            for p in relevant_posts
        ) / total_weight if total_weight > 0 else 0.0

        return {
            'asset': asset or 'ALL',
            'post_count': total_posts,
            'avg_sentiment_score': avg_sentiment_score,
            'bullish_count': bullish_count,
            'bearish_count': bearish_count,
            'neutral_count': neutral_count,
            'bullish_pct': (bullish_count / total_posts * 100) if total_posts > 0 else 0,
            'bearish_pct': (bearish_count / total_posts * 100) if total_posts > 0 else 0,
            'avg_confidence': avg_confidence,
            'weighted_sentiment': weighted_sentiment
        }


def main():
    """Run demo test."""
    print("=" * 60)
    print("Reddit Sentiment Trading Bot - DEMO TEST")
    print("Using mock data (no API keys required)")
    print("=" * 60)

    # Initialize components
    print("\nInitializing components...")
    db = TradingDatabase('data/trading.db')
    scraper = RedditScraper()
    analyzer = MockSentimentAnalyzer()

    from src.signals import SignalGenerator
    signal_gen = SignalGenerator(min_confidence=0.6)

    # Generate mock posts
    print("\n" + "=" * 60)
    print("Step 1: Scraping Reddit (using mock data)")
    print("=" * 60)

    subreddits = ['CryptoCurrency', 'Bitcoin', 'ethereum']
    all_posts = []

    for subreddit in subreddits:
        print(f"\nScraping r/{subreddit}...")
        posts = scraper._get_mock_data(subreddit, 10)
        all_posts.extend(posts)
        print(f"  ✓ Generated {len(posts)} mock posts")

    print(f"\nTotal posts: {len(all_posts)}")

    # Analyze sentiment
    print("\n" + "=" * 60)
    print("Step 2: Analyzing Sentiment (mock analysis)")
    print("=" * 60)

    analyzed_posts = analyzer.analyze_batch(all_posts)
    print(f"  ✓ Analyzed {len(analyzed_posts)} posts")

    # Store analyzed posts
    print("\nStoring analyzed posts...")
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

    # Show sentiment breakdown
    print("\nSentiment Breakdown:")
    sentiments = {}
    for post in analyzed_posts:
        s = post['sentiment']
        sentiments[s] = sentiments.get(s, 0) + 1

    for sentiment, count in sentiments.items():
        print(f"  {sentiment.capitalize()}: {count} posts ({count/len(analyzed_posts)*100:.1f}%)")

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

        # Create a paper trade
        mock_prices = {'BTC': 45000, 'ETH': 2500, 'DOGE': 0.15, 'ADA': 0.5, 'SOL': 100}
        entry_price = mock_prices.get(signal['asset'], 1000)
        trade_id = db.add_paper_trade(
            signal_id=signal_id,
            asset=signal['asset'],
            trade_type=signal['signal_type'],
            entry_price=entry_price,
            position_size=1000
        )
        print(f"    ✓ Created paper trade ID: {trade_id} @ ${entry_price}")

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
    print("Demo Test Complete!")
    print("=" * 60)
    print("\nTo view the dashboard:")
    print("  1. Run: python3 app.py")
    print("  2. Open: http://localhost:8080")
    print("\nThe dashboard will show all generated signals and trades.")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
