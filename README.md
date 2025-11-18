# News Fetcher

A Python utility to fetch news from multiple sources including The Guardian, Reddit, and NewsAPI.

## Features

- Fetch news from The Guardian (free API)
- Fetch news from Reddit (public API)
- Fetch news from NewsAPI (requires free API key)
- Combine results from multiple sources
- Sort by publication date
- Error handling for API failures

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. (Optional) Get a free API key from [NewsAPI](https://newsapi.org) for additional news sources

## Usage

### Basic Usage
```python
from news_fetcher import NewsFetcher

# Initialize without API key (uses free sources)
fetcher = NewsFetcher()

# Fetch news
articles = fetcher.fetch_all_news("technology")

# Or with NewsAPI key
fetcher = NewsFetcher(api_key="your_newsapi_key")
articles = fetcher.fetch_all_news("politics")
```

### Individual Sources
```python
# Fetch from specific sources
guardian_news = fetcher.fetch_guardian("technology")
reddit_news = fetcher.fetch_reddit_news("worldnews")
newsapi_news = fetcher.fetch_news_api("business")
```

### Run as Script
```bash
python news_fetcher.py
```

## API Sources

- **The Guardian**: Free API, no key required (limited requests)
- **Reddit**: Public API, no authentication required
- **NewsAPI**: Requires free API key from newsapi.org

## Error Handling

The fetcher gracefully handles API failures and returns error information in the response.

## License

MIT License