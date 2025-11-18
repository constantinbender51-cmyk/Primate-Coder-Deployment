#!/usr/bin/env python3
"""
Alternative script to run just the web server if CSV already exists
"""
from news_fetcher import create_web_server

if __name__ == "__main__":
    print("Starting web server on port 8080...")
    print("Visit http://localhost:8080 to download the CSV file")
    app = create_web_server()
    app.run(host='0.0.0.0', port=8080, debug=False)