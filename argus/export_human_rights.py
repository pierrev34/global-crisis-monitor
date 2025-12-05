"""
Human Rights Feed Exporter

Exports crisis data in a clean, frontend-friendly JSON format
for the Human Rights Intelligence Dashboard.

This module aggregates crisis data by country, builds time series,
and categorizes sources (NGO vs media) for transparency.
"""

import json
import logging
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


# Source trust mapping - NGOs and UN agencies are high-trust
NGO_SOURCES = {
    'human rights watch', 'hrw.org', 'amnesty', 'amnesty international',
    'unhcr', 'unicef', 'un ocha', 'reliefweb', 'msf', 'icrc',
    'doctors without borders', 'oxfam', 'save the children',
    'international rescue committee', 'care international'
}

UN_SOURCES = {
    'un', 'united nations', 'un ocha', 'unhcr', 'unicef', 'who',
    'wfp', 'undp', 'unrwa'
}

MEDIA_SOURCES = {
    'bbc', 'cnn', 'reuters', 'al jazeera', 'guardian', 'nytimes',
    'new york times', 'washington post', 'associated press', 'ap',
    'france24', 'dw', 'rfa', 'middle east eye'
}


def classify_source_type(source_name: str) -> str:
    """
    Classify source as NGO, UN, or media
    
    NGOs are privileged because human rights readers care about
    institutional reporting vs. journalistic coverage
    """
    source_lower = source_name.lower()
    
    # Check NGO first (highest trust for HRV reporting)
    for ngo in NGO_SOURCES:
        if ngo in source_lower:
            return 'ngo'
    
    # Check UN sources
    for un in UN_SOURCES:
        if un in source_lower:
            return 'un'
    
    # Check media
    for media in MEDIA_SOURCES:
        if media in source_lower:
            return 'media'
    
    # Default to media for unknown sources
    return 'media'


def extract_country_from_article(article: Dict) -> Optional[str]:
    """
    Extract primary country from article locations
    
    Returns the most relevant country, prioritizing:
    1. Countries from geocoded locations
    2. Crisis zone countries
    """
    locations = article.get('locations', [])
    
    if not locations:
        return None
    
    # Try to find a country in geocoded locations
    for location in locations:
        if location.get('geocoded', False):
            found_name = location.get('found_name', '')
            if isinstance(found_name, str) and found_name:
                # Extract country (last part of address)
                parts = found_name.split(', ')
                if len(parts) > 0:
                    country = parts[-1].strip()
                    # Filter out continents and regions
                    if country not in ['Asia', 'Africa', 'Europe', 'Antarctica', 'Oceania']:
                        return country
    
    return None


def get_country_iso2(country_name: str) -> str:
    """
    Get ISO2 code for country (simplified mapping)
    For production, use pycountry library
    """
    # Simplified mapping for common crisis zones
    country_to_iso = {
        'Afghanistan': 'AF', 'Sudan': 'SD', 'Yemen': 'YE',
        'Syria': 'SY', 'Ukraine': 'UA', 'Palestine': 'PS',
        'Ethiopia': 'ET', 'Myanmar': 'MM', 'Somalia': 'SO',
        'Haiti': 'HT', 'Lebanon': 'LB', 'Venezuela': 'VE',
        'China': 'CN', 'Iran': 'IR', 'Russia': 'RU',
        'United States': 'US', 'Israel': 'IL', 'Egypt': 'EG',
        'Turkey': 'TR', 'Pakistan': 'PK', 'Bangladesh': 'BD',
        'India': 'IN', 'Mexico': 'MX', 'Brazil': 'BR',
        'Colombia': 'CO', 'Nigeria': 'NG', 'South Africa': 'ZA',
        'Kenya': 'KE', 'Tanzania': 'TZ', 'Uganda': 'UG'
    }
    return country_to_iso.get(country_name, 'XX')


def get_country_coordinates(country_name: str) -> tuple:
    """
    Get approximate center coordinates for country
    For production, use a proper geocoding service
    """
    country_coords = {
        'Afghanistan': (33.93, 67.71),
        'Sudan': (12.86, 30.22),
        'Yemen': (15.55, 48.52),
        'Syria': (34.80, 38.99),
        'Ukraine': (48.38, 31.17),
        'Palestine': (31.95, 35.23),
        'Ethiopia': (9.15, 40.49),
        'Myanmar': (21.91, 95.96),
        'Somalia': (5.15, 46.20),
        'Haiti': (18.97, -72.29),
        'United States': (37.09, -95.71),
        'China': (35.86, 104.19),
        'Israel': (31.05, 34.85),
        'Egypt': (26.82, 30.80),
    }
    return country_coords.get(country_name, (0.0, 0.0))


