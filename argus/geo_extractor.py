"""
Geographic Entity Extraction Module

Uses spaCy NER to extract geographic entities from text and geocode them
to latitude/longitude coordinates.
"""

import logging
import spacy
from typing import List, Dict, Tuple, Optional, Set
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time
import re
import os
from dotenv import load_dotenv
import requests
from urllib.parse import quote
import ssl
import certifi
from .config import SPACY_MODEL, GEOCODING_TIMEOUT, MAX_LOCATIONS_PER_ARTICLE

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeographicExtractor:
    """Extracts and geocodes geographic entities from text"""
    
    def __init__(self, spacy_model: str = None):
        """
        Initialize the geographic extractor
        
        Args:
            spacy_model: Name of the spaCy model to use
        """
        self.model_name = spacy_model or SPACY_MODEL
        self.nlp = None
        
        # Create SSL context using certifi certificates
        ctx = ssl.create_default_context(cafile=certifi.where())
        self.geocoder = Nominatim(
            user_agent="argus-crisis-monitor", 
            timeout=GEOCODING_TIMEOUT,
            ssl_context=ctx
        )
        
        # Load .env (if present) for API keys
        try:
            load_dotenv()
        except Exception:
            pass
        self.mapbox_token = os.getenv("MAPBOX_TOKEN")
        self.mapbox_endpoint = "https://api.mapbox.com/geocoding/v5/mapbox.places/"
        
        # Cache for geocoding results to avoid repeated API calls
        self.geocoding_cache = {}
        
        logger.info(f"Initializing GeographicExtractor with model: {self.model_name}")
        self._load_model()
    
    def _load_model(self):
        """Load the spaCy NLP model"""
        try:
            logger.info("Loading spaCy model...")
            self.nlp = spacy.load(self.model_name)
            logger.info("spaCy model loaded successfully")
            
        except OSError as e:
            logger.error(f"Error loading spaCy model '{self.model_name}': {e}")
            logger.error("Please install the model with: python -m spacy download en_core_web_sm")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading spaCy model: {e}")
            raise
    
    def extract_locations(self, text: str) -> List[Dict]:
        """
        Extract geographic entities from text using NER
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of location dictionaries with entity info
        """
        if not text or not self.nlp:
            return []
        
        try:
            # Process text with spaCy
            doc = self.nlp(text)
            
            locations = []
            seen_locations = set()  # Avoid duplicates
            
            for ent in doc.ents:
                # Look for geographic entities
                if ent.label_ in ['GPE', 'LOC', 'GEOPOLITICAL']:  # Geographic/Political entities
                    location_text = ent.text.strip()
                    
                    # Clean and validate location text
                    cleaned_location = self._clean_location_text(location_text)
                    
                    if (cleaned_location and 
                        cleaned_location.lower() not in seen_locations and
                        len(cleaned_location) > 1):
                        
                        location_info = {
                            'text': cleaned_location,
                            'original_text': location_text,
                            'start_char': ent.start_char,
                            'end_char': ent.end_char,
                            'label': ent.label_,
                            'confidence': getattr(ent, 'score', 1.0)  # Default confidence
                        }
                        
                        locations.append(location_info)
                        seen_locations.add(cleaned_location.lower())
            
            # Limit number of locations per article
            if len(locations) > MAX_LOCATIONS_PER_ARTICLE:
                locations = locations[:MAX_LOCATIONS_PER_ARTICLE]
            
            logger.debug(f"Extracted {len(locations)} locations from text")
            return locations
            
        except Exception as e:
            logger.error(f"Error extracting locations: {e}")
            return []
    
    def _clean_location_text(self, location_text: str) -> Optional[str]:
        """
        Clean and validate location text
        
        Args:
            location_text: Raw location text from NER
            
        Returns:
            Cleaned location text or None if invalid
        """
        if not location_text:
            return None
        
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', location_text.strip())
        
        # Remove common prefixes/suffixes that aren't part of location names
        prefixes_to_remove = ['the ', 'The ']
        for prefix in prefixes_to_remove:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):]
        
        # Filter out obviously non-geographic terms
        non_geographic_terms = {
            'today', 'yesterday', 'tomorrow', 'monday', 'tuesday', 'wednesday',
            'thursday', 'friday', 'saturday', 'sunday', 'january', 'february',
            'march', 'april', 'may', 'june', 'july', 'august', 'september',
            'october', 'november', 'december', 'am', 'pm', 'news', 'report',
            'article', 'story', 'breaking', 'update'
        }
        
        if cleaned.lower() in non_geographic_terms:
            return None
        
        # Must be at least 2 characters and contain letters
        if len(cleaned) < 2 or not re.search(r'[a-zA-Z]', cleaned):
            return None
        
        return cleaned
    
    def geocode_location(self, location_text: str) -> Optional[Dict]:
        """
        Geocode a location to get latitude/longitude coordinates
        
        Args:
            location_text: Location name to geocode
            
        Returns:
            Dictionary with geocoding results or None if failed
        """
        # Check cache first
        cache_key = location_text.lower().strip()
        if cache_key in self.geocoding_cache:
            return self.geocoding_cache[cache_key]
        
        # Known crisis zones that should override geocoding (to avoid ambiguous matches)
        known_crisis_zones = {
            'gaza': {'lat': 31.3547, 'lon': 34.3088, 'name': 'Gaza Strip, Palestine'},
            'gaza strip': {'lat': 31.3547, 'lon': 34.3088, 'name': 'Gaza Strip, Palestine'},
            'west bank': {'lat': 31.9522, 'lon': 35.2332, 'name': 'West Bank, Palestine'},
            'palestine': {'lat': 31.9522, 'lon': 35.2332, 'name': 'Palestine'},
            'syria': {'lat': 33.5138, 'lon': 36.2765, 'name': 'Syria'},
            'yemen': {'lat': 15.5527, 'lon': 48.5164, 'name': 'Yemen'},
            'afghanistan': {'lat': 33.9391, 'lon': 67.7100, 'name': 'Afghanistan'},
            'ukraine': {'lat': 50.4501, 'lon': 30.5234, 'name': 'Ukraine'},
            'sudan': {'lat': 15.5007, 'lon': 32.5599, 'name': 'Sudan'},
            'south sudan': {'lat': 6.8770, 'lon': 31.3070, 'name': 'South Sudan'},
            'somalia': {'lat': 5.1521, 'lon': 46.1996, 'name': 'Somalia'},
        }
        
        # Check if this is a known crisis zone
        location_lower = location_text.lower().strip()
        if location_lower in known_crisis_zones:
            zone = known_crisis_zones[location_lower]
            result = {
                'query': location_text,
                'found_name': zone['name'],
                'latitude': zone['lat'],
                'longitude': zone['lon'],
                'raw_data': {'source': 'known_crisis_zone'}
            }
            self.geocoding_cache[cache_key] = result
            return result
        
        try:
            # Add rate limiting to avoid overwhelming the geocoding service
            time.sleep(0.1)

            # Primary: Nominatim (OSM) - add context to improve accuracy
            location = None
            try:
                # Try with original text first
                location = self.geocoder.geocode(location_text)
            except (GeocoderTimedOut, GeocoderServiceError) as e:
                logger.warning(f"Geocoding service error for '{location_text}': {e}")
            except Exception as e:
                logger.warning(f"Unexpected geocoding error for '{location_text}': {e}")

            if location:
                result = {
                    'query': location_text,
                    'found_name': location.address,
                    'latitude': location.latitude,
                    'longitude': location.longitude,
                    'raw_data': location.raw
                }
                # Cache and return
                self.geocoding_cache[cache_key] = result
                return result

            # Fallback: Mapbox Geocoding API (requires MAPBOX_TOKEN)
            if self.mapbox_token:
                try:
                    q = quote(location_text)
                    url = f"{self.mapbox_endpoint}{q}.json"
                    params = {
                        'access_token': self.mapbox_token,
                        'limit': 1,
                        'language': 'en'
                    }
                    resp = requests.get(url, params=params, timeout=10)
                    if resp.ok:
                        data = resp.json()
                        features = data.get('features', [])
                        if features:
                            center = features[0].get('center', [])
                            place_name = features[0].get('place_name', location_text)
                            if len(center) == 2:
                                result = {
                                    'query': location_text,
                                    'found_name': place_name,
                                    'latitude': center[1],
                                    'longitude': center[0],
                                    'raw_data': features[0]
                                }
                                self.geocoding_cache[cache_key] = result
                                return result
                except Exception as e:
                    logger.warning(f"Mapbox fallback failed for '{location_text}': {e}")

            # Cache negative results too
            self.geocoding_cache[cache_key] = None
            return None

        except Exception as e:
            logger.error(f"Unexpected geocoding error for '{location_text}': {e}")
            return None
    
    def process_article_locations(self, article: Dict) -> Dict:
        """
        Extract and geocode all locations from an article
        
        Args:
            article: Article dictionary with text content
            
        Returns:
            Article dictionary enhanced with location data
        """
        try:
            # Combine title and content for location extraction
            title = article.get('title', '')
            content = article.get('content', '')
            full_text = f"{title}. {content}".strip()
            
            # Extract locations using NER
            extracted_locations = self.extract_locations(full_text)
            
            # Geocode each location
            geocoded_locations = []
            for location_info in extracted_locations:
                geocoded = self.geocode_location(location_info['text'])
                
                if geocoded:
                    # Combine NER info with geocoding results
                    enhanced_location = {
                        **location_info,
                        **geocoded,
                        'geocoded': True
                    }
                else:
                    enhanced_location = {
                        **location_info,
                        'geocoded': False,
                        'latitude': None,
                        'longitude': None
                    }
                
                geocoded_locations.append(enhanced_location)
            
            # Add location data to article
            enhanced_article = article.copy()
            enhanced_article['locations'] = geocoded_locations
            enhanced_article['location_count'] = len(geocoded_locations)
            enhanced_article['geocoded_count'] = sum(1 for loc in geocoded_locations if loc['geocoded'])
            
            return enhanced_article
            
        except Exception as e:
            logger.error(f"Error processing article locations: {e}")
            # Return original article if processing fails
            enhanced_article = article.copy()
            enhanced_article['locations'] = []
            enhanced_article['location_count'] = 0
            enhanced_article['geocoded_count'] = 0
            return enhanced_article
    
    def process_batch_locations(self, articles: List[Dict]) -> List[Dict]:
        """
        Process locations for multiple articles
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            List of articles enhanced with location data
        """
        enhanced_articles = []
        total_articles = len(articles)
        
        logger.info(f"Processing locations for {total_articles} articles")
        
        for i, article in enumerate(articles):
            enhanced_article = self.process_article_locations(article)
            enhanced_articles.append(enhanced_article)
            
            # Log progress
            if (i + 1) % 10 == 0 or i + 1 == total_articles:
                logger.info(f"Processed locations for {i + 1}/{total_articles} articles")
        
        return enhanced_articles
    
    def get_location_statistics(self, articles: List[Dict]) -> Dict:
        """
        Generate statistics about location extraction
        
        Args:
            articles: List of articles with location data
            
        Returns:
            Dictionary with location statistics
        """
        stats = {
            'total_articles': len(articles),
            'articles_with_locations': 0,
            'total_locations_extracted': 0,
            'total_locations_geocoded': 0,
            'unique_locations': set(),
            'geocoding_success_rate': 0.0,
            'top_locations': {}
        }
        
        for article in articles:
            locations = article.get('locations', [])
            
            if locations:
                stats['articles_with_locations'] += 1
                stats['total_locations_extracted'] += len(locations)
                
                for location in locations:
                    if location.get('geocoded', False):
                        stats['total_locations_geocoded'] += 1
                    
                    location_name = location.get('text', '').lower()
                    if location_name:
                        stats['unique_locations'].add(location_name)
                        stats['top_locations'][location_name] = stats['top_locations'].get(location_name, 0) + 1
        
        # Calculate success rate
        if stats['total_locations_extracted'] > 0:
            stats['geocoding_success_rate'] = stats['total_locations_geocoded'] / stats['total_locations_extracted']
        
        # Convert set to count
        stats['unique_locations_count'] = len(stats['unique_locations'])
        del stats['unique_locations']  # Remove set for JSON serialization
        
        # Sort top locations
        stats['top_locations'] = dict(sorted(stats['top_locations'].items(), 
                                           key=lambda x: x[1], reverse=True)[:10])
        
        return stats


# Singleton instance for model reuse
_extractor_instance = None

def get_extractor_instance(spacy_model: str = None) -> GeographicExtractor:
    """Get or create singleton extractor instance to avoid reloading spaCy model"""
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = GeographicExtractor(spacy_model)
    return _extractor_instance

def extract_article_locations(articles: List[Dict]) -> List[Dict]:
    """
    Convenience function to extract locations from articles
    
    Args:
        articles: List of article dictionaries
        
    Returns:
        List of articles enhanced with location data
    """
    extractor = get_extractor_instance()
    return extractor.process_batch_locations(articles)
