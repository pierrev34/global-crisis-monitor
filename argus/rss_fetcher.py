"""
RSS News Fetcher Module

Fetches real crisis news from RSS feeds of major news outlets
as an alternative to GDELT API when it's not working properly.
"""

import requests
import feedparser
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import re
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class RSSCrisisFetcher:
    """Fetch real crisis news from RSS feeds of major news outlets"""
    
    def __init__(self):
        # Major news RSS feeds that cover crisis events
        # Using HTTP where possible to avoid SSL issues
        self.rss_feeds = {
            'BBC World': 'http://feeds.bbci.co.uk/news/world/rss.xml',
            'CNN International': 'http://rss.cnn.com/rss/edition.rss',
            'CNN World': 'http://rss.cnn.com/rss/cnn_world.rss',
            'ABC News': 'https://abcnews.go.com/abcnews/internationalheadlines',
            'CBS News': 'https://www.cbsnews.com/latest/rss/world',
            'NBC News': 'http://feeds.nbcnews.com/nbcnews/public/world',
            'Fox News World': 'http://feeds.foxnews.com/foxnews/world',
            # Backup feeds
            'Reuters (backup)': 'http://feeds.reuters.com/reuters/worldNews',
            'AP News (backup)': 'http://feeds.apnews.com/ApNews/WorldNews'
        }
        
        # Crisis-related keywords to filter articles
        self.crisis_keywords = [
            # Natural disasters
            'earthquake', 'quake', 'seismic', 'tremor',
            'flood', 'flooding', 'deluge', 'inundation',
            'hurricane', 'typhoon', 'cyclone', 'storm',
            'wildfire', 'fire', 'blaze', 'inferno',
            'tsunami', 'tidal wave',
            'drought', 'famine', 'starvation',
            'volcano', 'volcanic', 'eruption',
            'landslide', 'mudslide', 'avalanche',
            
            # Human crises
            'war', 'conflict', 'fighting', 'battle',
            'refugee', 'displaced', 'evacuation',
            'humanitarian', 'crisis', 'emergency',
            'disaster', 'catastrophe', 'tragedy',
            'casualties', 'victims', 'deaths',
            'violence', 'attack', 'bombing',
            'protest', 'unrest', 'riot',
            
            # Health & economic
            'outbreak', 'pandemic', 'epidemic',
            'recession', 'economic crisis', 'inflation',
            'unemployment', 'poverty',
            
            # Aid and response
            'aid', 'relief', 'rescue', 'assistance',
            'emergency response', 'international help'
        ]
        
        # Exclude these terms to avoid false positives
        self.exclude_keywords = [
            'sports', 'game', 'match', 'player', 'team',
            'movie', 'film', 'entertainment', 'celebrity',
            'fashion', 'music', 'concert', 'album'
        ]
    
    def fetch_crisis_articles(self, max_articles: int = 50, hours_back: int = 24) -> List[Dict]:
        """
        Fetch recent crisis articles from RSS feeds
        
        Args:
            max_articles: Maximum number of articles to return
            hours_back: How many hours back to consider articles
            
        Returns:
            List of crisis article dictionaries
        """
        all_articles = []
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        logger.info(f"Fetching crisis articles from {len(self.rss_feeds)} RSS sources...")
        
        for source_name, feed_url in self.rss_feeds.items():
            try:
                logger.debug(f"Fetching from {source_name}: {feed_url}")
                
                # Parse RSS feed with timeout
                feed = feedparser.parse(feed_url)
                
                if feed.bozo:
                    logger.warning(f"RSS feed parsing issues for {source_name}: {feed.bozo_exception}")
                
                articles_from_source = 0
                
                for entry in feed.entries:
                    # Check if article is recent enough
                    if self._is_article_recent(entry, cutoff_time):
                        # Check if article is crisis-related
                        if self._is_crisis_related(entry):
                            article = self._process_rss_entry(entry, source_name)
                            if article:
                                all_articles.append(article)
                                articles_from_source += 1
                                
                                # Limit articles per source to ensure diversity
                                if articles_from_source >= 10:
                                    break
                
                logger.info(f"Found {articles_from_source} crisis articles from {source_name}")
                
                # Stop if we have enough articles
                if len(all_articles) >= max_articles:
                    break
                    
            except Exception as e:
                logger.warning(f"Error fetching from {source_name}: {e}")
                continue
        
        # Sort by recency and limit
        all_articles.sort(key=lambda x: x.get('published_date', ''), reverse=True)
        result = all_articles[:max_articles]
        
        logger.info(f"Successfully fetched {len(result)} crisis articles from RSS feeds")
        return result
    
    def _is_article_recent(self, entry: Dict, cutoff_time: datetime) -> bool:
        """Check if article is recent enough"""
        try:
            # Try different date fields
            date_fields = ['published_parsed', 'updated_parsed']
            
            for field in date_fields:
                if hasattr(entry, field) and getattr(entry, field):
                    entry_time = datetime(*getattr(entry, field)[:6])
                    return entry_time >= cutoff_time
            
            # If no parsed date, assume it's recent
            return True
            
        except Exception:
            # If date parsing fails, include the article
            return True
    
    def _is_crisis_related(self, entry: Dict) -> bool:
        """Check if article is related to crisis events"""
        # Get text to analyze
        title = entry.get('title', '').lower()
        summary = entry.get('summary', '').lower()
        text_to_check = f"{title} {summary}"
        
        # Check for exclude keywords first
        if any(exclude_word in text_to_check for exclude_word in self.exclude_keywords):
            return False
        
        # Check for crisis keywords
        crisis_score = sum(1 for keyword in self.crisis_keywords if keyword in text_to_check)
        
        # Require at least 1 crisis keyword
        return crisis_score >= 1
    
    def _process_rss_entry(self, entry: Dict, source_name: str) -> Optional[Dict]:
        """Process RSS entry into article format"""
        try:
            title = entry.get('title', '').strip()
            summary = entry.get('summary', '').strip()
            link = entry.get('link', '')
            
            # Basic validation
            if not title or not link:
                return None
            
            # Clean up summary (remove HTML tags if present)
            if summary:
                summary = re.sub(r'<[^>]+>', '', summary)
                summary = re.sub(r'\s+', ' ', summary).strip()
            
            # Use summary as content, fallback to title
            content = summary if summary else title
            
            # Extract domain from URL
            try:
                domain = urlparse(link).netloc
            except:
                domain = source_name
            
            # Get published date
            published_date = ''
            if hasattr(entry, 'published'):
                published_date = entry.published
            elif hasattr(entry, 'updated'):
                published_date = entry.updated
            
            article = {
                'title': title,
                'content': content,
                'url': link,
                'source': domain,
                'source_name': source_name,
                'published_date': published_date,
                'language': 'en',
                'tone': -2.0,  # Assume slightly negative tone for crisis news
                'fetched_via': 'rss',
                'raw_data': dict(entry)
            }
            
            return article
            
        except Exception as e:
            logger.warning(f"Error processing RSS entry: {e}")
            return None


def get_real_crisis_news(max_articles: int = 20, hours_back: int = 24) -> List[Dict]:
    """
    Convenience function to get real crisis news from RSS feeds
    
    Args:
        max_articles: Maximum number of articles to fetch
        hours_back: How many hours back to search
        
    Returns:
        List of crisis articles
    """
    fetcher = RSSCrisisFetcher()
    return fetcher.fetch_crisis_articles(max_articles, hours_back)


if __name__ == "__main__":
    # Test the RSS fetcher
    logging.basicConfig(level=logging.INFO)
    
    articles = get_real_crisis_news(10)
    
    print(f"📰 Found {len(articles)} real crisis articles:")
    print()
    
    for i, article in enumerate(articles, 1):
        print(f"{i}. {article['title']}")
        print(f"   Source: {article['source_name']}")
        print(f"   URL: {article['url']}")
        print(f"   Published: {article['published_date']}")
        print()
