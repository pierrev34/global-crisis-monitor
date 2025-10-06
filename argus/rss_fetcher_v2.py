"""
Enhanced RSS Fetcher with NGO/Human Rights Sources
Focuses on underreported crises and systemic human rights issues
"""

import requests
import feedparser
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import re
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class EnhancedCrisisFetcher:
    """
    Fetch crisis news from diverse sources including NGOs, human rights orgs,
    and mainstream media to capture both breaking news and systemic crises
    """
    
    def __init__(self):
        # Organized by source type for better categorization
        self.rss_feeds = {
            # ============ HUMAN RIGHTS & NGO SOURCES ============
            # These cover underreported, systemic crises
            'Human Rights Watch': {
                'url': 'https://www.hrw.org/rss',
                'category': 'Human Rights Violations',
                'priority': 'high'
            },
            'Amnesty International': {
                'url': 'https://www.amnesty.org/en/rss/',
                'category': 'Human Rights Violations', 
                'priority': 'high'
            },
            'UN OCHA (Humanitarian Affairs)': {
                'url': 'https://www.unocha.org/rss.xml',
                'category': 'Humanitarian Crises',
                'priority': 'high'
            },
            'ReliefWeb - All Updates': {
                'url': 'https://reliefweb.int/updates/rss.xml',
                'category': 'Humanitarian Crises',
                'priority': 'high'
            },
            'Doctors Without Borders (MSF)': {
                'url': 'https://www.msf.org/rss.xml',
                'category': 'Health Emergencies',
                'priority': 'high'
            },
            'UNHCR - Refugee News': {
                'url': 'https://www.unhcr.org/rssfeed/rss.xml',
                'category': 'Humanitarian Crises',
                'priority': 'high'
            },
            'International Crisis Group': {
                'url': 'https://www.crisisgroup.org/rss.xml',
                'category': 'Political Conflicts',
                'priority': 'high'
            },
            'ICRC (Red Cross)': {
                'url': 'https://www.icrc.org/en/rss-feeds',
                'category': 'Humanitarian Crises',
                'priority': 'high'
            },
            
            # ============ DISASTER MONITORING ============
            'GDACS Global Disasters': {
                'url': 'https://www.gdacs.org/xml/rss.xml',
                'category': 'Natural Disasters',
                'priority': 'high'
            },
            'USGS Earthquakes (Significant)': {
                'url': 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_week.atom',
                'category': 'Natural Disasters',
                'priority': 'high'
            },
            'USGS Earthquakes (M4.5+)': {
                'url': 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_week.atom',
                'category': 'Natural Disasters',
                'priority': 'medium'
            },
            
            # ============ INVESTIGATIVE/INDEPENDENT MEDIA ============
            'Al Jazeera English': {
                'url': 'https://www.aljazeera.com/xml/rss/all.xml',
                'category': 'Political Conflicts',
                'priority': 'medium'
            },
            'BBC World': {
                'url': 'http://feeds.bbci.co.uk/news/world/rss.xml',
                'category': 'Mixed',
                'priority': 'medium'
            },
            'The Guardian - World': {
                'url': 'https://www.theguardian.com/world/rss',
                'category': 'Mixed',
                'priority': 'medium'
            },
            
            # ============ REGIONAL CRISIS COVERAGE ============
            'Radio Free Asia': {
                'url': 'https://www.rfa.org/english/RSS',
                'category': 'Human Rights Violations',
                'priority': 'high'  # Good for Uyghur, Myanmar, etc.
            },
            'Middle East Eye': {
                'url': 'https://www.middleeasteye.net/rss',
                'category': 'Political Conflicts',
                'priority': 'medium'
            },
        }
        
        # Underreported crisis zones to prioritize
        self.underreported_zones = [
            'uyghur', 'xinjiang', 'uighur',  # China
            'el salvador', 'nayib bukele',  # Mass incarceration
            'tigray', 'ethiopia',  # Ongoing conflict
            'yemen', 'houthi',  # Humanitarian crisis
            'rohingya', 'myanmar',  # Ethnic cleansing
            'darfur', 'sudan',  # Ongoing genocide
            'cameroon', 'anglophone',  # Separatist conflict
            'nagorno-karabakh', 'armenia', 'azerbaijan',
            'west papua', 'papua',  # Indonesian suppression
        ]
        
        # Systemic crisis keywords (not just breaking news)
        self.systemic_keywords = [
            'genocide', 'ethnic cleansing', 'mass detention', 
            'concentration camp', 'forced labor', 'slavery',
            'persecution', 'systematic', 'atrocities',
            'war crimes', 'crimes against humanity',
            'torture', 'disappearance', 'extrajudicial',
            'apartheid', 'occupation', 'blockade',
            'famine', 'starvation', 'malnutrition',
            'refugee crisis', 'internally displaced',
        ]
    
    def fetch_all_sources(self, max_per_source: int = 20, hours_back: int = 168) -> List[Dict]:
        """
        Fetch from all sources with intelligent prioritization
        
        Args:
            max_per_source: Max articles per source
            hours_back: Time window (default 7 days for systemic issues)
        
        Returns:
            List of article dictionaries with metadata
        """
        all_articles = []
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        logger.info(f"Fetching from {len(self.rss_feeds)} diverse sources (NGOs, human rights orgs, media)...")
        
        for source_name, source_info in self.rss_feeds.items():
            try:
                feed_url = source_info['url']
                category = source_info['category']
                priority = source_info['priority']
                
                logger.info(f"Fetching from {source_name}...")
                
                # Fetch with timeout
                response = requests.get(feed_url, timeout=15, headers={
                    'User-Agent': 'ARGUS-Crisis-Monitor/2.0'
                })
                
                if response.status_code == 200:
                    feed = feedparser.parse(response.content)
                    
                    source_articles = []
                    for entry in feed.entries[:max_per_source]:
                        article = self._parse_entry(entry, source_name, category, priority)
                        if article and self._is_crisis_relevant(article):
                            source_articles.append(article)
                    
                    all_articles.extend(source_articles)
                    logger.info(f"✓ {source_name}: {len(source_articles)} crisis articles")
                else:
                    logger.warning(f"HTTP {response.status_code} from {source_name}")
                    
            except Exception as e:
                logger.warning(f"Error fetching {source_name}: {e}")
                continue
        
        # Sort by priority and recency
        all_articles.sort(key=lambda x: (
            0 if x.get('priority') == 'high' else 1,
            -x.get('published_timestamp', 0)
        ))
        
        logger.info(f"✓ Total: {len(all_articles)} crisis articles from diverse sources")
        return all_articles
    
    def _parse_entry(self, entry, source_name: str, category: str, priority: str) -> Optional[Dict]:
        """Parse RSS entry into article format"""
        try:
            # Extract title
            title = entry.get('title', 'No title')
            
            # Extract content (try multiple fields)
            content = (
                entry.get('summary', '') or 
                entry.get('description', '') or
                entry.get('content', [{}])[0].get('value', '')
            )
            
            # Clean HTML from content
            if content:
                content = BeautifulSoup(content, 'html.parser').get_text()
                content = re.sub(r'\s+', ' ', content).strip()
            
            # Extract URL
            url = entry.get('link', '')
            
            # Extract date
            published = entry.get('published', entry.get('updated', ''))
            published_timestamp = 0
            try:
                if published:
                    import time
                    published_timestamp = time.mktime(entry.get('published_parsed', entry.get('updated_parsed', ())))
            except:
                pass
            
            return {
                'title': title,
                'content': content,
                'url': url,
                'source_name': source_name,
                'source_category': category,
                'priority': priority,
                'published_date': published,
                'published_timestamp': published_timestamp,
            }
        except Exception as e:
            logger.debug(f"Error parsing entry: {e}")
            return None
    
    def _is_crisis_relevant(self, article: Dict) -> bool:
        """
        Determine if article is crisis-relevant
        NO LLM - just keywords + source trust
        """
        text = f"{article['title']} {article['content']}".lower()
        
        # High-priority sources are pre-vetted (HRW, Amnesty, etc.)
        if article.get('priority') == 'high':
            return True
        
        # Check for underreported zones
        if any(zone in text for zone in self.underreported_zones):
            return True
        
        # Check for systemic crisis keywords
        if any(keyword in text for keyword in self.systemic_keywords):
            return True
        
        # Traditional crisis detection
        crisis_indicators = [
            'killed', 'deaths', 'dead', 'casualties',
            'emergency', 'disaster', 'crisis',
            'attack', 'bombing', 'conflict', 'war',
            'earthquake', 'flood', 'hurricane', 'fire',
            'refugee', 'displaced', 'evacuate',
            'outbreak', 'pandemic', 'epidemic'
        ]
        
        return any(indicator in text for indicator in crisis_indicators)


# Convenience function
def fetch_crisis_news(max_articles: int = 150, hours_back: int = 168) -> List[Dict]:
    """Fetch crisis news from enhanced sources"""
    fetcher = EnhancedCrisisFetcher()
    articles = fetcher.fetch_all_sources(max_per_source=15, hours_back=hours_back)
    return articles[:max_articles]
