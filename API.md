# ARGUS API Reference

## Module Overview

ARGUS consists of four main modules that can be used independently or together:

1. **`data_ingestion`** - Fetches news articles from GDELT
2. **`classifier`** - AI-powered crisis classification
3. **`geo_extractor`** - Geographic entity extraction and geocoding
4. **`mapper`** - Interactive map visualization

## data_ingestion Module

### GDELTIngester Class

```python
from argus.data_ingestion import GDELTIngester

ingester = GDELTIngester()
```

#### Methods

**`fetch_recent_articles(hours_back=24, max_articles=None)`**
- Fetches recent articles from GDELT API
- **Parameters:**
  - `hours_back` (int): Hours back to search
  - `max_articles` (int): Maximum articles to fetch
- **Returns:** List of article dictionaries

**`fetch_articles_by_keywords(keywords, hours_back=24)`**
- Fetches articles matching specific keywords
- **Parameters:**
  - `keywords` (List[str]): Keywords to search for
  - `hours_back` (int): Hours back to search
- **Returns:** List of article dictionaries

**`save_articles_to_file(articles, filename)`**
- Saves articles to JSON file
- **Parameters:**
  - `articles` (List[Dict]): Articles to save
  - `filename` (str): Output filename

### Convenience Functions

**`get_crisis_articles(hours_back=24, use_cache=True)`**
- Main function for fetching crisis-related articles
- **Returns:** List of article dictionaries

### Article Dictionary Structure

```python
{
    'title': str,           # Article title
    'content': str,         # Article content
    'url': str,            # Article URL
    'source': str,         # Source domain
    'published_date': str, # Publication date
    'language': str,       # Language code
    'tone': float,         # GDELT tone score
    'raw_data': dict      # Original GDELT data
}
```

## classifier Module

### CrisisClassifier Class

```python
from argus.classifier import CrisisClassifier

classifier = CrisisClassifier(model_name="facebook/bart-large-mnli")
```

#### Methods

**`classify_article(article, confidence_threshold=0.3)`**
- Classifies a single article
- **Parameters:**
  - `article` (Dict): Article dictionary
  - `confidence_threshold` (float): Minimum confidence
- **Returns:** Classification result dictionary

**`classify_batch(articles, confidence_threshold=0.3, batch_size=8)`**
- Classifies multiple articles in batches
- **Parameters:**
  - `articles` (List[Dict]): Articles to classify
  - `confidence_threshold` (float): Minimum confidence
  - `batch_size` (int): Batch size for processing
- **Returns:** List of classification results

**`get_category_statistics(classification_results)`**
- Generates statistics about classifications
- **Returns:** Statistics dictionary

**`filter_crisis_articles(classification_results, min_confidence=0.5)`**
- Filters to high-confidence crisis articles
- **Returns:** Filtered list of results

### Classification Result Structure

```python
{
    'article': dict,              # Original article
    'predicted_category': str,    # Predicted crisis category
    'confidence': float,          # Confidence score (0-1)
    'all_scores': dict,          # Scores for all categories
    'is_crisis': bool,           # Whether classified as crisis
    'classification_metadata': dict  # Model metadata
}
```

### Convenience Functions

**`classify_crisis_articles(articles, confidence_threshold=0.3, model_name=None)`**
- Main function for classifying articles
- **Returns:** List of classification results

## geo_extractor Module

### GeographicExtractor Class

```python
from argus.geo_extractor import GeographicExtractor

extractor = GeographicExtractor(spacy_model="en_core_web_sm")
```

#### Methods

**`extract_locations(text)`**
- Extracts geographic entities from text using NER
- **Parameters:**
  - `text` (str): Input text to analyze
- **Returns:** List of location dictionaries

**`geocode_location(location_text)`**
- Geocodes a location to lat/lng coordinates
- **Parameters:**
  - `location_text` (str): Location name
- **Returns:** Geocoding result dictionary or None

**`process_article_locations(article)`**
- Extracts and geocodes all locations from an article
- **Parameters:**
  - `article` (Dict): Article dictionary
- **Returns:** Enhanced article with location data

**`process_batch_locations(articles)`**
- Processes locations for multiple articles
- **Parameters:**
  - `articles` (List[Dict]): Articles to process
- **Returns:** List of enhanced articles

**`get_location_statistics(articles)`**
- Generates location extraction statistics
- **Returns:** Statistics dictionary

### Location Dictionary Structure

```python
{
    'text': str,              # Cleaned location text
    'original_text': str,     # Original extracted text
    'start_char': int,        # Start position in text
    'end_char': int,          # End position in text
    'label': str,             # NER label (GPE, LOC, etc.)
    'confidence': float,      # NER confidence
    'geocoded': bool,         # Whether successfully geocoded
    'latitude': float,        # Latitude (if geocoded)
    'longitude': float,       # Longitude (if geocoded)
    'found_name': str,        # Full geocoded address
    'query': str,             # Original query used
    'raw_data': dict         # Raw geocoding data
}
```

