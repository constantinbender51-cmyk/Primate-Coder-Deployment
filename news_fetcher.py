import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
import os
from flask import Flask, send_file

class NewsFetcher:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the NewsFetcher with optional API key
        
        Args:
            api_key: API key for news services (optional for public APIs)
        """
        self.api_key = api_key
        
    def fetch_news_api(self, query: str = "investment", language: str = "en", from_date: str = None, to_date: str = None) -> List[Dict]:
        """
        Fetch news from NewsAPI (requires free API key from newsapi.org)
        
        Args:
            query: Search query for news
            language: Language code (en, es, fr, etc.)
            from_date: Start date in YYYY-MM-DD format
            to_date: End date in YYYY-MM-DD format
            
        Returns:
            List of news articles
        """
        if not self.api_key:
            return [{"error": "API key required for NewsAPI. Get one from newsapi.org"}]
            
        url = f"https://newsapi.org/v2/everything"
        params = {
            'q': f"{query} OR funding OR venture capital OR startup investment OR M&A OR IPO OR Bitcoin OR cryptocurrency OR stock market OR economy",
            'language': language,
            'apiKey': self.api_key,
            'pageSize': 50,
            'sortBy': 'publishedAt'
        }
        
        # Add date filters if provided
        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date
        
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
    
    def fetch_guardian(self, query: str = "investment", from_date: str = None, to_date: str = None) -> List[Dict]:
        """
        Fetch news from The Guardian API (free, no API key required)
        
        Args:
            query: Search query for news
            from_date: Start date in YYYY-MM-DD format
            to_date: End date in YYYY-MM-DD format
            
        Returns:
            List of news articles
        """
        url = "https://content.guardianapis.com/search"
        params = {
            'q': f"{query} funding venture capital startup Bitcoin cryptocurrency stock market economy",
            'show-fields': 'headline,trailText,webUrl,publication',
            'api-key': self.api_key if self.api_key else 'test',  # test key works for limited requests
            'page-size': 50,
            'section': 'business'
        }
        
        # Add date filters if provided
        if from_date:
            params['from-date'] = from_date
        if to_date:
            params['to-date'] = to_date
        
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
    
    def fetch_reddit_news(self, subreddit: str = "investing", limit: int = 50) -> List[Dict]:
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
                investment_keywords = ['investment', 'funding', 'venture', 'capital', 'startup', 'ipo', 'acquisition', 'merger', 'fund', 'raise', 'bitcoin', 'crypto', 'cryptocurrency', 'btc', 'blockchain', 'stock', 'market', 'economy', 'financial', 'finance']
                
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
    
    def fetch_all_news(self, query: str = "investment", from_date: str = None, to_date: str = None) -> List[Dict]:
        """
        Fetch investment news from multiple sources
        
        Args:
            query: Search query for news (default: investment)
            from_date: Start date in YYYY-MM-DD format
            to_date: End date in YYYY-MM-DD format
            
        Returns:
            Combined list of news articles from all sources
        """
        all_articles = []
        
        # Fetch from multiple sources
        all_articles.extend(self.fetch_guardian(query, from_date, to_date))
        all_articles.extend(self.fetch_reddit_news("investing"))
        all_articles.extend(self.fetch_reddit_news("stocks"))
        all_articles.extend(self.fetch_reddit_news("Bitcoin"))
        all_articles.extend(self.fetch_reddit_news("CryptoCurrency"))
        all_articles.extend(self.fetch_reddit_news("worldnews"))
        all_articles.extend(self.fetch_reddit_news("news"))
        
        # Only fetch from NewsAPI if API key is provided
        if self.api_key:
            all_articles.extend(self.fetch_news_api(query, from_date=from_date, to_date=to_date))
        
        # Filter out error responses and sort by date (newest first)
        valid_articles = [article for article in all_articles if 'error' not in article]
        
        # Sort by published date (newest first)
        valid_articles.sort(key=lambda x: x.get('published_at', ''), reverse=True)
        
        return valid_articles
    
    def fetch_major_news_2018_to_today(self) -> List[Dict]:
        """
        Fetch major news from 2018 to today
        
        Returns:
            List of major news articles from 2018 to present
        """
        # Define date range
        from_date = "2018-01-01"
        to_date = datetime.now().strftime("%Y-%m-%d")
        
        # Major news queries covering different categories
        major_news_queries = [
            "politics",
            "economy",
            "technology",
            "business",
            "finance",
            "world news",
            "breaking news",
            "stock market",
            "cryptocurrency",
            "climate change",
            "health",
            "science",
            "artificial intelligence",
            "space",
            "entertainment"
        ]
        
        all_major_articles = []
        
        for query in major_news_queries:
            print(f"Fetching news for: {query}")
            articles = self.fetch_all_news(query, from_date, to_date)
            all_major_articles.extend(articles)
        
        # Remove duplicates based on title
        seen_titles = set()
        unique_articles = []
        
        for article in all_major_articles:
            title = article.get('title', '').lower()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_articles.append(article)
        
        # Sort by date and return 20-50 articles
        unique_articles.sort(key=lambda x: x.get('published_at', ''), reverse=True)
        return unique_articles[:50]
    
    def save_news_to_csv(self, articles: List[Dict], filename: str = "major_news_2018_to_today.csv") -> str:
        """
        Save news articles to CSV file
        
        Args:
            articles: List of news articles
            filename: Output CSV filename
            
        Returns:
            Path to the created CSV file
        """
        if not articles:
            return None
        
        # Prepare data for CSV
        data = []
        for article in articles:
            # Parse and format date
            published_at = article.get('published_at', '')
            try:
                if 'T' in published_at:
                    date_obj = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    formatted_date = date_obj.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    formatted_date = published_at
            except:
                formatted_date = published_at
            
            data.append({
                'Date': formatted_date,
                'Title': article.get('title', ''),
                'Source': article.get('source', ''),
                'Source Name': article.get('source_name', ''),
                'Description': article.get('description', ''),
                'URL': article.get('url', '')
            })
        
        # Create DataFrame and save to CSV
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        return filename


def create_web_server():
    """Create and run Flask web server with download link"""
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Major News 2018-Today</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .download-btn { 
                    display: inline-block; 
                    padding: 15px 30px; 
                    background: #007cba; 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 5px; 
                    font-size: 18px;
                    margin: 20px 0;
                }
                .download-btn:hover { background: #005a87; }
                .info { background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Major News Archive (2018 - Today)</h1>
                <div class="info">
                    <p>This archive contains major news articles from 2018 to today, collected from multiple sources including The Guardian, Reddit, and NewsAPI.</p>
                    <p>The CSV file includes articles sorted by date with titles, sources, descriptions, and URLs.</p>
                </div>
                <a href="/download" class="download-btn">Download CSV File</a>
                <p><strong>Note:</strong> The file contains 20-50 major news articles from various categories including politics, economy, technology, business, and more.</p>
            </div>
        </body>
        </html>
        '''
    
    @app.route('/download')
    def download_file():
        # Generate the CSV file if it doesn't exist
        csv_file = "major_news_2018_to_today.csv"
        if not os.path.exists(csv_file):
            fetcher = NewsFetcher()
            articles = fetcher.fetch_major_news_2018_to_today()
            fetcher.save_news_to_csv(articles, csv_file)
        
        return send_file(csv_file, as_attachment=True)
    
    return app


def main():
    """Main function to fetch news and start web server"""
    print("Starting Major News Fetcher (2018-Today)...")
    
    # Initialize fetcher
    fetcher = NewsFetcher()
    
    # Fetch major news from 2018 to today
    print("Fetching major news from 2018 to today...")
    articles = fetcher.fetch_major_news_2018_to_today()
    
    # Save to CSV
    print(f"Saving {len(articles)} articles to CSV...")
    csv_file = fetcher.save_news_to_csv(articles)
    
    if csv_file:
        print(f"CSV file created: {csv_file}")
        
        # Start web server
        print("Starting web server on port 8080...")
        print("Visit http://localhost:8080 to download the CSV file")
        
        app = create_web_server()
        app.run(host='0.0.0.0', port=8080, debug=False)
    else:
        print("Failed to create CSV file")


if __name__ == "__main__":
    main()