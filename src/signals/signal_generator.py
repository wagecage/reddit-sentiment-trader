"""Trading signal generator based on sentiment analysis."""

from typing import Dict, Any, List, Optional
from datetime import datetime


class SignalGenerator:
    """Generates trading signals based on sentiment analysis."""

    def __init__(self, min_confidence: float = 0.6, min_posts: int = 3):
        """
        Initialize signal generator.

        Args:
            min_confidence: Minimum confidence score to generate signals
            min_posts: Minimum number of posts required for signal
        """
        self.min_confidence = min_confidence
        self.min_posts = min_posts

    def generate_signal(self, aggregated_sentiment: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate a trading signal from aggregated sentiment.

        Args:
            aggregated_sentiment: Aggregated sentiment metrics for an asset

        Returns:
            Trading signal dictionary or None if no signal
        """
        asset = aggregated_sentiment['asset']
        post_count = aggregated_sentiment['post_count']
        avg_confidence = aggregated_sentiment['avg_confidence']
        weighted_sentiment = aggregated_sentiment['weighted_sentiment']
        bullish_pct = aggregated_sentiment.get('bullish_pct', 0)
        bearish_pct = aggregated_sentiment.get('bearish_pct', 0)

        # Check minimum requirements
        if post_count < self.min_posts:
            return None

        if avg_confidence < self.min_confidence:
            return None

        # Determine signal type and confidence
        signal_type = None
        confidence_score = 0.0
        reasoning = ""

        # Strong bullish signal
        if weighted_sentiment > 0.5 and bullish_pct > 60:
            signal_type = "BUY"
            confidence_score = min(avg_confidence * (bullish_pct / 100), 1.0)
            reasoning = f"Strong bullish sentiment detected: {bullish_pct:.1f}% bullish posts, weighted sentiment {weighted_sentiment:.2f}"

        # Moderate bullish signal
        elif weighted_sentiment > 0.25 and bullish_pct > 50:
            signal_type = "BUY"
            confidence_score = min(avg_confidence * 0.8 * (bullish_pct / 100), 1.0)
            reasoning = f"Moderate bullish sentiment: {bullish_pct:.1f}% bullish posts, weighted sentiment {weighted_sentiment:.2f}"

        # Strong bearish signal
        elif weighted_sentiment < -0.5 and bearish_pct > 60:
            signal_type = "SELL"
            confidence_score = min(avg_confidence * (bearish_pct / 100), 1.0)
            reasoning = f"Strong bearish sentiment detected: {bearish_pct:.1f}% bearish posts, weighted sentiment {weighted_sentiment:.2f}"

        # Moderate bearish signal
        elif weighted_sentiment < -0.25 and bearish_pct > 50:
            signal_type = "SELL"
            confidence_score = min(avg_confidence * 0.8 * (bearish_pct / 100), 1.0)
            reasoning = f"Moderate bearish sentiment: {bearish_pct:.1f}% bearish posts, weighted sentiment {weighted_sentiment:.2f}"

        # No clear signal
        else:
            return None

        # Ensure confidence meets minimum threshold
        if confidence_score < self.min_confidence:
            return None

        return {
            'asset': asset,
            'signal_type': signal_type,
            'confidence_score': confidence_score,
            'sentiment_score': weighted_sentiment,
            'post_count': post_count,
            'reasoning': reasoning,
            'timestamp': datetime.now().isoformat(),
            'bullish_pct': bullish_pct,
            'bearish_pct': bearish_pct
        }

    def generate_signals_from_posts(self, analyzed_posts: List[Dict[str, Any]],
                                   target_assets: List[str] = None) -> List[Dict[str, Any]]:
        """
        Generate trading signals from analyzed posts.

        Args:
            analyzed_posts: List of posts with sentiment analysis
            target_assets: List of assets to generate signals for (default: auto-detect)

        Returns:
            List of trading signals
        """
        from ..analyzers import SentimentAnalyzer

        analyzer = SentimentAnalyzer()
        signals = []

        # Auto-detect assets if not specified
        if not target_assets:
            all_assets = set()
            for post in analyzed_posts:
                all_assets.update(post.get('mentioned_assets', []))
            target_assets = list(all_assets)

        # Generate signal for each asset
        for asset in target_assets:
            aggregated = analyzer.aggregate_sentiment(analyzed_posts, asset)
            signal = self.generate_signal(aggregated)

            if signal:
                signals.append(signal)

        return signals

    def should_enter_trade(self, signal: Dict[str, Any],
                          existing_positions: List[str] = None) -> bool:
        """
        Determine if we should enter a trade based on a signal.

        Args:
            signal: Trading signal
            existing_positions: List of assets we already have positions in

        Returns:
            True if we should enter the trade
        """
        if not signal:
            return False

        # Don't enter if we already have a position
        if existing_positions and signal['asset'] in existing_positions:
            return False

        # Check confidence threshold
        if signal['confidence_score'] < self.min_confidence:
            return False

        return True

    def calculate_position_size(self, signal: Dict[str, Any],
                               account_balance: float = 10000.0,
                               max_position_pct: float = 0.1) -> float:
        """
        Calculate position size based on signal confidence.

        Args:
            signal: Trading signal
            account_balance: Total account balance
            max_position_pct: Maximum percentage of account per position

        Returns:
            Position size in dollars
        """
        # Scale position size by confidence
        confidence = signal['confidence_score']
        base_position = account_balance * max_position_pct

        # Scale by confidence (0.6 to 1.0 confidence -> 50% to 100% of base)
        scaled_confidence = (confidence - 0.6) / 0.4  # Normalize to 0-1
        position_size = base_position * (0.5 + 0.5 * scaled_confidence)

        return round(position_size, 2)
