# Global Crisis Monitor

**Tagline:** An automated pipeline that uses AI to identify, classify, and map global crises from real-time news data (RSS + crisis-native feeds + GDELT), with intelligent geocoding and interactive visualization.

## Project Overview

Global Crisis Monitor is a data processing system that continuously monitors thousands of global news articles to provide a real-time, high-level view of emerging world events. The system automatically ingests news data, uses a sophisticated Natural Language Processing (NLP) model to understand the content, and classifies articles into distinct crisis categories such as Natural Disasters, Political Conflicts, and Humanitarian Crises. The result is an interactive world map where each classified event is plotted, providing a dynamic and insightful dashboard of global challenges.

## Motivation & Purpose

In an era of information overload, distinguishing significant global events from background noise is a persistent challenge. This project was inspired by the goal of applying advanced AI not for commercial purposes, but for social good. The motivation was to create a proof-of-concept for a "humanitarian dashboard"—a tool that could help journalists, policymakers, or aid organizations gain rapid, structured insight into where and what kind of crises are unfolding.

- **Automated Data Ingestion**: Hybrid pipeline that ingests from major RSS feeds (e.g., CNN), crisis-native feeds (USGS Earthquakes, GDACS, WHO Disease Outbreaks, ReliefWeb), and falls back to the GDELT Project API for coverage.
- **Zero-Shot AI Classification**: Uses Hugging Face transformers for flexible crisis categorization
- **Geographic Entity Extraction**: Employs spaCy NER to identify and geocode locations
- **Interactive Mapping**: Creates dynamic world maps with Folium for crisis visualization

## Tech Stack

- **Core**: Python, Pandas
- **AI & NLP**: Hugging Face Transformers, spaCy
- **Geospatial**: Geopy, Folium
- **Data Sources**: Major RSS (CNN, etc.), USGS, GDACS, WHO Disease Outbreaks, ReliefWeb, and GDELT API

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd global-crisis-monitor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download spaCy language model:
```bash
python -m spacy download en_core_web_sm
```

## Usage

Run the main pipeline:
```bash
python main.py
```

This will:
1. Fetch recent news articles from the hybrid sources (RSS + crisis feeds + GDELT fallback)
2. Classify them into crisis categories
3. Extract geographic entities
4. Generate an interactive map saved as `crisis_map.html`

CLI options (defaults chosen for a fuller map):

```bash
# Defaults: --hours 72, --confidence 0.2, --max-articles 100
python main.py [--hours 72] [--max-articles 100] [--confidence 0.2] [--no-cache] [--output crisis_map.html]

# Examples
python main.py --no-cache                                  # Fresh fetch using defaults
python main.py --hours 48 --max-articles 200               # Wider window and more items
python main.py --confidence 0.15                           # Allow more lower-confidence items
```

Notes:
- The classification threshold now respects the `--confidence` flag (no hard-coded gate).
- If the map iframe looks stale, open `crisis_map.html` directly or add a cache-buster query param in `index.html`.

## Project Structure

```
global-crisis-monitor/
├── argus/                    # Main package
│   ├── __init__.py          # Package initialization
│   ├── config.py            # Configuration settings
│   ├── data_ingestion.py    # GDELT data fetching
│   ├── classifier.py        # AI-powered crisis classification
│   ├── geo_extractor.py     # Geographic entity extraction
│   └── mapper.py           # Interactive map generation
├── main.py                  # Main pipeline orchestrator
├── setup.py                # Environment setup script
├── example.py              # Usage examples and demos
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── USAGE.md               # Detailed usage guide
├── API.md                 # API reference documentation
├── CONTRIBUTING.md        # Development and contribution guide
└── .gitignore            # Git ignore patterns
```

## Crisis Categories

- Natural Disasters
- Political Conflicts
- Humanitarian Crises
- Economic Crises
- Health Emergencies
- Environmental Issues

## Output

The system generates several output files:

### Interactive Crisis Map (`crisis_map.html`)
- **Color-coded markers** for different crisis types
- **Interactive popups** with article details and source links  
- **Layer controls** to toggle crisis categories
- **Optional heatmap overlay** showing crisis density
- **Sidebar stats** live in `index.html` (map overlay panel removed to reduce clutter)
- **Fullscreen mode** and measurement tools

### Additional Files
- `crisis_summary.json` - Detailed statistics and analysis
- `argus.log` - System logs and processing information
- `articles_cache.json` - Cached article data for faster subsequent runs

## Geocoding & API Keys

- Primary geocoder: OpenStreetMap Nominatim via `geopy`.
- Fallback geocoder: Mapbox (recommended for reliability). Create a `.env` file in project root:

```bash
MAPBOX_TOKEN=pk_your_mapbox_token_here
```

The `.env` is already gitignored in `.gitignore`. With a Mapbox token, geocoding becomes precise and avoids SSL issues to OSM.

## Data Sources & Fetching

- RSS fetching uses `requests` + `feedparser.parse(bytes)` with SSL fallback.
- Crisis-native feeds: USGS Earthquakes, GDACS, WHO Disease Outbreaks, ReliefWeb.
- Major news RSS: multiple CNN channels; other outlets may be added.
- GDELT API is used as a supplement/fallback when RSS volume is low.

## Tips

- Want a busier map? Use a broader time window and/or a lower confidence:

```bash
python main.py --hours 96 --max-articles 200 --confidence 0.15 --no-cache
```

- Without a Mapbox token, the app still shows markers via intelligent fallbacks (country/region centroids). Add a token for exact city coordinates.

## Key Features

### 🤖 **Advanced AI Classification**
- Zero-shot learning using state-of-the-art transformer models
- No training data required - adapts to new crisis types automatically
- Confidence scoring for reliability assessment

### 🌍 **Intelligent Geographic Processing**
- Named Entity Recognition (NER) for location extraction
- Automatic geocoding to precise coordinates
- Handles ambiguous and multi-word location names

### 📊 **Rich Data Visualization**
- Interactive world map with crisis markers
- Real-time statistics and analytics
- Customizable color schemes and styling
- Mobile-responsive design

### ⚡ **Production-Ready Pipeline**
- Comprehensive error handling and logging
- Modular architecture for easy customization