### Enhanced Article Structure

Original article plus:
```python
{
    'locations': List[Dict],  # List of location dictionaries
    'location_count': int,    # Total locations found
    'geocoded_count': int    # Successfully geocoded locations
}
```

### Convenience Functions

**`extract_article_locations(articles)`**
- Main function for extracting locations from articles
- **Returns:** List of enhanced articles

## mapper Module

### CrisisMapper Class

```python
from argus.mapper import CrisisMapper

mapper = CrisisMapper(map_config=custom_config)
```

#### Methods

**`create_base_map()`**
- Creates a base world map
- **Returns:** Folium Map object

**`add_crisis_markers(world_map, crisis_data)`**
- Adds crisis markers to the map
- **Parameters:**
  - `world_map` (folium.Map): Base map
  - `crisis_data` (List[Dict]): Crisis data with locations
- **Returns:** Map with markers added

**`add_crisis_heatmap(world_map, crisis_data)`**
- Adds heatmap layer showing crisis density
- **Parameters:**
  - `world_map` (folium.Map): Base map
  - `crisis_data` (List[Dict]): Crisis data
- **Returns:** Map with heatmap layer

**`add_statistics_panel(world_map, crisis_data)`**
- Adds statistics panel to the map
- **Parameters:**
  - `world_map` (folium.Map): Base map
  - `crisis_data` (List[Dict]): Crisis data
- **Returns:** Map with statistics panel

**`create_crisis_map(crisis_data, output_file=None, include_heatmap=True, include_statistics=True)`**
- Creates complete crisis map with all features
- **Parameters:**
  - `crisis_data` (List[Dict]): Crisis data
  - `output_file` (str): Output HTML file path
  - `include_heatmap` (bool): Include heatmap layer
  - `include_statistics` (bool): Include statistics panel
- **Returns:** Path to generated HTML file

### Crisis Data Structure

Combination of classification and location data:
```python
{
    'article': dict,              # Enhanced article with locations
    'predicted_category': str,    # Crisis category
    'confidence': float,          # Classification confidence
    'all_scores': dict,          # All category scores
    'is_crisis': bool,           # Is classified as crisis
    'classification_metadata': dict  # Classification metadata
}
```

### Convenience Functions

**`create_crisis_visualization(crisis_data, output_file=None)`**
- Main function for creating crisis visualization
- **Returns:** Path to generated HTML file

## Configuration

### config.py Settings

**Crisis Categories:**
```python
CRISIS_CATEGORIES = [
    "Natural Disasters",
    "Political Conflicts", 
    "Humanitarian Crises",
    "Economic Crises",
    "Health Emergencies",
    "Environmental Issues"
]
```

**Model Settings:**
```python
CLASSIFICATION_MODEL = "facebook/bart-large-mnli"
SPACY_MODEL = "en_core_web_sm"
```

**GDELT API Configuration:**
```python
GDELT_BASE_URL = "http://api.gdeltproject.org/api/v2/doc/doc"
GDELT_PARAMS = {
    "query": "crisis OR disaster OR conflict OR emergency OR humanitarian",
    "mode": "artlist",
    "format": "json",
    "maxrecords": 250,
    "sort": "datedesc"
}
```

**Map Configuration:**
```python
MAP_CONFIG = {
    "default_location": [20.0, 0.0],
    "default_zoom": 2,
    "tile_style": "OpenStreetMap"
}

CRISIS_COLORS = {
    "Natural Disasters": "red",
    "Political Conflicts": "darkred", 
    "Humanitarian Crises": "orange",
    "Economic Crises": "blue",
    "Health Emergencies": "purple",
    "Environmental Issues": "green"
}
```

## Error Handling

All modules include comprehensive error handling:

- **Network errors**: Graceful handling of API timeouts and failures
- **Model errors**: Fallback behavior when AI models fail to load
- **Data validation**: Input validation and sanitization
- **Geocoding limits**: Rate limiting and caching to avoid service abuse

## Performance Considerations

### Memory Usage
- Large article datasets can consume significant memory
- Use batch processing for large datasets
- Consider limiting `max_articles` parameter

### API Rate Limits
- GDELT API has rate limits
- Geocoding services have rate limits (handled automatically)
- Use caching to minimize repeated requests

### Model Loading
- Transformer models require significant memory (2-4GB)
- Models are loaded once per session
- Consider using smaller models for resource-constrained environments

## Examples

See `example.py` for comprehensive usage examples of all modules.
