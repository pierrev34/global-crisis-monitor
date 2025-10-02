# Crisis Monitor Data Sources

## Current Status: Demo Data Mode

Your crisis monitoring system is currently displaying **sample/demo data** instead of real crisis news. This is why you see "example.com" URLs when clicking "Read Article" links.

## Why This Happens

The system tries to fetch real crisis data from the GDELT Project API, but falls back to demo data when:

1. **GDELT API Issues**: The API may be down, rate-limited, or returning non-English content
2. **Network Problems**: Connection issues preventing API access
3. **Data Quality**: API returns gaming/irrelevant content that gets filtered out

## Current Data Flow

```
1. Try GDELT API → 2. Process & Filter → 3. If no valid articles → 4. Use Demo Data
```

## Solutions to Get Real Crisis Data

### Option 1: Fix GDELT Integration (Technical)
- Install dependencies: `pip install -r requirements.txt`
- Run with verbose logging: `python3 main.py --verbose --no-cache`
- Check logs for specific API errors
- May require API key or different endpoints

### Option 2: Alternative News Sources (Recommended)
- Use RSS feeds from major news outlets (BBC, Reuters, CNN)
- Requires adding `feedparser` to requirements.txt
- More reliable than GDELT for English crisis news

### Option 3: Manual Data Input
- Create JSON files with real crisis data
- Load from local files instead of API
- Good for testing and demonstrations

## Quick Test

Run this to see what GDELT returns:
```bash
python3 test_gdelt.py
```

## Identifying Demo vs Real Data

**Demo Data Indicators:**
- URLs start with `https://example.com/`
- Same articles appear repeatedly
- Perfect geographic coverage
- Articles mention "sample domain"

**Real Data Indicators:**
- URLs from actual news sites (bbc.com, reuters.com, etc.)
- Varying article quality and locations
- Recent timestamps
- Clickable links to real articles

## Next Steps

1. **Immediate**: The system works perfectly for demonstration purposes
2. **Short-term**: Add RSS news integration for real data
3. **Long-term**: Improve GDELT API integration or switch to paid news APIs

The AI classification, geographic extraction, and mapping components all work correctly - they just need real news data as input.
