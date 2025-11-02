# ARGUS Human Rights Intelligence Dashboard

## Overview

ARGUS has been refactored into a clean, insight-first Human Rights Intelligence Dashboard. The system now has two main parts:

1. **Python Pipeline** - Ingests, classifies, and exports crisis data
2. **Next.js Dashboard** - Modern web interface with editorial presentation

## Quick Start

### Run the Python Pipeline

```bash
# Install Python dependencies (if needed)
pip install -r requirements.txt

# Run the pipeline to generate data
python main.py

# This creates: public/data/human_rights_feed.json
```

### Run the Dashboard

```bash
# Navigate to frontend
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev

# Open http://localhost:3000
```

## Architecture

### Python Backend

**Location**: Root directory and `argus/` package

**Key Files**:
- `main.py` - Pipeline orchestrator
- `argus/export_human_rights.py` - JSON exporter for dashboard
- `argus/rss_fetcher_v2.py` - Fetches from 15+ NGO and media sources
- `argus/simple_classifier.py` - Rule-based crisis classification
- `argus/geo_extractor.py` - Geographic entity extraction

**Output**: `public/data/human_rights_feed.json`

### Frontend Dashboard

**Location**: `frontend/` directory

**Tech Stack**:
- Next.js 14 (React framework)
- TypeScript
- Tailwind CSS
- Recharts for visualizations

**Key Components**:
- `KpiStrip` - Hero metrics (incidents, countries, HRV share, sources)
- `IncidentsStackedChart` - WSJ-style time series chart
- `CountryTable` - Sortable list of affected countries
- `CountryDetail` - Modal with country-specific details
- `SourceBreakdown` - Transparent source attribution

## Design Philosophy

### Insight-First Presentation

The dashboard is designed as an editorial data graphic, not a tool:

- **Scannable in 30 seconds** - Key metrics at the top
- **Opinionated defaults** - Shows top violators and patterns immediately
- **Source transparency** - NGO/UN sources clearly distinguished from media
- **Minimal design** - WSJ-inspired color palette, clean typography

### Data Flow

```
RSS/NGO Sources → Python Pipeline → human_rights_feed.json → Next.js Dashboard
     (15+ feeds)      (classify,         (structured JSON)      (visual presentation)
                       aggregate)
```

## Data Contract

The Python pipeline exports `public/data/human_rights_feed.json` with this structure:

```json
{
  "generated_at": "ISO 8601 timestamp",
  "window_days": 7,
  "summary": {
    "total_incidents": 108,
    "countries_affected": 34,
    "human_rights_share": 0.42,
    "top_categories": [...],
    "source_mix": {"ngo": 61, "media": 39}
  },
  "time_series": [
    {
      "date": "2025-11-01",
      "categories": {
        "Human Rights Violations": 7,
        "Political Conflicts": 4
      }
    }
  ],
  "by_country": [
    {
      "country": "Ethiopia",
      "iso2": "ET",
      "incidents": 9,
      "top_category": "Human Rights Violations",
      "latest": "2025-11-01T10:00:00Z",
      "items": [...]
    }
  ],
  "sources": [...]
}
```

## Running in Production

### Build Static Site

```bash
cd frontend
npm run build
```

This generates a static site in `frontend/out/` that can be deployed to:
- GitHub Pages
- Netlify
- Vercel
- Any static file host

### Automated Updates

Set up a daily cron job or GitHub Action to:

1. Run `python main.py` to update data
2. Rebuild frontend (if hosting requires it)
3. Deploy updated files

Example GitHub Action (`.github/workflows/update-crisis-map.yml`):

```yaml
name: Update Crisis Dashboard
on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install Python dependencies
        run: pip install -r requirements.txt
      - name: Run pipeline
        run: python main.py
      - name: Deploy
        # Add your deployment step here
```

## Development Workflow

### Making Changes to Python Pipeline

1. Edit files in `argus/` or `main.py`
2. Run `python main.py` to test
3. Check output in `public/data/human_rights_feed.json`

### Making Changes to Frontend

1. Edit files in `frontend/src/`
2. Dashboard auto-reloads in dev mode
3. Test with mock data or real data from pipeline

### Adding New Data Sources

1. Add RSS feed to `argus/rss_fetcher_v2.py`
2. Update source classification in `argus/export_human_rights.py`
3. Run pipeline and verify data appears in dashboard

## Customization

### Changing Time Window

Edit `main.py`:
```python
--hours 336  # 14 days instead of 7
```

### Adjusting Category Colors

Edit `frontend/src/types/feed.ts`:
```typescript
export const CATEGORY_COLORS: Record<string, string> = {
  'Human Rights Violations': '#101820',  // Change colors here
  // ...
}
```

### Modifying Layout

Edit `frontend/src/pages/index.tsx` to change component arrangement and styling.

## Maintenance

### Keeping Dependencies Updated

Python:
```bash
pip list --outdated
pip install --upgrade <package>
```

Frontend:
```bash
cd frontend
npm outdated
npm update
```

### Monitoring Data Quality

Check the pipeline logs for:
- Number of articles fetched
- Classification success rate
- Geocoding accuracy
- Source diversity

### Troubleshooting

**No data in dashboard**:
- Ensure Python pipeline has run: `ls public/data/human_rights_feed.json`
- Check file has recent timestamp
- Verify JSON is valid: `python -m json.tool public/data/human_rights_feed.json`

**Frontend build errors**:
- Clear node_modules: `rm -rf node_modules && npm install`
- Clear Next.js cache: `rm -rf .next`

**Geocoding failures**:
- Nominatim rate limits - add delays between requests
- Check `argus/geo_extractor.py` timeout settings

## Credits

Built with ARGUS crisis monitoring system, refactored for human rights intelligence presentation.

**Data Sources**: Human Rights Watch, Amnesty International, UNHCR, UN OCHA, ReliefWeb, MSF, ICRC, and trusted regional media outlets.

**Design Inspiration**: Wall Street Journal and Financial Times data graphics.
