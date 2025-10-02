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
        Add crisis markers to the map
        
        Args:
            world_map: Base Folium map
            crisis_data: List of crisis articles with location and classification data
            
        Returns:
            Map with crisis markers added
        """
        marker_count = 0
        
        # Create feature groups for different crisis types
        feature_groups = {}
        for category in self.crisis_colors.keys():
            feature_groups[category] = folium.FeatureGroup(name=category)
        
        # Add "Other" category for unclassified items
        feature_groups["Other"] = folium.FeatureGroup(name="Other")
        
        for crisis_item in crisis_data:
            article = crisis_item.get('article', {})
            category = crisis_item.get('predicted_category', 'Other')
            confidence = crisis_item.get('confidence', 0.0)
            locations = article.get('locations', [])
            
            # Add markers for each geocoded location in the article
            for location in locations:
                if location.get('geocoded', False):
                    lat = location.get('latitude')
                    lon = location.get('longitude')
                    
                    if lat is not None and lon is not None:
                        marker = self._create_crisis_marker(
                            lat, lon, article, category, confidence, location
                        )
                        
                        # Add to appropriate feature group
                        group = feature_groups.get(category, feature_groups["Other"])
                        marker.add_to(group)
                        marker_count += 1
        
        # Add all feature groups to map
        for group in feature_groups.values():
            group.add_to(world_map)
        
        # Add layer control
        folium.LayerControl().add_to(world_map)
        
        logger.info(f"Added {marker_count} crisis markers to map")
        return world_map
    
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
        
        # Create popup content
        popup_html = self._create_popup_content(article, category, confidence, location)
        
        # Create marker with custom icon
        marker = folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=400),
            tooltip=f"{category}: {article.get('title', 'No title')[:50]}...",
            icon=folium.Icon(
                color=color,
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
        title = article.get('title', 'No title')
        source = article.get('source', 'Unknown source')
        url = article.get('url', '#')
        published_date = article.get('published_date', 'Unknown date')
        location_name = location.get('found_name', location.get('text', 'Unknown location'))
        
        # Truncate content for popup
        content = article.get('content', '')
        if len(content) > 200:
            content = content[:200] + "..."
        
        # Create HTML popup
        popup_html = f"""
        <div style="width: 350px;">
            <h4 style="color: {self.crisis_colors.get(category, 'black')}; margin-bottom: 10px;">
                {category}
            </h4>
            <h5 style="margin-bottom: 8px;">{title}</h5>
            
            <div style="margin-bottom: 8px;">
                <strong>Location:</strong> {location_name}<br>
                <strong>Source:</strong> {source}<br>
                <strong>Date:</strong> {published_date}<br>
                <strong>Confidence:</strong> {confidence:.2f}
            </div>
            
            <div style="margin-bottom: 10px; font-size: 12px; color: #666;">
                {content}
            </div>
            
            <a href="{url}" target="_blank" style="color: #007cba; text-decoration: none;">
                📰 Read Full Article
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
            # Create heatmap layer
            heatmap = plugins.HeatMap(
                heat_data,
                name="Crisis Density Heatmap",
                min_opacity=0.2,
                max_zoom=18,
                radius=15,
                blur=10,
                gradient={
                    0.2: 'blue',
                    0.4: 'lime', 
                    0.6: 'orange',
                    0.8: 'red',
                    1.0: 'darkred'
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
        
        if include_statistics:
            world_map = self.add_statistics_panel(world_map, crisis_data)
        
        # Add title
        title_html = '''
        <div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%);
                    background: rgba(255,255,255,0.9); padding: 10px; border-radius: 5px;
                    z-index: 1000; box-shadow: 0 0 10px rgba(0,0,0,0.3);">
            <h2 style="margin: 0; color: #333; text-align: center;">
                🌍 Global Crisis Monitor
            </h2>
            <p style="margin: 5px 0 0 0; text-align: center; color: #666; font-size: 12px;">
                Real-time AI-powered crisis mapping from global news sources
            </p>
        </div>
        '''
        
        world_map.get_root().html.add_child(folium.Element(title_html))
        
        # Save map to file
        world_map.save(output_file)
        
        logger.info(f"Crisis map saved to: {output_file}")
        return output_file


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
