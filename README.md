# Investment News Fetcher

A Python utility to fetch major investment news from multiple sources including The Guardian, Reddit, and NewsAPI.

## Features

- Fetch investment news from The Guardian (free API)
- Fetch investment news from Reddit investing communities
- Fetch investment news from NewsAPI (requires free API key)
- Specialized investment news queries (VC funding, M&A, IPOs, etc.)
- Combine results from multiple sources
- Sort by publication date
- Error handling for API failures
- Deduplication of articles

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

# Fetch investment news
articles = fetcher.fetch_investment_news()

# Or with NewsAPI key
fetcher = NewsFetcher(api_key="your_newsapi_key")
articles = fetcher.fetch_investment_news()
```

### Individual Sources
```python
# Fetch from specific sources
guardian_news = fetcher.fetch_guardian("venture capital")
reddit_news = fetcher.fetch_reddit_news("investing")
newsapi_news = fetcher.fetch_news_api("investment")
```

### Run as Script
```bash
python news_fetcher.py
```

## Investment News Coverage

The fetcher specializes in:
- Venture capital funding rounds
- Startup investments
- M&A deals and acquisitions
- IPO announcements
- Private equity investments
- Major corporate investments

## API Sources

- **The Guardian**: Free API, no key required (limited requests)
- **Reddit**: Public API, no authentication required (r/investing, r/stocks)
- **NewsAPI**: Requires free API key from newsapi.org

## Error Handling

The fetcher gracefully handles API failures and returns error information in the response.

## License

MIT License