#!/usr/bin/env python3
"""Generate additional test signals with more variety."""

import random
from src.database import TradingDatabase
from src.signals import SignalGenerator

def generate_varied_posts():
    """Generate posts with varied sentiment patterns."""
    # Create scenarios with strong sentiment for certain assets
    scenarios = [
        ('SOL', 'bullish', 10),  # 10 bullish SOL posts
        ('ADA', 'bearish', 8),   # 8 bearish ADA posts
        ('DOGE', 'bullish', 7),  # 7 bullish DOGE posts
        ('MATIC', 'bearish', 6), # 6 bearish MATIC posts
        ('AVAX', 'bullish', 5),  # 5 bullish AVAX posts
    ]

    posts = []
    post_id = 1000

    for asset, sentiment, count in scenarios:
        for i in range(count):
            if sentiment == 'bullish':
                titles = [
                    f"{asset} breaking out! Great fundamentals",
                    f"Why I'm bullish on {asset} long term",
                    f"{asset} looking extremely strong right now",
                    f"Just bought more {asset}, here's why",
                    f"{asset} is the future of crypto"
                ]
                sentiment_score = random.uniform(0.5, 0.9)
            else:  # bearish
                titles = [
                    f"Concerns about {asset} long-term viability",
                    f"Why I sold all my {asset}",
                    f"{asset} looking weak, possible downturn",
                    f"Red flags in {asset} project",
                    f"Time to exit {asset}?"
                ]
                sentiment_score = random.uniform(-0.9, -0.5)

            title = random.choice(titles)
            content = f"Detailed analysis of {asset}. {sentiment.capitalize()} outlook based on fundamentals."

            post = {
                'id': f'test_{post_id}',
                'title': title,
                'content': content,
                'score': random.randint(100, 2000),
                'num_comments': random.randint(20, 500),
                'subreddit': random.choice(['CryptoCurrency', 'Bitcoin', 'ethereum']),
                'sentiment': sentiment,
                'sentiment_score': sentiment_score,
                'confidence': random.uniform(0.65, 0.95),
                'mentioned_assets': [asset],
                'key_themes': ['cryptocurrency', 'trading']
            }
            posts.append(post)
            post_id += 1

    return posts

def main():
    print("Generating additional test signals...")

    db = TradingDatabase('data/trading.db')
    signal_gen = SignalGenerator(min_confidence=0.6, min_posts=3)

    # Generate varied posts
    posts = generate_varied_posts()

    # Store posts
    for post in posts:
        db.add_analyzed_post(
            post_id=post['id'],
            subreddit=post['subreddit'],
            title=post['title'],
            content=post['content'],
            sentiment=post['sentiment'],
            sentiment_score=post['sentiment_score'],
            mentioned_assets=','.join(post['mentioned_assets']),
            url=f"https://reddit.com/{post['id']}"
        )

    # Generate signals
    signals = signal_gen.generate_signals_from_posts(posts)

    print(f"\nGenerated {len(signals)} new signals:")

    for signal in signals:
        print(f"\n  {signal['asset']}: {signal['signal_type']}")
        print(f"    Confidence: {signal['confidence_score']:.1%}")
        print(f"    Sentiment: {signal['sentiment_score']:.2f}")
        print(f"    Posts: {signal['post_count']}")

        # Store signal
        signal_id = db.add_signal(
            asset=signal['asset'],
            signal_type=signal['signal_type'],
            confidence_score=signal['confidence_score'],
            sentiment_score=signal['sentiment_score'],
            source_subreddit='CryptoCurrency,Bitcoin,ethereum',
            post_count=signal['post_count'],
            reasoning=signal['reasoning']
        )

        # Create paper trade
        mock_prices = {
            'BTC': 45000, 'ETH': 2500, 'SOL': 100,
            'ADA': 0.5, 'DOGE': 0.15, 'MATIC': 0.8, 'AVAX': 35
        }
        entry_price = mock_prices.get(signal['asset'], 1000)

        db.add_paper_trade(
            signal_id=signal_id,
            asset=signal['asset'],
            trade_type=signal['signal_type'],
            entry_price=entry_price,
            position_size=1000
        )

    # Show final stats
    stats = db.get_performance_stats()
    print("\n" + "=" * 60)
    print("Final Statistics:")
    print("=" * 60)
    print(f"Total Signals: {stats['total_signals']}")
    print(f"Total Trades: {stats['total_trades']}")
    print(f"Posts Analyzed (24h): {stats['posts_analyzed_24h']}")

    print("\nDone! Start the dashboard to view all signals.")

if __name__ == '__main__':
    main()
