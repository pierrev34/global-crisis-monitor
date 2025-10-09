# Global Crisis Monitor

Real-time crisis monitoring system aggregating data from NGOs, human rights organizations, and disaster monitoring agencies.

## Features

- **Data Sources**: 15+ feeds (Human Rights Watch, Amnesty International, UN OCHA, ReliefWeb, GDACS, USGS, Al Jazeera, Radio Free Asia)
- **Rule-Based Classification**: Fast keyword + source trust filtering (no LLM dependency)
- **Geographic Extraction**: spaCy NER + Nominatim geocoding
- **Interactive Map**: Folium visualization with crisis markers, heatmap, and filtering
- **AI Chat**: Optional Groq API integration for conversational crisis queries

## Setup

```bash
# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Optional: Add Groq API key for AI chat
echo "GROQ_API_KEY=your_key_here" > .env

# Run pipeline
python3 main.py --hours 168
```

## Usage

```bash
# Generate map with last 7 days of data
python3 main.py

# Adjust time window and filtering
python3 main.py --hours 336 --confidence 0.3
```

Output: `crisis_map.html` (interactive map with chat interface)

## Architecture

```
argus/
├── rss_fetcher_v2.py      # RSS feed aggregation
├── simple_classifier.py   # Rule-based classification
├── geo_extractor.py       # Location extraction & geocoding
├── mapper.py              # Map generation + chat UI
└── config.py              # Crisis categories & colors
```

## Categories

Natural Disasters, Political Conflicts, Humanitarian Crises, Human Rights Violations, Health Emergencies, Economic Crises, Environmental Issues

## Tech Stack

Python, Pandas, spaCy, Folium, Geopy, BeautifulSoup, Feedparser, Groq API (optional)

