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
        world_map = folium.Map(
            location=self.config['default_location'],
            zoom_start=self.config['default_zoom'],
            tiles=self.config['tile_style']
        )
        
        # Add fullscreen button
        plugins.Fullscreen().add_to(world_map)
        
        # Add measure control for distance measurement
        plugins.MeasureControl().add_to(world_map)
        
        return world_map
    
    def add_crisis_markers(self, world_map: folium.Map, 
                          crisis_data: List[Dict]) -> folium.Map:
        """
        Add crisis markers to the map with clustering to reduce visual clutter
        
        Args:
            world_map: Base Folium map
            crisis_data: List of crisis articles with location and classification data
            
        Returns:
            Map with crisis markers added
        """
        marker_count = 0
        
        # Create marker clusters for different crisis types
        clusters = {}
        for category in self.crisis_colors.keys():
            clusters[category] = plugins.MarkerCluster(
                name=category,
                show=True,
                control=True
            )
        
        # Add "Other" category cluster
        clusters["Other"] = plugins.MarkerCluster(name="Other", show=False, control=True)
        
        for crisis_item in crisis_data:
            article = crisis_item.get('article', {})
            category = crisis_item.get('predicted_category', 'Other')
            confidence = crisis_item.get('confidence', 0.0)
            locations = article.get('locations', [])
            
            # First try to add markers for perfectly geocoded locations
            markers_added_for_article = 0
            for location in locations:
                if location.get('geocoded', False):
                    lat = location.get('latitude')
                    lon = location.get('longitude')
                    
                    if lat is not None and lon is not None:
                        marker = self._create_crisis_marker(
                            lat, lon, article, category, confidence, location
                        )
                        
                        # Add to appropriate cluster
                        cluster = clusters.get(category, clusters["Other"])
                        marker.add_to(cluster)
                        marker_count += 1
                        markers_added_for_article += 1
            
            # If no perfect geocoding, use intelligent fallbacks
            if markers_added_for_article == 0 and confidence >= 0.5:
                fallback_location = self._get_fallback_location(article, category)
                if fallback_location:
                    lat, lon, location_name = fallback_location
                    
                    # Create fallback location data
                    fallback_loc_data = {
                        'text': location_name,
                        'found_name': location_name,
                        'geocoded': True,  # Mark as geocoded for display
                        'latitude': lat,
                        'longitude': lon,
                        'fallback': True  # Mark as fallback
                    }
                    
                    marker = self._create_crisis_marker(
                        lat, lon, article, category, confidence, fallback_loc_data
                    )
                    
                    # Add to appropriate cluster
                    cluster = clusters.get(category, clusters["Other"])
                    marker.add_to(cluster)
                    marker_count += 1
        
        # Add all clusters to map
        for cluster in clusters.values():
            cluster.add_to(world_map)
        
        # Add layer control for toggling categories
        folium.LayerControl(collapsed=False).add_to(world_map)
        
        logger.info(f"Added {marker_count} crisis markers to map")
        return world_map
    
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
        """Add custom filter panel to the generated map HTML"""
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Count categories from crisis data
        category_counts = {}
        if crisis_data:
            for item in crisis_data:
                category = item.get('predicted_category', 'Other')
                if category in self.crisis_colors:
                    category_counts[category] = category_counts.get(category, 0) + 1
        
        # Generate JavaScript object for categories
        import json
        categories_js = json.dumps(category_counts)
        
        # Create filter panel HTML/CSS/JS
        filter_panel = f"""
        <style>
            .filter-panel {{
                position: fixed;
                top: 80px;
                right: 10px;
                background: white;
                border-radius: 2px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.12);
                padding: 8px 10px;
                z-index: 1000;
                min-width: 180px;
                max-width: 200px;
                font-family: "Computer Modern Serif", Georgia, "Times New Roman", serif;
                border: 0.5px solid #333;
                font-size: 11px;
            }}
            .filter-panel.collapsed .filter-content {{
                display: none;
            }}
            .filter-header {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                cursor: pointer;
                margin-bottom: 6px;
                padding-bottom: 4px;
                border-bottom: 0.5px solid #ddd;
            }}
            .filter-panel h3 {{
                margin: 0;
                font-size: 11px;
                color: #333;
                flex: 1;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .filter-toggle {{
                background: none;
                border: none;
                font-size: 14px;
                cursor: pointer;
                padding: 0;
                width: 16px;
                height: 16px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #666;
            }}
            .filter-item {{
                display: flex;
                align-items: center;
                margin: 3px 0;
                cursor: pointer;
                padding: 2px;
                border-radius: 2px;
            }}
            .filter-item:hover {{
                background: #f9f9f9;
            }}
            .filter-checkbox {{
                width: 13px;
                height: 13px;
                margin-right: 6px;
                cursor: pointer;
                flex-shrink: 0;
            }}
            .filter-label {{
                flex: 1;
                font-size: 11px;
                color: #333;
                display: flex;
                align-items: center;
                cursor: pointer;
                line-height: 1.3;
            }}
            .filter-color {{
                width: 8px;
                height: 8px;
                border-radius: 50%;
                margin-right: 5px;
                display: inline-block;
            }}
            .filter-count {{
                font-size: 9px;
                color: #999;
                margin-left: auto;
                padding-left: 4px;
            }}
            .filter-buttons {{
                margin-top: 6px;
                padding-top: 6px;
                border-top: 0.5px solid #ddd;
                display: flex;
                gap: 4px;
            }}
            .filter-btn {{
                flex: 1;
                padding: 3px 6px;
                border: 0.5px solid #666;
                background: white;
                border-radius: 1px;
                cursor: pointer;
                font-size: 10px;
                font-family: "Computer Modern Serif", Georgia, "Times New Roman", serif;
                transition: all 0.15s;
            }}
            .filter-btn:hover {{
                background: #f5f5f5;
            }}
        </style>
        
        <div class="filter-panel" id="filterPanel">
            <div class="filter-header" onclick="toggleFilterPanel()">
                <h3>Filter</h3>
                <button class="filter-toggle" id="filterToggle">−</button>
            </div>
            <div class="filter-content">
                <div id="filterItems"></div>
                <div class="filter-buttons">
                    <button class="filter-btn" onclick="selectAllFilters()">All</button>
                    <button class="filter-btn" onclick="clearAllFilters()">None</button>
                </div>
            </div>
        </div>
        
        <script>
            // Category data from Python
            const categoryCounts = {categories_js};
            
            // Category colors matching Python config
            const categoryColors = {{
                'Human Rights Violations': '#8B0000',
                'Political Conflicts': '#DC143C',
                'Humanitarian Crises': '#FF6B35',
                'Natural Disasters': '#FF8C00',
                'Health Emergencies': '#9370DB',
                'Economic Crises': '#4682B4',
                'Environmental Issues': '#228B22'
            }};
            
            // Track visibility state
            let categoryStates = {{}};
            
            // Toggle filter panel
            function toggleFilterPanel() {{
                const panel = document.getElementById('filterPanel');
                const toggle = document.getElementById('filterToggle');
                panel.classList.toggle('collapsed');
                toggle.textContent = panel.classList.contains('collapsed') ? '+' : '−';
            }}
            
            // Initialize filters from pre-computed data
            function initializeFilters() {{
                const filterContainer = document.getElementById('filterItems');
                filterContainer.innerHTML = ''; // Clear existing
                
                // Use pre-computed category counts
                Object.keys(categoryCounts).forEach(category => {{
                    const count = categoryCounts[category];
                    if (count > 0 && categoryColors[category]) {{
                        categoryStates[category] = true;
                        
                        const filterItem = document.createElement('div');
                        filterItem.className = 'filter-item';
                        
                        const checkbox = document.createElement('input');
                        checkbox.type = 'checkbox';
                        checkbox.className = 'filter-checkbox';
                        checkbox.id = 'filter-' + category.replace(/\\s+/g, '-');
                        checkbox.checked = true;
                        checkbox.addEventListener('change', function() {{
                            toggleCategory(category);
                        }});
                        
                        const labelEl = document.createElement('label');
                        labelEl.className = 'filter-label';
                        labelEl.htmlFor = checkbox.id;
                        
                        const colorSpan = document.createElement('span');
                        colorSpan.className = 'filter-color';
                        colorSpan.style.background = categoryColors[category];
                        
                        const nameSpan = document.createElement('span');
                        nameSpan.textContent = category;
                        nameSpan.style.fontSize = '11px';
                        nameSpan.style.whiteSpace = 'nowrap';
                        nameSpan.style.overflow = 'hidden';
                        nameSpan.style.textOverflow = 'ellipsis';
                        
                        labelEl.appendChild(colorSpan);
                        labelEl.appendChild(nameSpan);
                        
                        filterItem.appendChild(checkbox);
                        filterItem.appendChild(labelEl);
                        filterContainer.appendChild(filterItem);
                    }}
                }});
                
                if (Object.keys(categoryCounts).length === 0) {{
                    filterContainer.innerHTML = '<div style="font-size:10px;color:#999;padding:5px;">No categories found</div>';
                }}
            }}
            
            function toggleCategory(category) {{
                const checkbox = document.getElementById('filter-' + category.replace(/\\s+/g, '-'));
                if (!checkbox) return;
                
                const isChecked = checkbox.checked;
                categoryStates[category] = isChecked;
                
                // Find and toggle the corresponding layer in Leaflet layer control
                setTimeout(() => {{
                    const layers = document.querySelectorAll('.leaflet-control-layers-overlays label');
                    layers.forEach(label => {{
                        const labelText = label.textContent.trim();
                        // Match exact category name (spans can be present)
                        if (labelText === category || labelText.includes(category)) {{
                            const input = label.querySelector('input[type="checkbox"]');
                            if (input && input.checked !== isChecked) {{
                                input.click();
                            }}
                        }}
                    }});
                }}, 100);
            }}
            
            function selectAllFilters() {{
                Object.keys(categoryStates).forEach(category => {{
                    const checkbox = document.getElementById('filter-' + category.replace(/\\s+/g, '-'));
                    if (checkbox && !checkbox.checked) {{
                        checkbox.checked = true;
                        toggleCategory(category);
                    }}
                }});
            }}
            
            function clearAllFilters() {{
                Object.keys(categoryStates).forEach(category => {{
                    const checkbox = document.getElementById('filter-' + category.replace(/\\s+/g, '-'));
                    if (checkbox && checkbox.checked) {{
                        checkbox.checked = false;
                        toggleCategory(category);
                    }}
                }});
            }}
            
            // Initialize when DOM is loaded
            document.addEventListener('DOMContentLoaded', function() {{
                setTimeout(initializeFilters, 500);
            }});
        </script>
        """
        
        # Insert before closing body tag
        html_content = html_content.replace('</body>', f'{filter_panel}</body>')
        
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
