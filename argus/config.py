"""
Configuration settings for ARGUS Global Crisis Monitor
"""

import os
from typing import List, Dict

# Crisis categories for classification
CRISIS_CATEGORIES = [
    "Natural Disasters",
    "Political Conflicts", 
    "Humanitarian Crises",
    "Economic Crises",
    "Health Emergencies",
    "Environmental Issues"
]

# GDELT API configuration
GDELT_BASE_URL = "http://api.gdeltproject.org/api/v2/doc/doc"
GDELT_PARAMS = {
    "query": "(earthquake OR flood OR hurricane OR wildfire OR tsunami OR drought OR famine OR war OR conflict OR refugee OR humanitarian OR economic crisis OR recession OR pandemic OR outbreak) AND (news OR breaking OR alert OR emergency) -game -gaming -video -mod",
    "mode": "artlist",
    "format": "json",
    "maxrecords": 250,
    "sort": "datedesc",
    "sourcelang": "english"
}

# Model configurations
CLASSIFICATION_MODEL = "facebook/bart-large-mnli"
SPACY_MODEL = "en_core_web_sm"

# Geographic settings
GEOCODING_TIMEOUT = 5
MAX_LOCATIONS_PER_ARTICLE = 10

# Map visualization settings
MAP_CONFIG = {
    "default_location": [20.0, 0.0],  # Center of world map
    "default_zoom": 2,
    "tile_style": "OpenStreetMap"
}

# Color mapping for crisis types
CRISIS_COLORS = {
    "Natural Disasters": "red",
    "Political Conflicts": "darkred", 
    "Humanitarian Crises": "orange",
    "Economic Crises": "blue",
    "Health Emergencies": "purple",
    "Environmental Issues": "green"
}

# Output settings
OUTPUT_MAP_FILE = "crisis_map.html"
DATA_CACHE_FILE = "crisis_data.json"

# Processing limits
MAX_ARTICLES_TO_PROCESS = 100
MIN_ARTICLE_LENGTH = 100  # Minimum characters for processing
