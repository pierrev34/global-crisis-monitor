# Global Crisis Monitor

Automated pipeline that aggregates crisis reports from NGOs, human rights organizations, and disaster monitoring systems, then geocodes and maps them for humanitarian analysis.

## Overview

This system monitors diverse crisis sources globally, categorizes events using rule-based classification, extracts geographic entities, and generates an interactive world map showing current crises. It prioritizes underreported situations by sourcing from human rights organizations and regional outlets rather than relying solely on mainstream Western media.

## Key Features

- **Diverse Crisis Sources**: Aggregates from 15+ sources including Human Rights Watch, Amnesty International, UN OCHA, ReliefWeb, UNHCR, Radio Free Asia, Middle East Eye, GDACS, and USGS
- **Rule-Based Classification**: Fast categorization using source trust and keyword matching (no LLM overhead)
- **Geographic Processing**: spaCy NER for location extraction, Nominatim geocoding with known crisis zone overrides
- **Interactive Mapping**: Folium-based world map with 400+ crisis markers, category filtering, and heatmap overlay
- **Underreported Crisis Coverage**: Captures systemic issues (Uyghur situation, El Salvador mass incarceration, etc.) often missed by mainstream outlets
- **Daily Automated Updates**: GitHub Actions workflow runs daily at midnight UTC

## Tech Stack

- **Language**: Python 3.9+
- **Data Processing**: Pandas, Feedparser, BeautifulSoup
- **NLP**: spaCy (named entity recognition for locations)
- **Geospatial**: Geopy/Nominatim geocoding, Folium map generation
- **Data Sources**: NGO RSS feeds (HRW, Amnesty, UN), disaster monitoring (GDACS, USGS), regional media (Radio Free Asia, Middle East Eye, Al Jazeera)
- **Deployment**: GitHub Actions, GitHub Pages

## Usage

Run the pipeline:
```bash
python main.py
```

Pipeline steps:
1. Fetch articles from 15+ NGO, human rights, and disaster monitoring sources
2. Classify using rule-based categorization (source trust + keywords)
3. Extract and geocode locations using spaCy NER
4. Generate interactive map saved as `crisis_map.html`

CLI options:
```bash
# Defaults: 7 days lookback, 150 articles max, 0.15 confidence threshold
python main.py --hours 168 --max-articles 150 --confidence 0.15

# Increase coverage
python main.py --hours 336 --max-articles 200

# Stricter filtering
python main.py --confidence 0.3
```

The system runs automatically via GitHub Actions daily at midnight UTC.

## Project Structure

```
global-crisis-monitor/
├── argus/
│   ├── rss_fetcher_v2.py      # NGO/human rights source aggregation
│   ├── simple_classifier.py   # Rule-based crisis categorization
│   ├── geo_extractor.py       # spaCy NER + geocoding
│   ├── mapper.py              # Folium map generation
│   └── config.py              # Configuration
├── main.py                     # Pipeline orchestrator
├── test_new_system.py          # System validation
├── requirements.txt            # Dependencies
└── .github/workflows/          # Daily auto-update via GitHub Actions
```

## Crisis Categories

- Human Rights Violations
- Political Conflicts
- Humanitarian Crises
- Natural Disasters
- Health Emergencies
- Economic Crises
- Environmental Issues

## Output

The system generates several output files:

### Interactive Crisis Map (`crisis_map.html`)
- **Conversational chat interface** for querying crisis data:
  - Natural language search: "show me gaza", "humanitarian crises", "how many events"
  - Location queries: Automatically zooms to locations and shows details
  - Category filtering: "show me conflicts", "hide natural disasters"
  - Statistics: "how many total", "list all crises"
- **Color-coded markers** for different crisis types (7 distinct colors including cadet blue for human rights)
- **Interactive popups** with article details and source links  
- **Optional heatmap overlay** showing crisis density
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

