"""
GDELT Data Ingestion Module

Fetches and processes news articles from the GDELT Project API.
"""

import requests
import pandas as pd
import json
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging
from .config import GDELT_BASE_URL, GDELT_PARAMS, MAX_ARTICLES_TO_PROCESS, MIN_ARTICLE_LENGTH

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import RSS fetcher
try:
    from .rss_fetcher import get_real_crisis_news
    RSS_AVAILABLE = True
    logger.info("RSS fetcher available")
except ImportError as e:
    logger.warning(f"RSS fetcher not available: {e}")
    RSS_AVAILABLE = False


class GDELTIngester:
    """Handles data ingestion from GDELT Project API"""
    
    def __init__(self):
        self.base_url = GDELT_BASE_URL
        self.default_params = GDELT_PARAMS.copy()
        
    def fetch_recent_articles(self, hours_back: int = 24, max_articles: int = None) -> List[Dict]:
        """
        Fetch recent articles from GDELT API
        
        Args:
            hours_back: How many hours back to search for articles
            max_articles: Maximum number of articles to fetch
            
        Returns:
            List of article dictionaries
        """
        if max_articles is None:
            max_articles = MAX_ARTICLES_TO_PROCESS
            
        # Calculate time range
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours_back)
        
        # Format dates for GDELT API (YYYYMMDDHHMMSS)
        start_date = start_time.strftime("%Y%m%d%H%M%S")
        end_date = end_time.strftime("%Y%m%d%H%M%S")
        
        # Prepare API parameters
        params = self.default_params.copy()
        params.update({
            "startdatetime": start_date,
            "enddatetime": end_date,
            "maxrecords": min(max_articles, 250)  # GDELT API limit
        })
        
        try:
            logger.info(f"Fetching articles from GDELT API from {start_time} to {end_time}")
            logger.debug(f"API URL: {self.base_url}")
            logger.debug(f"API Params: {params}")
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            # Log response details for debugging
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {response.headers}")
            
            data = response.json()
            articles = data.get('articles', [])
            
            logger.info(f"Successfully fetched {len(articles)} raw articles from GDELT")
            
            # Process and filter articles
            processed_articles = self._process_articles(articles)
            
            if not processed_articles:
                logger.warning("No valid articles found after processing. Using demo data...")
                return self._get_demo_data()
            
            logger.info(f"Successfully processed {len(processed_articles)} valid articles")
            return processed_articles
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from GDELT API: {e}")
            logger.info("Falling back to demo data...")
            return self._get_demo_data()
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing GDELT API response: {e}")
            logger.info("GDELT returned invalid JSON, falling back to demo data...")
            return self._get_demo_data()
        except Exception as e:
            logger.error(f"Unexpected error in GDELT fetch: {e}")
            logger.info("Falling back to demo data...")
            return self._get_demo_data()
    
    def _process_articles(self, raw_articles: List[Dict]) -> List[Dict]:
        """
        Process and clean raw articles from GDELT API
        
        Args:
            raw_articles: Raw article data from API
            
        Returns:
            Processed article list
        """
        processed_articles = []
        
        for article in raw_articles:
            try:
                # Extract relevant fields from GDELT structure
                title = article.get('title', '').strip()
                url = article.get('url', '')
                domain = article.get('domain', '')
                language = article.get('language', 'en').lower()
                
                # Skip non-English articles and gaming/mod content
                if language not in ['en', 'english']:
                    continue
                    
                # Filter out gaming content
                title_lower = title.lower()
                domain_lower = domain.lower()
                if any(keyword in title_lower or keyword in domain_lower 
                       for keyword in ['game', 'gaming', 'mod', 'patch', '生化危机', 'resident evil']):
                    continue
                
                # Create content from title (GDELT doesn't provide full content)
                content = title  # GDELT API typically only provides titles
                
                processed_article = {
                    'title': title,
                    'content': content,
                    'url': url,
                    'source': domain,
                    'published_date': article.get('seendate', ''),
                    'language': language,
                    'tone': article.get('tone', 0.0),
                    'country': article.get('sourcecountry', ''),
                    'raw_data': article
                }
                
                # Filter out articles that are missing key data
                if (title and url and domain and 
                    len(title) >= 20 and  # Reasonable title length
                    not url.startswith('https://example.com')):  # Not demo data
                    
                    processed_articles.append(processed_article)
                    logger.debug(f"Processed article: {title[:50]}...")
                    
            except Exception as e:
                logger.warning(f"Error processing article: {e}")
                continue
        
        logger.info(f"Processed {len(processed_articles)} valid articles from {len(raw_articles)} raw articles")
        return processed_articles
    
    def _get_demo_data(self) -> List[Dict]:
        """
        Provide minimal demo data when GDELT API is unavailable
        
        Returns:
            List of sample crisis articles
        """
        logger.info("Using demo crisis data for demonstration")
        logger.info("💡 Note: These are sample articles for demonstration purposes")
        logger.info("💡 To get real crisis data, the GDELT API integration needs to be working properly")
        
        demo_articles = [
            {
                'title': 'Earthquake Strikes Turkey, Magnitude 7.2',
                'content': 'A powerful earthquake struck Turkey causing significant damage. Emergency services are responding with international aid.',
                'url': 'https://example.com/turkey-earthquake',
                'source': 'reuters.com',
                'published_date': '20241001120000',
                'language': 'en',
                'tone': -5.2
            },
            {
                'title': 'Humanitarian Crisis in Sudan',
                'content': 'The ongoing conflict in Sudan has created a severe humanitarian crisis with over 2 million displaced.',
                'url': 'https://example.com/sudan-crisis',
                'source': 'bbc.com',
                'published_date': '20241001100000',
                'language': 'en',
                'tone': -7.8
            }
        ]
        
        return self._process_articles(demo_articles)
    
    def fetch_articles_by_keywords(self, keywords: List[str], hours_back: int = 24) -> List[Dict]:
        """
        Fetch articles matching specific keywords
        
        Args:
            keywords: List of keywords to search for
            hours_back: How many hours back to search
            
        Returns:
            List of matching articles
        """
        all_articles = []
        
        for keyword in keywords:
            params = self.default_params.copy()
            params['query'] = keyword
            
            # Calculate time range
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours_back)
            params.update({
                "startdatetime": start_time.strftime("%Y%m%d%H%M%S"),
                "enddatetime": end_time.strftime("%Y%m%d%H%M%S")
            })
            
            try:
                logger.info(f"Searching for keyword: {keyword}")
                response = requests.get(self.base_url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                articles = data.get('articles', [])
                processed = self._process_articles(articles)
                all_articles.extend(processed)
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error fetching articles for keyword '{keyword}': {e}")
                continue
        
        # Remove duplicates based on URL
        unique_articles = {}
        for article in all_articles:
            url = article['url']
            if url not in unique_articles:
                unique_articles[url] = article
        
        return list(unique_articles.values())
    
    def save_articles_to_file(self, articles: List[Dict], filename: str = "articles_cache.json"):
        """Save articles to JSON file for caching"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(articles, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(articles)} articles to {filename}")
        except Exception as e:
            logger.error(f"Error saving articles to file: {e}")
    
    def load_articles_from_file(self, filename: str = "articles_cache.json") -> List[Dict]:
        """Load articles from JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                articles = json.load(f)
            logger.info(f"Loaded {len(articles)} articles from {filename}")
            return articles
        except FileNotFoundError:
            logger.warning(f"Cache file {filename} not found")
            return []
        except Exception as e:
            logger.error(f"Error loading articles from file: {e}")
            return []


def get_crisis_articles(hours_back: int = 24, use_cache: bool = True, prefer_rss: bool = True) -> List[Dict]:
    """
    Convenience function to get crisis-related articles
    
    Args:
        hours_back: How many hours back to search
        use_cache: Whether to use cached data if available
        prefer_rss: Whether to prefer RSS feeds over GDELT API
        
    Returns:
        List of crisis-related articles
    """
    ingester = GDELTIngester()
    
    # Try to load from cache first if requested
    if use_cache:
        cached_articles = ingester.load_articles_from_file()
        if cached_articles:
            logger.info("Using cached articles")
            return cached_articles
    
    articles = []
    
    # Try RSS feeds first if available and preferred
    if prefer_rss and RSS_AVAILABLE:
        try:
            logger.info("🌐 Attempting to fetch real crisis news from RSS feeds...")
            articles = get_real_crisis_news(
                max_articles=MAX_ARTICLES_TO_PROCESS, 
                hours_back=hours_back
            )
            
            if articles and len(articles) >= 1:  # Use RSS even with fewer articles
                logger.info(f"✅ Successfully fetched {len(articles)} articles from RSS feeds")
                # Cache the results
                ingester.save_articles_to_file(articles)
                return articles
            else:
                logger.warning(f"Only found {len(articles)} articles from RSS feeds, trying GDELT for more coverage...")
                
        except Exception as e:
            logger.warning(f"RSS fetch failed: {e}, trying GDELT...")
    
    # Try GDELT API to supplement RSS articles
    logger.info("📡 Trying GDELT API for additional coverage...")
    gdelt_articles = ingester.fetch_recent_articles(hours_back=hours_back)
    
    # Combine RSS and GDELT articles with efficient deduplication
    if gdelt_articles:
        if articles:
            # Build URL set from existing articles for O(1) lookup
            seen_urls = {article.get('url', '') for article in articles}
            # Add only unique GDELT articles
            for article in gdelt_articles:
                url = article.get('url', '')
                if url and url not in seen_urls:
                    articles.append(article)
                    seen_urls.add(url)
                    if len(articles) >= MAX_ARTICLES_TO_PROCESS:
                        break
            logger.info(f"✅ Combined RSS and GDELT: {len(articles)} unique articles")
        else:
            articles = gdelt_articles
            logger.info(f"✅ Using GDELT articles: {len(articles)} articles")
    
    # Cache the results if we got any
    if articles:
        ingester.save_articles_to_file(articles)
    
    return articles
