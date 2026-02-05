"""Sentiment analyzer using Claude API."""

import os
import json
from typing import Dict, Any, List
from anthropic import Anthropic


class SentimentAnalyzer:
    """Analyzes sentiment of Reddit posts using Claude."""

    def __init__(self, api_key: str = None):
        """Initialize the analyzer with Anthropic API key."""
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is required")

        self.client = Anthropic(api_key=self.api_key)

    def analyze_post(self, title: str, content: str, score: int = 0,
                     num_comments: int = 0) -> Dict[str, Any]:
        """
        Analyze sentiment of a single Reddit post.

        Args:
            title: Post title
            content: Post content/body
            score: Reddit score (upvotes - downvotes)
            num_comments: Number of comments

        Returns:
            Dictionary with sentiment analysis results
        """
        prompt = f"""Analyze this Reddit post about cryptocurrency and provide sentiment analysis.

Post Title: {title}

Post Content: {content}

Post Engagement: Score={score}, Comments={num_comments}

Please analyze and respond with a JSON object containing:
1. sentiment: "bullish", "bearish", or "neutral"
2. sentiment_score: a float from -1.0 (very bearish) to 1.0 (very bullish)
3. confidence: float from 0.0 to 1.0 indicating how confident you are
4. mentioned_assets: list of crypto assets mentioned (e.g., ["BTC", "ETH", "DOGE"])
5. key_themes: list of main themes/topics discussed
6. reasoning: brief explanation of your sentiment analysis

Only respond with valid JSON, no other text."""

        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Extract JSON from response
            response_text = message.content[0].text
            result = json.loads(response_text)

            return result

        except Exception as e:
            print(f"Error analyzing post: {e}")
            # Return neutral sentiment on error
            return {
                'sentiment': 'neutral',
                'sentiment_score': 0.0,
                'confidence': 0.0,
                'mentioned_assets': [],
                'key_themes': [],
                'reasoning': f'Error during analysis: {str(e)}'
            }

    def analyze_batch(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze sentiment for multiple posts.

        Args:
            posts: List of post dictionaries with 'title', 'content', etc.

        Returns:
            List of posts with added sentiment analysis
        """
        analyzed_posts = []

        for post in posts:
            title = post.get('title', '')
            content = post.get('content', '')
            score = post.get('score', 0)
            num_comments = post.get('num_comments', 0)

            # Skip posts without meaningful content
            if not title and not content:
                continue

            analysis = self.analyze_post(title, content, score, num_comments)

            # Combine post data with analysis
            analyzed_post = {
                **post,
                'sentiment': analysis['sentiment'],
                'sentiment_score': analysis['sentiment_score'],
                'confidence': analysis['confidence'],
                'mentioned_assets': analysis['mentioned_assets'],
                'key_themes': analysis['key_themes'],
                'reasoning': analysis['reasoning']
            }

            analyzed_posts.append(analyzed_post)

        return analyzed_posts

    def aggregate_sentiment(self, analyzed_posts: List[Dict[str, Any]],
                           asset: str = None) -> Dict[str, Any]:
        """
        Aggregate sentiment across multiple posts.

        Args:
            analyzed_posts: List of posts with sentiment analysis
            asset: Optional asset to filter by (e.g., "BTC", "ETH")

        Returns:
            Aggregated sentiment metrics
        """
        # Filter by asset if specified
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

        # Calculate metrics
        total_posts = len(relevant_posts)
        bullish_count = sum(1 for p in relevant_posts if p['sentiment'] == 'bullish')
        bearish_count = sum(1 for p in relevant_posts if p['sentiment'] == 'bearish')
        neutral_count = sum(1 for p in relevant_posts if p['sentiment'] == 'neutral')

        avg_sentiment_score = sum(p['sentiment_score'] for p in relevant_posts) / total_posts
        avg_confidence = sum(p['confidence'] for p in relevant_posts) / total_posts

        # Weighted sentiment (considering post score as weight)
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
