# ARGUS Usage Guide

## Quick Start

1. **Setup the environment:**
```bash
python setup.py
```

2. **Run the crisis monitor:**
```bash
python main.py
```

3. **View the results:**
Open `crisis_map.html` in your web browser to see the interactive crisis map.

## Command Line Options

### Basic Usage
```bash
python main.py [OPTIONS]
```
### Available Options

    | Option | Short | Description | Default |
    |--------|-------|-------------|---------|
    | `--hours` | `-h` | Hours back to search for articles | 72 |
    | `--max-articles` | `-m` | Maximum articles to process | 100 |
    | `--confidence` | `-c` | Minimum confidence threshold | 0.5 |
    | `--output` | `-o` | Output HTML file path | crisis_map.html |
    | `--no-cache` | | Force fresh data fetch | False |
    | `--verbose` | `-v` | Enable verbose logging | False |

### Example Commands

```bash
# Basic run with default settings
python main.py

# Fetch 48 hours of data with higher confidence threshold
python main.py --hours 48 --confidence 0.5

# Process more articles with custom output file
python main.py --max-articles 200 --output global_crises.html

# Force fresh data fetch (ignore cache)
python main.py --no-cache

# Enable verbose logging for debugging
python main.py --verbose
```

## Understanding the Output

### Interactive Map Features

1. **Crisis Markers**: Color-coded markers representing different crisis types
   - 🔴 Red: Natural Disasters
   - 🔴 Dark Red: Political Conflicts
   - 🟠 Orange: Humanitarian Crises
   - 🔵 Blue: Economic Crises
   - 🟣 Purple: Health Emergencies
   - 🟢 Green: Environmental Issues

2. **Layer Controls**: Toggle different crisis categories on/off

3. **Heatmap**: Shows crisis density across regions

4. **Statistics Panel**: Real-time statistics in the top-right corner

5. **Marker Popups**: Click markers for detailed article information

### Generated Files

- `crisis_map.html`: Interactive world map
- `crisis_summary.json`: Detailed statistics and analysis
- `argus.log`: System logs
- `articles_cache.json`: Cached article data

## Using Individual Components

### Data Ingestion
```python
from argus.data_ingestion import get_crisis_articles

# Fetch recent articles
articles = get_crisis_articles(hours_back=24)
print(f"Found {len(articles)} articles")
```

### Crisis Classification
```python
from argus.classifier import classify_crisis_articles

# Classify articles
results = classify_crisis_articles(articles, confidence_threshold=0.5)
crisis_articles = [r for r in results if r['is_crisis']]
```

### Geographic Extraction
```python
from argus.geo_extractor import extract_article_locations

# Extract locations
enhanced_articles = extract_article_locations(articles)
for article in enhanced_articles:
    print(f"Locations: {article['location_count']}")
```

### Map Creation
```python
from argus.mapper import create_crisis_visualization

# Create map
map_file = create_crisis_visualization(crisis_data, "my_map.html")
```

## Configuration

Edit `argus/config.py` to customize:

- Crisis categories
- Model settings
- Geographic parameters
- Map styling
- Color schemes

## Troubleshooting

### Common Issues

1. **"spaCy model not found"**
   ```bash
   python -m spacy download en_core_web_sm
   ```

2. **"No articles found"**
   - Check internet connection
   - Try increasing `--hours` parameter
   - Use `--no-cache` to force fresh data

3. **"Low geocoding success rate"**
   - This is normal; not all locations can be geocoded
   - Geographic extraction depends on article quality

4. **"Map shows no markers"**
   - Increase `--hours` to get more data
   - Lower `--confidence` threshold
   - Check that articles contain geographic entities

### Performance Tips

1. **For faster processing:**
   - Reduce `--max-articles`
   - Use cached data (default behavior)
   - Run on GPU-enabled machine for AI classification

2. **For more comprehensive results:**
   - Increase `--hours` (e.g., 48-72)
   - Increase `--max-articles`
   - Lower `--confidence` threshold

## Data Sources and Limitations

### GDELT Project
- **Source**: Global Database of Events, Language, and Tone
- **Coverage**: Worldwide news monitoring
- **Update Frequency**: Real-time (15-minute intervals)
- **Languages**: Primarily English, with some multilingual support

### Limitations
1. **Geographic Coverage**: Better for major cities and countries
2. **Language Bias**: English-language sources are better represented
3. **Classification Accuracy**: AI model may misclassify some articles
4. **Geocoding Limits**: Rate-limited to avoid overwhelming services
5. **Real-time Lag**: 15-30 minute delay from news publication

## Advanced Usage

### Custom Crisis Categories
Modify `CRISIS_CATEGORIES` in `config.py`:
```python
CRISIS_CATEGORIES = [
    "Natural Disasters",
    "Cyber Attacks",      # Custom category
    "Supply Chain Issues", # Custom category
    # ... other categories
]
```

### Custom Models
Use different AI models by modifying `CLASSIFICATION_MODEL`:
```python
CLASSIFICATION_MODEL = "microsoft/DialoGPT-medium"  # Alternative model
```

### Batch Processing
For processing large datasets:
```python
from argus.classifier import CrisisClassifier

classifier = CrisisClassifier()
results = classifier.classify_batch(articles, batch_size=16)
```
