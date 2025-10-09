"""
Interactive Mapping Module

Creates interactive world maps using Folium to visualize global crises
with color-coded markers and detailed popups.
"""

import logging
import folium
from folium import plugins
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import os
from .config import MAP_CONFIG, CRISIS_COLORS, OUTPUT_MAP_FILE

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CrisisMapper:
    """Creates interactive maps for crisis visualization"""
    
    def __init__(self, map_config: Dict = None):
        """
        Initialize the crisis mapper
        
        Args:
            map_config: Optional custom map configuration
        """
        self.config = map_config or MAP_CONFIG
        self.crisis_colors = CRISIS_COLORS
        
    def create_base_map(self) -> folium.Map:
        """
        Create a base world map
        
        Returns:
            Folium Map object
        """
        # Create base map centered on world
        # Use tiles=None and add a TileLayer with no_wrap to prevent world repeating at extreme zooms
        world_map = folium.Map(
            location=self.config['default_location'],
            zoom_start=self.config['default_zoom'],
            tiles=None,
            min_zoom=2,
            max_bounds=True
        )
        folium.TileLayer(
            tiles=self.config['tile_style'],
            name="Base Map",
            control=False,
            no_wrap=True,
            attr="OpenStreetMap"
        ).add_to(world_map)
        
        # Add fullscreen button
        plugins.Fullscreen().add_to(world_map)
        
        # Add measure control for distance measurement
        plugins.MeasureControl().add_to(world_map)
        
        return world_map
    
    def aggregate_crises(self, crisis_data: List[Dict]) -> List[Dict]:
        """
        Aggregate multiple articles about the same crisis into single markers
        
        Groups articles by:
        - Location (rounded coordinates)
        - Category (crisis type)
        
        Args:
            crisis_data: List of individual crisis articles
            
        Returns:
            List of aggregated crisis objects with multiple articles per location
        """
        from collections import defaultdict
        
        # Group articles by location + category
        crisis_groups = defaultdict(list)
        
        for crisis_item in crisis_data:
            article = crisis_item.get('article', {})
            category = crisis_item.get('predicted_category', 'Other')
            locations = article.get('locations', [])
            
            # Get first valid geocoded location
            for loc in locations:
                if loc.get('geocoded') and 'latitude' in loc and 'longitude' in loc:
                    lat = loc['latitude']
                    lon = loc['longitude']
                    
                    # Round coordinates to group nearby locations (0.5 degree ~= 55km)
                    lat_rounded = round(lat * 2) / 2  # Round to nearest 0.5
                    lon_rounded = round(lon * 2) / 2
                    
                    # Create unique key for this crisis location
                    key = (lat_rounded, lon_rounded, category)
                    crisis_groups[key].append({
                        'article': article,
                        'crisis_item': crisis_item,
                        'exact_lat': lat,
                        'exact_lon': lon,
                        # Use the geocoded display name key returned by our extractor
                        # geo_extractor.geocode_location() sets 'found_name' (or we fallback to raw 'text')
                        'location_name': loc.get('found_name', loc.get('text', 'Unknown Location'))
                    })
                    break  # Only use first location per article
        
        # Convert groups to aggregated crisis objects
        aggregated_crises = []
        for (lat, lon, category), articles in crisis_groups.items():
            if len(articles) == 0:
                continue
                
            # Use average of exact coordinates
            avg_lat = sum(a['exact_lat'] for a in articles) / len(articles)
            avg_lon = sum(a['exact_lon'] for a in articles) / len(articles)
            
            # Use most common location name
            location_names = [a['location_name'] for a in articles]
            primary_location = max(set(location_names), key=location_names.count)
            
            aggregated_crises.append({
                'lat': avg_lat,
                'lon': avg_lon,
                'category': category,
                'location_name': primary_location,
                'article_count': len(articles),
                'articles': articles,
                'dates': [a['article'].get('publish_date') for a in articles if a['article'].get('publish_date')]
            })
        
        logger.info(f"Aggregated {len(crisis_data)} articles into {len(aggregated_crises)} crisis locations")
        return aggregated_crises
    
    def generate_crisis_summary(self, aggregated_crisis: Dict) -> str:
        """
        Generate a concise summary of an aggregated crisis
        
        Uses article titles and content to create a brief description
        without requiring external LLM API
        
        Args:
            aggregated_crisis: Aggregated crisis object with multiple articles
            
        Returns:
            HTML string with crisis summary
        """
        category = aggregated_crisis['category']
        location = aggregated_crisis['location_name']
        article_count = aggregated_crisis['article_count']
        articles = aggregated_crisis['articles']
        
        # Extract key information from articles
        titles = []
        sources = set()
        dates = []
        
        for article_data in articles[:5]:  # Use top 5 articles
            article = article_data['article']
            title = article.get('title', '')
            source = article.get('source', 'Unknown')
            date = article.get('publish_date', '')
            
            if title:
                titles.append(title)
            sources.add(source)
            if date:
                dates.append(date)
        
        # Get most recent date
        recent_date = max(dates) if dates else 'Recent'
        if recent_date and recent_date != 'Recent':
            try:
                date_obj = datetime.fromisoformat(recent_date.replace('Z', '+00:00'))
                recent_date = date_obj.strftime('%B %d, %Y')
            except:
                recent_date = 'Recent'
        
        # Create summary from common words in titles
        all_titles_text = ' '.join(titles).lower()
        
        # Simple extractive summary: use the most informative title
        summary_title = titles[0] if titles else f"{category} in {location}"
        
        return {
            'summary_title': summary_title,
            'category': category,
            'location': location,
            'article_count': article_count,
            'sources': list(sources),
            'recent_date': recent_date
        }
    
    def add_crisis_markers(self, world_map: folium.Map, 
                          crisis_data: List[Dict]) -> folium.Map:
        """
        Add aggregated crisis markers to the map
        
        Args:
            world_map: Base Folium map
            crisis_data: List of crisis articles with location and classification data
            
        Returns:
            Map with crisis markers added
        """
        # Step 1: Aggregate articles into crisis locations
        aggregated_crises = self.aggregate_crises(crisis_data)
        
        # Create feature groups for each category (not clusters, for cleaner control)
        category_groups = {}
        for category in self.crisis_colors.keys():
            category_groups[category] = folium.FeatureGroup(name=category, show=True)
        category_groups["Other"] = folium.FeatureGroup(name="Other", show=False)
        
        # Step 2: Create one marker per aggregated crisis
        for crisis in aggregated_crises:
            category = crisis['category']
            lat = crisis['lat']
            lon = crisis['lon']
            
            # Generate summary
            summary_data = self.generate_crisis_summary(crisis)
            
            # Create popup HTML
            popup_html = self._create_aggregated_popup(crisis, summary_data)
            
            # Create marker
            color = self.crisis_colors.get(category, '#666666')
            marker = folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=400),
                tooltip=f"{category}: {summary_data['summary_title'][:60]}...",
                icon=folium.Icon(
                    color=self._get_folium_color(color),
                    icon='exclamation-triangle',
                    prefix='fa'
                )
            )
            
            # Add to appropriate group
            group = category_groups.get(category, category_groups["Other"])
            marker.add_to(group)
        
        # Add all groups to map
        for group in category_groups.values():
            group.add_to(world_map)
        
        # Add layer control for toggling categories
        folium.LayerControl(collapsed=False).add_to(world_map)
        
        logger.info(f"Added {len(aggregated_crises)} aggregated crisis markers to map")
        return world_map
    
    def _create_aggregated_popup(self, crisis: Dict, summary_data: Dict) -> str:
        """
        Create rich HTML popup for aggregated crisis marker
        
        Args:
            crisis: Aggregated crisis object
            summary_data: Summary data generated for this crisis
            
        Returns:
            HTML string for popup
        """
        category = summary_data['category']
        location = summary_data['location']
        article_count = summary_data['article_count']
        sources = summary_data['sources']
        recent_date = summary_data['recent_date']
        summary_title = summary_data['summary_title']
        
        # Build article links (show up to 5)
        article_links = []
        for i, article_data in enumerate(crisis['articles'][:5]):
            article = article_data['article']
            title = article.get('title', 'Untitled')
            url = article.get('url', '#')
            source = article.get('source', 'Unknown')
            
            article_links.append(f"""
                <div style="margin: 5px 0; padding: 5px; background: #f9f9f9; border-left: 2px solid #ddd;">
                    <a href="{url}" target="_blank" style="color: #0066cc; text-decoration: none; font-size: 11px;">
                        {title[:80]}{"..." if len(title) > 80 else ""}
                    </a>
                    <div style="font-size: 9px; color: #666; margin-top: 2px;">{source}</div>
                </div>
            """)
        
        more_articles = ""
        if article_count > 5:
            more_articles = f"<div style='font-size: 10px; color: #888; margin-top: 5px;'>+ {article_count - 5} more articles</div>"
        
        popup_html = f"""
        <div style="font-family: 'Computer Modern Serif', Georgia, serif; min-width: 300px;">
            <div style="background: {self.crisis_colors.get(category, '#666')}; color: white; padding: 8px; margin: -10px -10px 10px -10px;">
                <div style="font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.9;">
                    {category}
                </div>
                <div style="font-size: 13px; font-weight: bold; margin-top: 3px;">
                    {location}
                </div>
            </div>
            
            <div style="margin: 10px 0; padding: 8px; background: #f5f5f5; border-left: 3px solid {self.crisis_colors.get(category, '#666')};">
                <div style="font-size: 12px; line-height: 1.4; color: #333;">
                    {summary_title}
                </div>
            </div>
            
            <div style="margin: 10px 0; font-size: 10px; color: #666;">
                <strong>{article_count}</strong> reports from <strong>{len(sources)}</strong> sources
                <br>Last updated: {recent_date}
            </div>
            
            <div style="border-top: 0.5px solid #ddd; padding-top: 8px; margin-top: 8px;">
                <div style="font-size: 11px; font-weight: bold; margin-bottom: 5px; color: #333;">
                    Related Articles:
                </div>
                {"".join(article_links)}
                {more_articles}
            </div>
        </div>
        """
        
        return popup_html
    
    def _get_folium_color(self, color: str) -> str:
        """
        Convert hex color to Folium color name, or return if already a Folium color
        
        Args:
            color: Hex color code or Folium color name
            
        Returns:
            Folium color name (red, blue, green, etc.)
        """
        # Valid Folium color names
        valid_folium_colors = {
            'red', 'darkred', 'lightred', 'orange', 'beige', 'green', 
            'darkgreen', 'lightgreen', 'blue', 'darkblue', 'lightblue', 
            'purple', 'darkpurple', 'pink', 'cadetblue', 'white', 'gray', 
            'lightgray', 'black'
        }
        
        # If it's already a valid Folium color, return as-is
        if color.lower() in valid_folium_colors:
            return color.lower()
        
        # Map hex colors to Folium's limited color set
        color_map = {
            '#8B0000': 'darkred',
            '#DC143C': 'red',
            '#FF6B35': 'orange',
            '#FF8C00': 'orange',
            '#9370DB': 'purple',
            '#4682B4': 'blue',
            '#228B22': 'green'
        }
        return color_map.get(color, 'gray')
    
    def _get_fallback_location(self, article: Dict, category: str) -> Optional[Tuple[float, float, str]]:
        """
        Get fallback location for articles without perfect geocoding
        
        Args:
            article: Article data
            category: Crisis category
            
        Returns:
            Tuple of (lat, lon, location_name) or None
        """
        title = article.get('title', '').lower()
        content = article.get('content', '').lower()
        source = article.get('source', '').lower()
        text = f"{title} {content}".lower()
        
        # Geographic keyword mapping (expanded for Americas + key cities)
        location_keywords = {
            'china': (39.9042, 116.4074, 'China'),
            'chinese': (39.9042, 116.4074, 'China'),
            'beijing': (39.9042, 116.4074, 'Beijing, China'),
            # United States & major US cities/states
            'united states': (39.8283, -98.5795, 'United States'),
            'usa': (39.8283, -98.5795, 'United States'),
            'u.s.': (39.8283, -98.5795, 'United States'),
            'us ': (39.8283, -98.5795, 'United States'),
            'america': (39.8283, -98.5795, 'United States'),
            'washington': (38.9072, -77.0369, 'Washington, DC, USA'),
            'new york': (40.7128, -74.0060, 'New York, USA'),
            'los angeles': (34.0522, -118.2437, 'Los Angeles, USA'),
            'san francisco': (37.7749, -122.4194, 'San Francisco, USA'),
            'chicago': (41.8781, -87.6298, 'Chicago, USA'),
            'miami': (25.7617, -80.1918, 'Miami, USA'),
            'seattle': (47.6062, -122.3321, 'Seattle, USA'),
            'boston': (42.3601, -71.0589, 'Boston, USA'),
            'atlanta': (33.7490, -84.3880, 'Atlanta, USA'),
            'houston': (29.7604, -95.3698, 'Houston, USA'),
            'dallas': (32.7767, -96.7970, 'Dallas, USA'),
            'austin': (30.2672, -97.7431, 'Austin, USA'),
            'phoenix': (33.4484, -112.0740, 'Phoenix, USA'),
            'denver': (39.7392, -104.9903, 'Denver, USA'),
            'philadelphia': (39.9526, -75.1652, 'Philadelphia, USA'),
            'nashville': (36.1627, -86.7816, 'Nashville, USA'),
            'san diego': (32.7157, -117.1611, 'San Diego, USA'),
            'orlando': (28.5384, -81.3789, 'Orlando, USA'),
            'minneapolis': (44.9778, -93.2650, 'Minneapolis, USA'),
            # Canada & key cities
            'canada': (56.1304, -106.3468, 'Canada'),
            'toronto': (43.6532, -79.3832, 'Toronto, Canada'),
            'vancouver': (49.2827, -123.1207, 'Vancouver, Canada'),
            'montreal': (45.5019, -73.5674, 'Montreal, Canada'),
            'ottawa': (45.4215, -75.6972, 'Ottawa, Canada'),
            # Mexico & LATAM
            'mexico': (23.6345, -102.5528, 'Mexico'),
            'mexico city': (19.4326, -99.1332, 'Mexico City, Mexico'),
            'brazil': ( -14.2350, -51.9253, 'Brazil'),
            'brasilia': (-15.8267, -47.9218, 'Brasilia, Brazil'),
            'sao paulo': (-23.5505, -46.6333, 'Sao Paulo, Brazil'),
            'rio de janeiro': (-22.9068, -43.1729, 'Rio de Janeiro, Brazil'),
            'argentina': (-34.6037, -58.3816, 'Argentina'),
            'buenos aires': (-34.6037, -58.3816, 'Buenos Aires, Argentina'),
            'chile': (-33.4489, -70.6693, 'Chile'),
            'santiago': (-33.4489, -70.6693, 'Santiago, Chile'),
            'colombia': (4.7110, -74.0721, 'Colombia'),
            'bogota': (4.7110, -74.0721, 'Bogotá, Colombia'),
            'peru': (-12.0464, -77.0428, 'Peru'),
            'lima': (-12.0464, -77.0428, 'Lima, Peru'),
            'venezuela': (10.4806, -66.9036, 'Venezuela'),
            'caracas': (10.4806, -66.9036, 'Caracas, Venezuela'),
            'haiti': (18.5944, -72.3074, 'Haiti'),
            'port-au-prince': (18.5944, -72.3074, 'Port-au-Prince, Haiti'),
            'cuba': (23.1136, -82.3666, 'Cuba'),
            'havana': (23.1136, -82.3666, 'Havana, Cuba'),
            'dominican republic': (18.4861, -69.9312, 'Dominican Republic'),
            'santo domingo': (18.4861, -69.9312, 'Santo Domingo, Dominican Republic'),
            'puerto rico': (18.4655, -66.1057, 'Puerto Rico'),
            'san juan': (18.4655, -66.1057, 'San Juan, Puerto Rico'),
            'guatemala': (14.6349, -90.5069, 'Guatemala'),
            'guatemala city': (14.6349, -90.5069, 'Guatemala City, Guatemala'),
            'ecuador': (-0.1807, -78.4678, 'Ecuador'),
            'quito': (-0.1807, -78.4678, 'Quito, Ecuador'),
            'bolivia': (-16.4897, -68.1193, 'Bolivia'),
            'la paz': (-16.4897, -68.1193, 'La Paz, Bolivia'),
            'paraguay': (-25.2637, -57.5759, 'Paraguay'),
            'asuncion': (-25.2637, -57.5759, 'Asunción, Paraguay'),
            'uruguay': (-34.9011, -56.1645, 'Uruguay'),
            'montevideo': (-34.9011, -56.1645, 'Montevideo, Uruguay'),
            'turkey': (39.9334, 32.8597, 'Turkey'),
            'turkish': (39.9334, 32.8597, 'Turkey'),
            'ankara': (39.9334, 32.8597, 'Ankara, Turkey'),
            'istanbul': (41.0082, 28.9784, 'Istanbul, Turkey'),
            'ukraine': (50.4501, 30.5234, 'Ukraine'),
            'ukrainian': (50.4501, 30.5234, 'Ukraine'),
            'russia': (55.7558, 37.6176, 'Russia'),
            'russian': (55.7558, 37.6176, 'Russia'),
            'israel': (31.7683, 35.2137, 'Israel'),
            'gaza': (31.3547, 34.3088, 'Gaza'),
            'palestine': (31.9522, 35.2332, 'Palestine'),
            'syria': (33.5138, 36.2765, 'Syria'),
            'lebanon': (33.8547, 35.8623, 'Lebanon'),
            'iran': (35.6892, 51.3890, 'Iran'),
            'iraq': (33.2232, 43.6793, 'Iraq'),
            'afghanistan': (33.9391, 67.7100, 'Afghanistan'),
            'pakistan': (30.3753, 69.3451, 'Pakistan'),
            'india': (20.5937, 78.9629, 'India'),
            'japan': (36.2048, 138.2529, 'Japan'),
            'south korea': (35.9078, 127.7669, 'South Korea'),
            'north korea': (40.3399, 127.5101, 'North Korea'),
        }
        
        # Check for geographic keywords
        for keyword, (lat, lon, name) in location_keywords.items():
            if keyword in text:
                return (lat, lon, name)
        
        # Category-based fallbacks (bias to US for common US hazards)
        if 'cyber' in text or 'malware' in text or 'hack' in text:
            return (37.7749, -122.4194, 'Global Cyber Threat')  # San Francisco (tech hub)
        
        if 'economic' in text or 'recession' in text or 'inflation' in text:
            return (40.7128, -74.0060, 'Global Economic Impact')  # New York (financial hub)
        
        if 'climate' in text or 'environment' in text:
            return (0, 0, 'Global Environmental Issue')  # Equator
        
        if 'wildfire' in text or 'brush fire' in text:
            return (36.7783, -119.4179, 'Wildfire (USA)')  # California centroid
        if 'hurricane' in text or 'tropical storm' in text:
            return (25.7617, -80.1918, 'Hurricane Event (USA)')  # Miami area
        if 'tornado' in text:
            return (35.4676, -97.5164, 'Tornado Alley (USA)')  # Oklahoma City
        
        # Source-based fallbacks
        if any(s in source for s in ['cnn', 'cbsnews', 'nbcnews', 'apnews', 'foxnews', 'abcnews', 'nytimes', 'washingtonpost', 'usatoday', 'latimes', 'wsj']):
            return (39.8283, -98.5795, 'United States (News Source)')  # US centroid
        elif 'bbc' in source:
            return (51.5074, -0.1278, 'BBC World Report')  # London
        elif 'reuters' in source:
            return (51.5074, -0.1278, 'Reuters Global Report')  # London
        
        # Default fallback for unlocated crises
        return (20, 0, 'Global Crisis Event')
    
    def _sanitize_dict(self, data: Dict) -> Dict:
        """Remove non-JSON-serializable data from dictionaries"""
        if not isinstance(data, dict):
            return data
        
        sanitized = {}
        for key, value in data.items():
            # Ensure keys are strings
            str_key = str(key) if not isinstance(key, str) else key
            
            # Skip raw_data to avoid complex nested structures
            if str_key == 'raw_data':
                continue
                
            # Handle nested dicts
            if isinstance(value, dict):
                sanitized[str_key] = self._sanitize_dict(value)
            elif isinstance(value, (list, tuple)):
                sanitized[str_key] = [self._sanitize_dict(v) if isinstance(v, dict) else v for v in value]
            else:
                sanitized[str_key] = value
        
        return sanitized
    
    def _create_crisis_marker(self, lat: float, lon: float, article: Dict,
                             category: str, confidence: float, location: Dict) -> folium.Marker:
        """
        Create a single crisis marker
        
        Args:
            lat: Latitude
            lon: Longitude
            article: Article data
            category: Crisis category
            confidence: Classification confidence
            location: Location data
            
        Returns:
            Folium Marker object
        """
        # Get color for crisis category
        color = self.crisis_colors.get(category, 'gray')
        
        # Sanitize location data to avoid issues with Folium rendering
        clean_location = self._sanitize_dict(location)
        
        # Create popup content
        popup_html = self._create_popup_content(article, category, confidence, clean_location)
        
        # Create marker with custom icon (use only simple types to avoid Folium serialization issues)
        marker = folium.Marker(
            location=[float(lat), float(lon)],
            popup=folium.Popup(popup_html, max_width=400),
            tooltip=str(f"{category}: {article.get('title', 'No title')[:50]}..."),
            icon=folium.Icon(
                color=str(color),
                icon='exclamation-triangle',
                prefix='fa'
            )
        )
        
        return marker
    
    def _create_popup_content(self, article: Dict, category: str, 
                             confidence: float, location: Dict) -> str:
        """
        Create HTML content for marker popup
        
        Args:
            article: Article data
            category: Crisis category
            confidence: Classification confidence
            location: Location data
            
        Returns:
            HTML string for popup
        """
        title = str(article.get('title', 'No title'))
        source = str(article.get('source_name', article.get('source', 'Unknown source')))
        url = str(article.get('url', '#'))
        published_date = article.get('published_date', 'Unknown date')
        # Ensure published_date is a string
        if not isinstance(published_date, str):
            published_date = str(published_date) if published_date is not None else 'Unknown date'
        location_name = location.get('found_name', location.get('text', 'Unknown location'))
        # Ensure location_name is a string
        if not isinstance(location_name, str):
            location_name = str(location_name) if location_name is not None else 'Unknown location'
        
        # Check if using fallback location
        is_fallback = location.get('fallback', False)
        location_note = " (estimated)" if is_fallback else ""
        
        # Truncate content for popup
        content = article.get('content', '')
        if len(content) > 200:
            content = content[:200] + "..."
        
        # Create HTML popup (clean, no "REAL DATA" banner)
        popup_html = f"""
        <div style="width: 350px;">
            <h4 style="color: {self.crisis_colors.get(category, 'black')}; margin-bottom: 10px;">
                {category}
            </h4>
            <h5 style="margin-bottom: 8px;">{title}</h5>
            
            <div style="margin-bottom: 8px;">
                <strong>Location:</strong> {location_name}{location_note}<br>
                <strong>Source:</strong> {source}<br>
                <strong>Date:</strong> {published_date}<br>
                <strong>Confidence:</strong> {confidence:.2f}
            </div>
            
            <div style="margin-bottom: 10px; font-size: 12px; color: #666;">
                {content}
            </div>
            
            <a href="{url}" target="_blank" style="color: #007cba; text-decoration: none;">
                📰 Read Article
            </a>
        </div>
        """
        
        return popup_html
    
    def add_crisis_heatmap(self, world_map: folium.Map, 
                          crisis_data: List[Dict]) -> folium.Map:
        """
        Add a heatmap layer showing crisis density
        
        Args:
            world_map: Base Folium map
            crisis_data: List of crisis articles with location data
            
        Returns:
            Map with heatmap layer added
        """
        # Collect all geocoded locations
        heat_data = []
        
        for crisis_item in crisis_data:
            article = crisis_item.get('article', {})
            confidence = crisis_item.get('confidence', 0.0)
            locations = article.get('locations', [])
            
            for location in locations:
                if location.get('geocoded', False):
                    lat = location.get('latitude')
                    lon = location.get('longitude')
                    
                    if lat is not None and lon is not None:
                        # Weight by confidence score
                        weight = max(confidence, 0.1)  # Minimum weight
                        heat_data.append([lat, lon, weight])
        
        if heat_data:
            # Create heatmap layer (ensure all values are native Python types)
            clean_heat_data = [[float(lat), float(lon), float(weight)] for lat, lon, weight in heat_data]
            heatmap = plugins.HeatMap(
                clean_heat_data,
                name="Crisis Density Heatmap",
                min_opacity=0.2,
                max_zoom=18,
                radius=15,
                blur=10,
                gradient={
                    '0.2': 'blue',
                    '0.4': 'lime', 
                    '0.6': 'orange',
                    '0.8': 'red',
                    '1.0': 'darkred'
                }
            )
            
            heatmap.add_to(world_map)
            logger.info(f"Added heatmap with {len(heat_data)} data points")
        
        return world_map
    
    def add_statistics_panel(self, world_map: folium.Map, 
                           crisis_data: List[Dict]) -> folium.Map:
        """
        Add a statistics panel to the map
        
        Args:
            world_map: Base Folium map
            crisis_data: List of crisis articles
            
        Returns:
            Map with statistics panel added
        """
        # Calculate statistics
        stats = self._calculate_crisis_statistics(crisis_data)
        
        # Create HTML for statistics panel
        stats_html = self._create_statistics_html(stats)
        
        # Add as a custom control
        stats_control = folium.Element(stats_html)
        world_map.get_root().html.add_child(stats_control)
        
        return world_map
    
    def _calculate_crisis_statistics(self, crisis_data: List[Dict]) -> Dict:
        """Calculate statistics for the crisis data"""
        stats = {
            'total_articles': len(crisis_data),
            'category_counts': {},
            'total_locations': 0,
            'geocoded_locations': 0,
            'average_confidence': 0.0
        }
        
        total_confidence = 0.0
        
        for crisis_item in crisis_data:
            category = crisis_item.get('predicted_category', 'Other')
            confidence = crisis_item.get('confidence', 0.0)
            article = crisis_item.get('article', {})
            locations = article.get('locations', [])
            
            # Count categories
            stats['category_counts'][category] = stats['category_counts'].get(category, 0) + 1
            
            # Count locations
            stats['total_locations'] += len(locations)
            stats['geocoded_locations'] += sum(1 for loc in locations if loc.get('geocoded', False))
            
            total_confidence += confidence
        
        # Calculate average confidence
        if crisis_data:
            stats['average_confidence'] = total_confidence / len(crisis_data)
        
        return stats
    
    def _create_statistics_html(self, stats: Dict) -> str:
        """Create HTML for statistics panel"""
        category_rows = ""
        for category, count in stats['category_counts'].items():
            color = self.crisis_colors.get(category, 'gray')
            category_rows += f"""
                <tr>
                    <td style="color: {color};">● {category}</td>
                    <td>{count}</td>
                </tr>
            """
        
        stats_html = f"""
        <div style="position: fixed; top: 10px; right: 10px; width: 250px; 
                    background: white; border: 2px solid #ccc; border-radius: 5px;
                    padding: 10px; z-index: 1000; box-shadow: 0 0 10px rgba(0,0,0,0.3);">
            <h4 style="margin-top: 0; color: #333;">Crisis Monitor Statistics</h4>
            
            <table style="width: 100%; font-size: 12px;">
                <tr><td><strong>Total Articles:</strong></td><td>{stats['total_articles']}</td></tr>
                <tr><td><strong>Locations Found:</strong></td><td>{stats['total_locations']}</td></tr>
                <tr><td><strong>Geocoded:</strong></td><td>{stats['geocoded_locations']}</td></tr>
                <tr><td><strong>Avg Confidence:</strong></td><td>{stats['average_confidence']:.2f}</td></tr>
            </table>
            
            <h5 style="margin-bottom: 5px; color: #333;">Crisis Categories:</h5>
            <table style="width: 100%; font-size: 11px;">
                {category_rows}
            </table>
            
            <div style="margin-top: 10px; font-size: 10px; color: #666;">
                Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
            </div>
        </div>
        """
        
        return stats_html
    
    def create_crisis_map(self, crisis_data: List[Dict], 
                         output_file: str = None,
                         include_heatmap: bool = True,
                         include_statistics: bool = True) -> str:
        """
        Create a complete crisis map with all features
        
        Args:
            crisis_data: List of crisis articles with location and classification data
            output_file: Output HTML file path
            include_heatmap: Whether to include heatmap layer
            include_statistics: Whether to include statistics panel
            
        Returns:
            Path to the generated HTML file
        """
        if output_file is None:
            output_file = OUTPUT_MAP_FILE
        
        logger.info(f"Creating crisis map with {len(crisis_data)} crisis items")
        
        # Create base map
        world_map = self.create_base_map()
        
        # Add crisis markers
        world_map = self.add_crisis_markers(world_map, crisis_data)
        
        # Add optional features
        if include_heatmap:
            world_map = self.add_crisis_heatmap(world_map, crisis_data)
        
        # Statistics panel removed to avoid duplication with main page panel
        # if include_statistics:
        #     world_map = self.add_statistics_panel(world_map, crisis_data)
        
        # Title panel removed per user request
        
        # Save map to file
        world_map.save(output_file)
        
        # Add custom filter panel with crisis data
        self._add_filter_panel(output_file, crisis_data)
        
        logger.info(f"Crisis map saved to: {output_file}")
        return output_file
    
    def _add_filter_panel(self, html_file: str, crisis_data: List[Dict] = None):
        """
        Add unified left sidebar with three tabs:
        - Chat: Conversational queries (keyword fallback, optional RAG)
        - Search: Real-time location/category filtering
        - Filter: Visual category toggles
        """
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Count categories from crisis data and build searchable index
        category_counts = {}
        search_index = []
        total_events = 0
        unique_sources = set()
        window_start = 'N/A'
        window_end = 'N/A'
        ts_values = []
        
        if crisis_data:
            aggregated = self.aggregate_crises(crisis_data)
            total_events = len(aggregated)
            
            for crisis in aggregated:
                category = crisis.get('category', 'Other')
                if category in self.crisis_colors:
                    category_counts[category] = category_counts.get(category, 0) + 1
                
                # Build search index with location + category
                location = crisis.get('location_name', '')
                search_index.append({
                    'location': location,
                    'category': category,
                    'lat': crisis.get('lat'),
                    'lon': crisis.get('lon'),
                    'count': crisis.get('article_count', 1)
                })
                
                # Count unique sources
                for article_data in crisis.get('articles', []):
                    source = article_data['article'].get('source_name', 
                                                        article_data['article'].get('source', ''))
                    if source:
                        unique_sources.add(source)
            
            # Compute data window from original crisis_data timestamps
            try:
                for item in crisis_data:
                    art = item.get('article', {})
                    ts = art.get('published_timestamp')
                    if isinstance(ts, (int, float)) and ts > 0:
                        ts_values.append(ts)
                if ts_values:
                    from datetime import datetime
                    window_start = datetime.utcfromtimestamp(min(ts_values)).strftime('%Y-%m-%d')
                    window_end = datetime.utcfromtimestamp(max(ts_values)).strftime('%Y-%m-%d')
            except Exception:
                pass
        
        # Convert Folium colors to hex for display
        folium_to_hex = {
            'red': '#d63e2a',
            'darkred': '#a23336',
            'orange': '#f69730',
            'blue': '#38aadd',
            'purple': '#d252b9',
            'green': '#72b026',
            'gray': '#575757',
            'darkgreen': '#728224',
            'lightred': '#ff8e7f',
            'lightblue': '#8adaff',
            'cadetblue': '#5f9ea0'
        }
        
        # Build category colors dict with hex values
        category_colors_hex = {}
        for category, folium_color in self.crisis_colors.items():
            hex_color = folium_to_hex.get(folium_color, '#575757')
            category_colors_hex[category] = hex_color
        
        # Generate JavaScript objects
        import json
        categories_js = json.dumps(category_counts)
        colors_js = json.dumps(category_colors_hex)
        search_index_js = json.dumps(search_index)
        
        # No external API needed - pure client-side search
        import os
        
        # Create unified sidebar UI
        sidebar_ui = f"""
        <style>
            /* Reset and base styles */
            * {{
                box-sizing: border-box;
            }}
            
            /* Sidebar container */
            .crisis-sidebar {{
                position: fixed;
                left: 0;
                top: 0;
                bottom: 0;
                width: 240px;
                background: white;
                border-right: 1px solid #ddd;
                display: flex;
                flex-direction: column;
                z-index: 1000;
                font-family: "Computer Modern Serif", Georgia, "Times New Roman", serif;
            }}
            
            /* Header */
            .sidebar-header {{
                padding: 12px 16px;
                border-bottom: 1px solid #ddd;
                background: #f8f9fa;
            }}
            
            .sidebar-title {{
                font-size: 13px;
                font-weight: bold;
                color: #333;
                margin: 0 0 4px 0;
                letter-spacing: 0.3px;
            }}
            
            .sidebar-stats {{
                font-size: 10px;
                color: #666;
                margin: 0;
            }}

            /* window selector removed (fixed to 7 days) */
            
            /* Content area */
            .sidebar-content {{
                flex: 1;
                overflow-y: auto;
                padding: 16px;
                display: flex;
                flex-direction: column;
            }}
            
            /* Chat interface */
            .chat-messages {{
                height: calc(100vh - 300px);
                overflow-y: auto;
                margin-bottom: 12px;
                padding: 8px;
                background: #f8f9fa;
                border-radius: 2px;
                border: 0.5px solid #ddd;
            }}
            
            .chat-message {{
                margin-bottom: 12px;
                padding: 8px 10px;
                border-radius: 4px;
                font-size: 11px;
                line-height: 1.5;
            }}
            
            .chat-message.user {{
                background: #e3f2fd;
                color: #1565c0;
                margin-left: 20px;
            }}
            
            .chat-message.bot {{
                background: white;
                border: 0.5px solid #ddd;
                color: #333;
                margin-right: 20px;
            }}
            
            .chat-message.bot .sources {{
                margin-top: 8px;
                padding-top: 8px;
                border-top: 0.5px solid #ddd;
                font-size: 9px;
                color: #666;
            }}
            
            .chat-input-container {{
                display: flex;
                gap: 8px;
            }}
            
            .chat-input {{
                flex: 1;
                padding: 8px;
                border: 0.5px solid #666;
                border-radius: 2px;
                font-size: 11px;
                font-family: "Computer Modern Serif", Georgia, "Times New Roman", serif;
            }}
            
            .chat-send-btn {{
                padding: 8px 16px;
                background: #333;
                color: white;
                border: none;
                border-radius: 2px;
                cursor: pointer;
                font-size: 11px;
                font-family: "Computer Modern Serif", Georgia, "Times New Roman", serif;
                transition: background 0.2s;
            }}
            
            .chat-send-btn:hover {{
                background: #000;
            }}
            
            .chat-send-btn:disabled {{
                background: #ccc;
                cursor: not-allowed;
            }}
            
            
            /* Adjust map to make room for sidebar */
            .folium-map {{
                margin-left: 240px !important;
            }}
        </style>
        
        <!-- Unified Sidebar -->
        <div class="crisis-sidebar">
            <!-- Header -->
            <div class="sidebar-header">
                <h1 class="sidebar-title">CRISIS MONITOR</h1>
                <p class="sidebar-stats">{total_events} events • {len(unique_sources)} sources<br><span class="muted">Window: {window_start} – {window_end} UTC • Last 7 days</span></p>
            </div>
            
            <!-- Chat Interface -->
            <div class="sidebar-content">
                <div class="chat-messages" id="chatMessages">
                    <div class="chat-message bot">
                        <div>How can I assist you today?</div>
                    </div>
                </div>
                
                <div class="chat-input-container">
                    <input 
                        type="text" 
                        class="chat-input" 
                        id="chatInput" 
                        placeholder="Search places or categories..."
                        onkeypress="if(event.key==='Enter') sendMessage()"
                    />
                    <button class="chat-send-btn" onclick="sendMessage()">Send</button>
                </div>
            </div>
        </div>
        
        <script>
            // Data from Python
            const categoryCounts = {categories_js};
            const categoryColors = {colors_js};
            const searchIndex = {search_index_js};
            
            // Get reference to Leaflet map
            let mapInstance = null;
            setTimeout(() => {{
                // Find the map instance (Folium creates it with a specific pattern)
                const mapElements = document.querySelectorAll('[id^="map_"]');
                if (mapElements.length > 0) {{
                    const mapId = mapElements[0].id;
                    mapInstance = window[mapId];
                }}
            }}, 1000);

            // Data window fixed to 7 days; selector removed

            // --- Search helpers ---
            function normalizeText(s) {{
                try {{
                    return (s || '')
                        .toString()
                        .toLowerCase()
                        .normalize('NFD')
                        .replace(/[\u0300-\u036f]/g, '')  // strip diacritics
                        .replace(/[^a-z0-9 ,\-]/g, ' ')    // drop punctuation except comma/hyphen
                        .replace(/\s+/g, ' ')              // collapse spaces
                        .trim();
                }} catch {{
                    return (s || '').toString().toLowerCase().trim();
                }}
            }}

            const aliasMap = {{
                'us': 'united states',
                'u s': 'united states',
                'usa': 'united states',
                'u.s.': 'united states',
                'u.s': 'united states',
                'uk': 'united kingdom',
                'uae': 'united arab emirates',
                'drc': 'democratic republic of the congo',
                'dr congo': 'democratic republic of the congo',
                'gaza': 'gaza strip',
                'nyc': 'new york'
            }};
            
            // Chat functionality
            async function sendMessage() {{
                const input = document.getElementById('chatInput');
                const message = input.value.trim();
                if (!message) return;
                
                const messagesDiv = document.getElementById('chatMessages');
                
                // Add user message
                const userMsg = document.createElement('div');
                userMsg.className = 'chat-message user';
                userMsg.textContent = message;
                messagesDiv.appendChild(userMsg);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
                
                input.value = '';
                
                // Show thinking indicator
                const thinkingMsg = document.createElement('div');
                thinkingMsg.className = 'chat-message bot';
                thinkingMsg.innerHTML = '<em>Thinking...</em>';
                messagesDiv.appendChild(thinkingMsg);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
                
                // Get response using smart keyword search
                const answer = processQuery(message);
                
                // Replace thinking with actual response
                thinkingMsg.innerHTML = answer;
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }}
            
            function processQuery(query) {{
                const q = query.toLowerCase().trim();
                
                // Statistics queries
                if (q.includes('how many') || q.includes('total') || q.includes('count') || q.includes('stats')) {{
                    let stats = `<strong>${{searchIndex.length}} crisis locations tracked</strong>:<br><br>`;
                    Object.entries(categoryCounts).forEach(([cat, count]) => {{
                        stats += `<strong>${{cat}}:</strong> ${{count}} locations<br>`;
                    }});
                    return stats;
                }}
                
                // List all
                if (q.includes('list') || q === 'all' || q.includes('show all')) {{
                    let html = '<strong>Top crisis locations:</strong><br><br>';
                    searchIndex.slice(0, 10).forEach((item, i) => {{
                        html += `${{i+1}}. <strong>${{item.location}}</strong><br>`;
                        html += `   ${{item.category}} (${{item.count}} incidents)<br>`;
                    }});
                    if (searchIndex.length > 10) {{
                        html += `<br><em>+ ${{searchIndex.length - 10}} more locations</em>`;
                    }}
                    return html;
                }}
                
                // Search for location or category
                let searchTerm = q.replace(/^(show me|show|find|search|where is|what about|tell me about|whats in|what's in|what is happening in|what's happening in|whats happening in|what is going on in|what's going on in)\s+/i, '').trim();
                let normalized = normalizeText(searchTerm);
                // If user asked "... in X" or "... about X", grab X
                const inIdx = normalized.lastIndexOf(' in ');
                const aboutIdx = normalized.lastIndexOf(' about ');
                const splitIdx = Math.max(inIdx, aboutIdx);
                if (splitIdx > -1) {{
                    normalized = normalized.substring(splitIdx + (inIdx > aboutIdx ? 4 : 7));
                }}
                // Trim trailing noise
                normalized = normalized.replace(/\b(now|today|currently)\b$/,'').trim();
                // Remove any trailing punctuation
                normalized = normalized.replace(/[^a-z0-9 \-,]/gi, '').trim();
                if (aliasMap[normalized]) {{
                    normalized = aliasMap[normalized];
                }}
                // Try location match first
                const locationMatches = searchIndex.filter(item =>
                    normalizeText(item.location).includes(normalized)
                );
                
                if (locationMatches.length > 0) {{
                    const loc = locationMatches[0];
                    if (mapInstance) {{
                        mapInstance.setView([loc.lat, loc.lon], 8);
                    }}
                    let response = `<strong>${{loc.location}}</strong><br><br>`;
                    response += `Category: ${{loc.category}}<br>`;
                    response += `Incidents: ${{loc.count}}<br><br>`;
                    response += `<em>Map zoomed to location</em>`;
                    
                    if (locationMatches.length > 1) {{
                        response += `<br><br>Other matches: `;
                        response += locationMatches.slice(1, 4).map(m => m.location.split(',')[0]).join(', ');
                    }}
                    return response;
                }}

                // Try category match
                const categoryMatches = searchIndex.filter(item =>
                    normalizeText(item.category).includes(normalized)
                );
                if (categoryMatches.length > 0) {{
                    let html = `<strong>Found ${{categoryMatches.length}} ${{categoryMatches[0].category}} locations:</strong><br><br>`;
                    categoryMatches.slice(0, 8).forEach((item, i) => {{
                        html += `${{i+1}}. ${{item.location}} (${{item.count}} incidents)<br>`;
                    }});
                    if (categoryMatches.length > 8) {{
                        html += `<br><em>+ ${{categoryMatches.length - 8}} more</em>`;
                    }}
                    return html;
                }}
                
                // No matches
                const examples = [
                    searchIndex[0].location.split(',')[0],
                    'humanitarian',
                    'how many total',
                    'list all'
                ];
                return `No results found for "${{query}}"<br><br>Try: "${{examples.join('", "')}}"`;
            }}
            
            
            function zoomToLocation(lat, lon) {{
                if (mapInstance) {{
                    mapInstance.setView([lat, lon], 8);
                }}
            }}
        </script>
        """
        
        # Insert before closing body tag
        html_content = html_content.replace('</body>', f'{sidebar_ui}</body>')
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)


def create_crisis_visualization(crisis_data: List[Dict], 
                              output_file: str = None) -> str:
    """
    Convenience function to create a crisis visualization map
    
    Args:
        crisis_data: List of crisis articles with location and classification data
        output_file: Optional output file path
        
    Returns:
        Path to the generated HTML file
    """
    mapper = CrisisMapper()
    return mapper.create_crisis_map(crisis_data, output_file)
