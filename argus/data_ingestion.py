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
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('articles', [])
            
            logger.info(f"Successfully fetched {len(articles)} articles from GDELT")
            return self._process_articles(articles)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from GDELT API: {e}")
            logger.info("Falling back to demo data...")
            return self._get_demo_data()
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing GDELT API response: {e}")
            logger.info("GDELT returned invalid JSON, falling back to demo data...")
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
                # Extract relevant fields
                processed_article = {
                    'title': article.get('title', '').strip(),
                    'content': article.get('content', '').strip(),
                    'url': article.get('url', ''),
                    'source': article.get('domain', ''),
                    'published_date': article.get('seendate', ''),
                    'language': article.get('language', 'en'),
                    'tone': article.get('tone', 0.0),  # GDELT tone score
                    'raw_data': article  # Keep original for reference
                }
                
                # Filter out articles that are too short or missing key data
                if (len(processed_article['content']) >= MIN_ARTICLE_LENGTH and 
                    processed_article['title'] and 
                    processed_article['url']):
                    
                    processed_articles.append(processed_article)
                    
            except Exception as e:
                logger.warning(f"Error processing article: {e}")
                continue
        
        logger.info(f"Processed {len(processed_articles)} valid articles")
        return processed_articles
    
    def _get_demo_data(self) -> List[Dict]:
        """
        Provide demo data when GDELT API is unavailable
        
        Returns:
            List of sample crisis articles
        """
        logger.info("Using demo crisis data for demonstration")
        
        demo_articles = [
            {
                'title': 'Earthquake Strikes Central Turkey, Magnitude 7.2',
                'content': 'A powerful earthquake measuring 7.2 on the Richter scale struck central Turkey near Ankara early this morning. The earthquake caused significant damage to buildings and infrastructure across the region. Emergency services are responding to reports of casualties and people trapped in collapsed buildings. The Turkish government has declared a state of emergency and is coordinating rescue efforts with international aid organizations.',
                'url': 'https://example.com/turkey-earthquake',
                'source': 'reuters.com',
                'published_date': '20241001120000',
                'language': 'en',
                'tone': -5.2
            },
            {
                'title': 'Humanitarian Crisis Deepens in Sudan as Conflict Continues',
                'content': 'The ongoing conflict in Sudan has created a severe humanitarian crisis, with over 2 million people displaced from their homes. The United Nations reports that food insecurity is reaching critical levels, particularly in the Darfur region. International aid organizations are struggling to deliver assistance due to security concerns and restricted access. The situation has been exacerbated by the destruction of key infrastructure including hospitals and schools.',
                'url': 'https://example.com/sudan-crisis',
                'source': 'bbc.com',
                'published_date': '20241001100000',
                'language': 'en',
                'tone': -7.8
            },
            {
                'title': 'Typhoon Approaches Philippines, Millions Evacuated',
                'content': 'Super Typhoon Maria is approaching the Philippines with winds reaching 180 km/h. Authorities in Manila and surrounding provinces have ordered the evacuation of over 3 million residents from coastal and low-lying areas. The Philippine Atmospheric Administration warns of catastrophic flooding and landslides. Emergency shelters have been set up across Luzon island, and the military is on standby for rescue operations.',
                'url': 'https://example.com/philippines-typhoon',
                'source': 'cnn.com',
                'published_date': '20241001080000',
                'language': 'en',
                'tone': -6.1
            },
            {
                'title': 'Economic Crisis Hits Argentina as Inflation Soars',
                'content': 'Argentina is facing a severe economic crisis as inflation rates have reached 150% annually. The peso has lost significant value against the dollar, making basic goods unaffordable for many citizens. Protests have erupted in Buenos Aires as people demand government action. The International Monetary Fund is in discussions with Argentine officials about potential emergency financial assistance.',
                'url': 'https://example.com/argentina-economy',
                'source': 'financial-times.com',
                'published_date': '20241001060000',
                'language': 'en',
                'tone': -4.5
            },
            {
                'title': 'Wildfire Emergency Declared in California',
                'content': 'A massive wildfire in Northern California has burned over 50,000 acres and forced the evacuation of several communities near Sacramento. The fire, dubbed the "Golden Fire," is being fueled by strong winds and dry conditions. Firefighters from across the state are battling the blaze, but containment efforts are being hampered by difficult terrain and weather conditions. Air quality alerts have been issued for the entire Bay Area.',
                'url': 'https://example.com/california-wildfire',
                'source': 'latimes.com',
                'published_date': '20241001040000',
                'language': 'en',
                'tone': -5.9
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


def get_crisis_articles(hours_back: int = 24, use_cache: bool = True) -> List[Dict]:
    """
    Convenience function to get crisis-related articles
    
    Args:
        hours_back: How many hours back to search
        use_cache: Whether to use cached data if available
        
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
    
    # Fetch fresh data
    articles = ingester.fetch_recent_articles(hours_back=hours_back)
    
    # Cache the results
    if articles:
        ingester.save_articles_to_file(articles)
    
    return articles
