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
            'CNN International': 'http://rss.cnn.com/rss/edition.rss',
            'CNN World': 'http://rss.cnn.com/rss/cnn_world.rss',
            'CNN US': 'http://rss.cnn.com/rss/cnn_us.rss',
            'CNN Politics': 'http://rss.cnn.com/rss/cnn_allpolitics.rss',
            'CNN Health': 'http://rss.cnn.com/rss/cnn_health.rss',
            'CNN Tech': 'http://rss.cnn.com/rss/cnn_tech.rss',
            # Crisis-native feeds (higher signal)
            'USGS Earthquakes (All, 24h)': 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.atom',
            'USGS Earthquakes (M2.5+, 24h)': 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.atom',
            'GDACS Global Disasters': 'https://www.gdacs.org/xml/rss.xml',
            'WHO Disease Outbreaks': 'https://www.who.int/feeds/entity/csr/don/en/rss.xml',
            'ReliefWeb Updates': 'https://reliefweb.int/updates?format=rss',
            # Add more working feeds
            'Yahoo News': 'https://news.yahoo.com/rss/world',
            'Google News': 'https://news.google.com/rss?topic=w&hl=en-US&gl=US&ceid=US:en',
            # Keep some backups
            'BBC World': 'http://feeds.bbci.co.uk/news/world/rss.xml',
            'Reuters': 'http://feeds.reuters.com/reuters/worldNews'
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
                
                # Fetch RSS with requests first (handles SSL/certs better), then parse bytes
                headers = {
                    'User-Agent': 'ARGUS/1.0 (+https://github.com/pierrev34/global-crisis-monitor)'
                }
                feed_content = None
                try:
                    resp = requests.get(feed_url, headers=headers, timeout=20)
                    resp.raise_for_status()
                    feed_content = resp.content
                except requests.exceptions.SSLError as ssl_err:
                    logger.warning(f"SSL issue for {source_name}, retrying without verify: {ssl_err}")
                    try:
                        resp = requests.get(feed_url, headers=headers, timeout=20, verify=False)
                        resp.raise_for_status()
                        feed_content = resp.content
                    except Exception as e2:
                        logger.warning(f"Failed fetching {source_name} after SSL fallback: {e2}")
                        continue
                except Exception as e:
                    logger.warning(f"HTTP error fetching {source_name}: {e}")
                    continue

                feed = feedparser.parse(feed_content)
                
                if feed.bozo:
                    logger.warning(f"RSS feed parsing issues for {source_name}: {feed.bozo_exception}")
                
                articles_from_source = 0
                
                for entry in feed.entries:
                    # Check if article is recent enough (be more lenient with time)
                    if self._is_article_recent(entry, cutoff_time):
                        # Check if article is crisis-related (be more inclusive)
                        if self._is_crisis_related(entry):
                            article = self._process_rss_entry(entry, source_name)
                            if article:
                                all_articles.append(article)
                                articles_from_source += 1
                                
                                # Increase limit per source for more articles
                                if articles_from_source >= 30:
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
        
        # Define impact/emergency cues and soft-news noise terms
        impact_terms = ['killed','deaths','dead','injured','wounded','missing','evacuate','evacuation',
                        'displaced','emergency','state of emergency','rescue','aid','relief','destroyed',
                        'collapsed','damage','casualties','fatalities','curfew','shutdown']
        general_crisis_words = ['breaking','urgent','alert','warning','threat','danger','attack','bomb',
                                'shoot','fire','burn','crash','rescue','emergency','evacuate','missing',
                                'search','found dead']
        soft_noise_terms = ['handwriting','prescription','policy','policies','guideline','guidelines',
                            'opinion','editorial','interview','feature','awareness','tips','prevention',
                            'advice','lifestyle']

        hazard_hit = any(keyword in text_to_check for keyword in self.crisis_keywords)
        impact_hit = any(word in text_to_check for word in (impact_terms + general_crisis_words))
        soft_noise = any(term in text_to_check for term in soft_noise_terms)

        # Stricter gate: require a hazard indicator and an impact/emergency cue, and not soft-news
        return hazard_hit and impact_hit and not soft_noise
    
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
