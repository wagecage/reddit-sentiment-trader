"""Reddit scraper using Apify."""

import os
import time
from typing import List, Dict, Any
from apify_client import ApifyClient


class RedditScraper:
    """Scrapes Reddit posts using Apify."""

    def __init__(self, api_token: str = None):
        """Initialize the scraper with Apify API token."""
        self.api_token = api_token or os.getenv('APIFY_API_TOKEN')

        # Only initialize client if token is available
        if self.api_token:
            self.client = ApifyClient(self.api_token)
        else:
            self.client = None
            print("Warning: APIFY_API_TOKEN not set, will use mock data")

    def scrape_subreddit(self, subreddit: str, max_posts: int = 50) -> List[Dict[str, Any]]:
        """
        Scrape posts from a subreddit using Apify Reddit Scraper.

        Args:
            subreddit: Name of the subreddit (without r/)
            max_posts: Maximum number of posts to scrape

        Returns:
            List of post dictionaries with title, content, score, etc.
        """
        print(f"Scraping r/{subreddit}...")

        # Use mock data if no API token
        if not self.client:
            return self._get_mock_data(subreddit, max_posts)

        # Use Apify's Reddit Scraper actor
        # Actor ID: trudax/reddit-scraper or vaclavrut/reddit-scraper
        run_input = {
            "startUrls": [
                {"url": f"https://www.reddit.com/r/{subreddit}/hot/"}
            ],
            "maxItems": max_posts,
            "maxPostCount": max_posts,
            "skipComments": True,
            "searchType": "posts",
            "sort": "hot"
        }

        try:
            # Run the actor and wait for it to finish
            run = self.client.actor("trudax/reddit-scraper").call(run_input=run_input)

            # Fetch results
            posts = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                # Extract relevant fields
                post_data = {
                    'id': item.get('id', ''),
                    'title': item.get('title', ''),
                    'content': item.get('selftext', '') or item.get('body', ''),
                    'score': item.get('score', 0),
                    'upvote_ratio': item.get('upvote_ratio', 0),
                    'num_comments': item.get('num_comments', 0),
                    'author': item.get('author', ''),
                    'created_utc': item.get('created_utc', 0),
                    'url': item.get('url', ''),
                    'permalink': item.get('permalink', ''),
                    'subreddit': subreddit
                }
                posts.append(post_data)

            print(f"Successfully scraped {len(posts)} posts from r/{subreddit}")
            return posts

        except Exception as e:
            print(f"Error scraping r/{subreddit}: {e}")
            # Fallback: Return mock data for testing
            return self._get_mock_data(subreddit, max_posts)

    def scrape_multiple_subreddits(self, subreddits: List[str], max_posts_per_sub: int = 50) -> Dict[str, List[Dict[str, Any]]]:
        """
        Scrape posts from multiple subreddits.

        Args:
            subreddits: List of subreddit names
            max_posts_per_sub: Maximum posts per subreddit

        Returns:
            Dictionary mapping subreddit names to lists of posts
        """
        results = {}

        for subreddit in subreddits:
            posts = self.scrape_subreddit(subreddit, max_posts_per_sub)
            results[subreddit] = posts
            # Be nice to the API
            time.sleep(2)

        return results

    def _get_mock_data(self, subreddit: str, count: int = 10) -> List[Dict[str, Any]]:
        """Generate mock data for testing when Apify is unavailable."""
        print(f"Using mock data for r/{subreddit}")

        mock_posts = [
            {
                'id': f'mock_{i}',
                'title': f'Bitcoin hits new ATH! To the moon! 🚀',
                'content': 'Just saw Bitcoin break through resistance. This bull run is looking strong. What do you all think about the current market conditions?',
                'score': 1500 + i * 100,
                'upvote_ratio': 0.92,
                'num_comments': 250 + i * 10,
                'author': f'crypto_trader_{i}',
                'created_utc': int(time.time()) - (i * 3600),
                'url': f'https://reddit.com/r/{subreddit}/mock_{i}',
                'permalink': f'/r/{subreddit}/comments/mock_{i}',
                'subreddit': subreddit
            } if i % 3 == 0 else
            {
                'id': f'mock_{i}',
                'title': f'Ethereum merge update - concerns about validators',
                'content': 'Has anyone else noticed the declining validator participation? Should we be worried about centralization risks?',
                'score': 800 + i * 50,
                'upvote_ratio': 0.85,
                'num_comments': 120 + i * 5,
                'author': f'eth_hodler_{i}',
                'created_utc': int(time.time()) - (i * 3600),
                'url': f'https://reddit.com/r/{subreddit}/mock_{i}',
                'permalink': f'/r/{subreddit}/comments/mock_{i}',
                'subreddit': subreddit
            } if i % 3 == 1 else
            {
                'id': f'mock_{i}',
                'title': f'Market analysis: Why I think we are entering bear territory',
                'content': 'Looking at the indicators, volume is declining, and we are seeing lower highs. This could be the start of a prolonged downturn. Time to take profits?',
                'score': 600 + i * 30,
                'upvote_ratio': 0.78,
                'num_comments': 180 + i * 8,
                'author': f'bear_trader_{i}',
                'created_utc': int(time.time()) - (i * 3600),
                'url': f'https://reddit.com/r/{subreddit}/mock_{i}',
                'permalink': f'/r/{subreddit}/comments/mock_{i}',
                'subreddit': subreddit
            }
            for i in range(min(count, 20))
        ]

        return mock_posts