def build_time_series(crisis_articles: List[Dict], window_days: int = 7) -> List[Dict]:
    """
    Build daily time series of incidents by category
    """
    # Initialize date buckets
    end_date = datetime.now()
    start_date = end_date - timedelta(days=window_days)
    
    # Create buckets for each day
    date_buckets = {}
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        date_buckets[date_str] = defaultdict(int)
        current_date += timedelta(days=1)
    
    # Fill buckets
    for result in crisis_articles:
        article = result['article']
        category = result.get('predicted_category', 'Unknown')
        
        # Extract publish date with multiple fallbacks
        published = article.get('published_date') or article.get('published') or article.get('pubDate')
        
        # If no date, use today as fallback
        if not published:
            pub_date = datetime.now()
        else:
            # Parse date (handle various formats)
            try:
                if isinstance(published, str):
                    if len(published) == 14:  # YYYYMMDDHHMMSS (GDELT format)
                        pub_date = datetime.strptime(published[:8], '%Y%m%d')
                    else:
                        # Try multiple date formats
                        from email.utils import parsedate_to_datetime
                        try:
                            # RFC 2822 format (RSS feeds): "Sat, 02 Nov 2024 12:00:00 GMT"
                            pub_date = parsedate_to_datetime(published)
                        except:
                            # ISO format: "2024-11-02T12:00:00Z"
                            pub_date = datetime.fromisoformat(published.replace('Z', '+00:00'))
                else:
                    pub_date = datetime.now()
            except Exception as e:
                logger.debug(f"Could not parse date {published}: {e}, using today")
                pub_date = datetime.now()
        
        date_str = pub_date.strftime('%Y-%m-%d')
        if date_str in date_buckets:
            date_buckets[date_str][category] += 1
    
    # Convert to list format - include ALL days (even with zero incidents)
    time_series = []
    for date_str in sorted(date_buckets.keys()):
        categories_dict = dict(date_buckets[date_str])
        # Include all days to show proper 30-day timeline
        time_series.append({
            'date': date_str,
            'categories': categories_dict if categories_dict else {}
        })
    
    return time_series


def aggregate_by_country(crisis_articles: List[Dict]) -> List[Dict]:
    """
    Aggregate articles by country with full details
    """
    country_data = defaultdict(lambda: {
        'incidents': [],
        'categories': defaultdict(int),
        'sources': set(),
        'latest_date': None
    })
    
    for result in crisis_articles:
        article = result['article']
        category = result.get('predicted_category', 'Unknown')
        
        # Extract country
        country = extract_country_from_article(article)
        if not country:
            continue
        
        # Get article metadata
        title = article.get('title', 'Untitled')
        url = article.get('url', '')
        source_name = article.get('source_name', article.get('source', 'Unknown'))
        published = article.get('published_date', '')
        
        # Parse published date
        published_iso = None
        try:
            if isinstance(published, str) and len(published) == 14:
                pub_date = datetime.strptime(published[:8], '%Y%m%d')
                published_iso = pub_date.isoformat() + 'Z'
            elif isinstance(published, str):
                published_iso = published
        except:
            pass
        
        # Add to country data
        country_data[country]['incidents'].append({
            'title': title,
            'url': url,
            'source': source_name,
            'category': category,
            'published': published_iso or datetime.now().isoformat() + 'Z'
        })
        
        country_data[country]['categories'][category] += 1
        country_data[country]['sources'].add(source_name)
        
        # Track latest date
        if published_iso:
            if not country_data[country]['latest_date'] or published_iso > country_data[country]['latest_date']:
                country_data[country]['latest_date'] = published_iso
    
    # Convert to list format
    by_country = []
    for country, data in country_data.items():
        # Get top category
        top_category = max(data['categories'].items(), key=lambda x: x[1])[0] if data['categories'] else 'Unknown'
        
        # Get coordinates
        lat, lon = get_country_coordinates(country)
        
        # Sort items by date (most recent first)
        sorted_items = sorted(data['incidents'], 
                            key=lambda x: x['published'], 
                            reverse=True)
        
        by_country.append({
            'country': country,
            'iso2': get_country_iso2(country),
            'lat': lat,
            'lon': lon,
            'incidents': len(data['incidents']),
            'top_category': top_category,
            'latest': data['latest_date'] or datetime.now().isoformat() + 'Z',
            'items': sorted_items[:10]  # Top 10 most recent
        })
    
    # Sort by incident count (descending)
    by_country.sort(key=lambda x: x['incidents'], reverse=True)
    
    return by_country


