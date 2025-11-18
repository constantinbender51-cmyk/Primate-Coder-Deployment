import requests
import json
from datetime import datetime
from typing import List, Dict, Optional

class NewsFetcher:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the NewsFetcher with optional API key
        
        Args:
            api_key: API key for news services (optional for public APIs)
        """
        self.api_key = api_key
        
    def fetch_news_api(self, query: str = "investment", language: str = "en") -> List[Dict]:
        """
        Fetch news from NewsAPI (requires free API key from newsapi.org)
        
        Args:
            query: Search query for news
            language: Language code (en, es, fr, etc.)
            
        Returns:
            List of news articles
        """
        if not self.api_key:
            return [{"error": "API key required for NewsAPI. Get one from newsapi.org"}]
            
        url = f"https://newsapi.org/v2/everything"
        params = {
            'q': f"{query} OR funding OR venture capital OR startup investment OR M&A OR IPO",
            'language': language,
            'apiKey': self.api_key,
            'pageSize': 15,
            'sortBy': 'publishedAt'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for article in data.get('articles', []):
                articles.append({
                    'source': 'NewsAPI',
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'url': article.get('url', ''),
                    'published_at': article.get('publishedAt', ''),
                    'source_name': article.get('source', {}).get('name', '')
                })
            return articles
            
        except requests.exceptions.RequestException as e:
            return [{"error": f"Failed to fetch from NewsAPI: {str(e)}"}]
    
    def fetch_guardian(self, query: str = "investment") -> List[Dict]:
        """
        Fetch news from The Guardian API (free, no API key required)
        
        Args:
            query: Search query for news
            
        Returns:
            List of news articles
        """
        url = "https://content.guardianapis.com/search"
        params = {
            'q': f"{query} funding venture capital startup",
            'show-fields': 'headline,trailText,webUrl,publication',
            'api-key': self.api_key if self.api_key else 'test',  # test key works for limited requests
            'page-size': 15,
            'section': 'business'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for article in data.get('response', {}).get('results', []):
                fields = article.get('fields', {})
                articles.append({
                    'source': 'The Guardian',
                    'title': fields.get('headline', ''),
                    'description': fields.get('trailText', ''),
                    'url': fields.get('webUrl', ''),
                    'published_at': article.get('webPublicationDate', ''),
                    'source_name': 'The Guardian'
                })
            return articles
            
        except requests.exceptions.RequestException as e:
            return [{"error": f"Failed to fetch from The Guardian: {str(e)}"}]
    
    def fetch_reddit_news(self, subreddit: str = "investing", limit: int = 15) -> List[Dict]:
        """
        Fetch news from Reddit (public API, no authentication required)
        
        Args:
            subreddit: Subreddit to fetch from
            limit: Number of posts to fetch
            
        Returns:
            List of news articles
        """
        url = f"https://www.reddit.com/r/{subreddit}/hot.json"
        headers = {'User-Agent': 'NewsFetcher/1.0'}
        
        try:
            response = requests.get(url, headers=headers, params={'limit': limit})
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for post in data.get('data', {}).get('children', []):
                post_data = post.get('data', {})
                # Filter for investment-related content
                title = post_data.get('title', '').lower()
                investment_keywords = ['investment', 'funding', 'venture', 'capital', 'startup', 'ipo', 'acquisition', 'merger', 'fund', 'raise']
                
                if any(keyword in title for keyword in investment_keywords):
                    articles.append({
                        'source': 'Reddit',
                        'title': post_data.get('title', ''),
                        'description': post_data.get('selftext', ''),
                        'url': post_data.get('url', ''),
                        'published_at': datetime.fromtimestamp(post_data.get('created_utc', 0)).isoformat(),
                        'source_name': f'r/{subreddit}',
                        'score': post_data.get('score', 0)
                    })
            return articles
            
        except requests.exceptions.RequestException as e:
            return [{"error": f"Failed to fetch from Reddit: {str(e)}"}]
    
    def fetch_all_news(self, query: str = "investment") -> List[Dict]:
        """
        Fetch investment news from multiple sources
        
        Args:
            query: Search query for news (default: investment)
            
        Returns:
            Combined list of news articles from all sources
        """
        all_articles = []
        
        # Fetch from multiple sources
        all_articles.extend(self.fetch_guardian(query))
        all_articles.extend(self.fetch_reddit_news("investing"))
        all_articles.extend(self.fetch_reddit_news("stocks"))
        
        # Only fetch from NewsAPI if API key is provided
        if self.api_key:
            all_articles.extend(self.fetch_news_api(query))
        
        # Filter out error responses and sort by date (newest first)
        valid_articles = [article for article in all_articles if 'error' not in article]
        
        # Sort by published date (newest first)
        valid_articles.sort(key=lambda x: x.get('published_at', ''), reverse=True)
        
        return valid_articles
    
    def fetch_investment_news(self) -> List[Dict]:
        """
        Specialized method to fetch major investment news
        
        Returns:
            List of investment-related news articles
        """
        investment_queries = [
            "venture capital funding",
            "startup investment",
            "M&A deals",
            "IPO news",
            "private equity",
            "major investments"
        ]
        
        all_investment_articles = []
        
        for query in investment_queries:
            articles = self.fetch_all_news(query)
            all_investment_articles.extend(articles)
        
        # Remove duplicates based on title
        seen_titles = set()
        unique_articles = []
        
        for article in all_investment_articles:
            title = article.get('title', '').lower()
            if title not in seen_titles:
                seen_titles.add(title)
                unique_articles.append(article)
        
        # Sort by date and return top 20
        unique_articles.sort(key=lambda x: x.get('published_at', ''), reverse=True)
        return unique_articles[:20]


def main():
    """Example usage of the NewsFetcher for investment news"""
    # Initialize without API key (will use free sources only)
    fetcher = NewsFetcher()
    
    # Or initialize with API key for NewsAPI
    # fetcher = NewsFetcher(api_key="your_newsapi_key_here")
    
    print("Fetching major investment news...")
    articles = fetcher.fetch_investment_news()
    
    print(f"\nFound {len(articles)} investment articles:")
    print("-" * 80)
    
    for i, article in enumerate(articles, 1):
        print(f"\n{i}. {article['title']}")
        print(f"   Source: {article['source']} - {article['source_name']}")
        print(f"   Description: {article.get('description', 'No description')[:200]}...")
        print(f"   URL: {article['url']}")
        print(f"   Published: {article.get('published_at', 'Unknown')}")
        print("-" * 80)


if __name__ == "__main__":
    main()