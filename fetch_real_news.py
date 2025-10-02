#!/usr/bin/env python3
"""
Alternative news fetcher using RSS feeds from major news sources
This provides real crisis news when GDELT API is not working optimally
"""

import requests
import feedparser
import json
from datetime import datetime, timedelta
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class RSSNewsFetcher:
    """Fetch real crisis news from RSS feeds"""
    
    def __init__(self):
        # Major news RSS feeds that cover crisis events
        self.rss_feeds = {
            'BBC World': 'http://feeds.bbci.co.uk/news/world/rss.xml',
            'Reuters World': 'https://feeds.reuters.com/reuters/worldNews',
            'CNN World': 'http://rss.cnn.com/rss/edition.rss',
            'AP News': 'https://feeds.apnews.com/ApNews/WorldNews',
            'Guardian World': 'https://www.theguardian.com/world/rss',
        }
        
        # Crisis-related keywords to filter articles
        self.crisis_keywords = [
            'earthquake', 'flood', 'hurricane', 'wildfire', 'tsunami', 'drought',
            'famine', 'war', 'conflict', 'refugee', 'humanitarian', 'crisis',
            'emergency', 'disaster', 'outbreak', 'pandemic', 'recession',
            'violence', 'protest', 'evacuation', 'casualties', 'aid'
        ]
    
    def fetch_crisis_articles(self, max_articles: int = 50) -> List[Dict]:
        """Fetch recent crisis articles from RSS feeds"""
        all_articles = []
        
        for source_name, feed_url in self.rss_feeds.items():
            try:
                logger.info(f"Fetching from {source_name}...")
                
                # Parse RSS feed
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:10]:  # Limit per source
                    # Check if article is crisis-related
                    title = entry.get('title', '')
                    summary = entry.get('summary', '')
                    text_to_check = (title + ' ' + summary).lower()
                    
                    if any(keyword in text_to_check for keyword in self.crisis_keywords):
                        article = {
                            'title': title,
                            'content': summary or title,
                            'url': entry.get('link', ''),
                            'source': source_name,
                            'published_date': entry.get('published', ''),
                            'language': 'en',
                            'tone': -3.0,  # Assume negative tone for crisis news
                            'raw_data': entry
                        }
                        all_articles.append(article)
                        
                        if len(all_articles) >= max_articles:
                            break
                
            except Exception as e:
                logger.warning(f"Error fetching from {source_name}: {e}")
                continue
        
        logger.info(f"Fetched {len(all_articles)} crisis articles from RSS feeds")
        return all_articles[:max_articles]

def get_real_crisis_news(max_articles: int = 20) -> List[Dict]:
    """Get real crisis news from RSS feeds"""
    fetcher = RSSNewsFetcher()
    return fetcher.fetch_crisis_articles(max_articles)

if __name__ == "__main__":
    # Test the RSS fetcher
    articles = get_real_crisis_news(5)
    
    print(f"📰 Found {len(articles)} real crisis articles:")
    print()
    
    for i, article in enumerate(articles, 1):
        print(f"{i}. {article['title']}")
        print(f"   Source: {article['source']}")
        print(f"   URL: {article['url']}")
        print()