def build_source_breakdown(crisis_articles: List[Dict]) -> List[Dict]:
    """
    Build source statistics with trust classification
    """
    source_counts = defaultdict(int)
    source_types = {}
    
    for result in crisis_articles:
        article = result['article']
        source_name = article.get('source_name', article.get('source', 'Unknown'))
        
        source_counts[source_name] += 1
        
        # Classify source type if not already done
        if source_name not in source_types:
            source_types[source_name] = classify_source_type(source_name)
    
    # Convert to list
    sources = []
    for source_name, count in source_counts.items():
        sources.append({
            'name': source_name,
            'count': count,
            'type': source_types.get(source_name, 'media')
        })
    
    # Sort by count (descending)
    sources.sort(key=lambda x: x['count'], reverse=True)
    
    return sources


def export_human_rights_json(crisis_articles: List[Dict], 
                             window_days: int = 30,
                             output_path: str = 'frontend/public/data/human_rights_feed.json') -> str:
    """
    Export crisis data in frontend-friendly JSON format
    
    Args:
        crisis_articles: List of classified crisis articles
        window_days: Time window in days (default 30 for insight-first view)
        output_path: Output file path
    
    Returns:
        Path to generated JSON file
    """
    logger.info(f"Exporting human rights feed for {len(crisis_articles)} articles...")
    
    # Build time series for full 30 days
    time_series = build_time_series(crisis_articles, window_days)
    
    # Aggregate by country
    by_country = aggregate_by_country(crisis_articles)
    
    # Build source breakdown
    sources = build_source_breakdown(crisis_articles)
    
    # Calculate summary statistics
    total_incidents = len(crisis_articles)
    countries_affected = len(by_country)
    
    # Count human rights violations
    hrv_count = sum(1 for r in crisis_articles 
                   if r.get('predicted_category') == 'Human Rights Violations')
    human_rights_share = hrv_count / total_incidents if total_incidents > 0 else 0
    
    # Top categories
    category_counts = defaultdict(int)
    for result in crisis_articles:
        category = result.get('predicted_category', 'Unknown')
        if category != 'Unknown':
            category_counts[category] += 1
    
    top_categories = [
        {'name': cat, 'count': count}
        for cat, count in sorted(category_counts.items(), 
                                key=lambda x: x[1], 
                                reverse=True)[:5]
    ]
    
    # Source mix (NGO vs media)
    ngo_count = sum(1 for s in sources if s['type'] in ['ngo', 'un'])
    media_count = sum(1 for s in sources if s['type'] == 'media')
    
    # Calculate week-over-week comparison
    # Last 7 days vs previous 7 days
    current_7d_total = 0
    prev_7d_total = 0
    
    if len(time_series) >= 14:
        # Last 7 days
        for point in time_series[-7:]:
            current_7d_total += sum(point['categories'].values())
        # Previous 7 days (days 7-14 from end)
        for point in time_series[-14:-7]:
            prev_7d_total += sum(point['categories'].values())
    elif len(time_series) >= 7:
        # Only have current week
        for point in time_series[-7:]:
            current_7d_total += sum(point['categories'].values())
    
    delta_pct = None
    if prev_7d_total > 0:
        delta_pct = round(((current_7d_total - prev_7d_total) / prev_7d_total) * 100, 1)
    
    # Calculate 30-day rolling average
    rolling_avg_30d = None
    if time_series:
        total_30d = sum(sum(point['categories'].values()) for point in time_series)
        rolling_avg_30d = round(total_30d / len(time_series), 1)
    
    # Build final JSON structure
    feed = {
        'generated_at': datetime.now().isoformat() + 'Z',
        'window_days': window_days,
        'summary': {
            'total_incidents': total_incidents,
            'countries_affected': countries_affected,
            'human_rights_share': round(human_rights_share, 2),
            'top_categories': top_categories,
            'source_mix': {
                'ngo': ngo_count,
                'media': media_count
            },
            'prev_7d_total': prev_7d_total if prev_7d_total > 0 else None,
            'delta_pct': delta_pct,
            'rolling_avg_30d': rolling_avg_30d
        },
        'time_series': time_series,
        'by_country': by_country,
        'sources': sources
    }
    
    # Ensure output directory exists
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Write JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(feed, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Exported human rights feed to {output_path}")
    logger.info(f"   {total_incidents} incidents across {countries_affected} countries")
    logger.info(f"   {hrv_count} human rights violations ({human_rights_share:.1%})")
    logger.info(f"   {ngo_count} NGO/UN items, {media_count} media items")
    if delta_pct is not None:
        logger.info(f"   Week-over-week: {delta_pct:+.1f}%")
    
    return str(output_file)
