#!/usr/bin/env python3
"""
Test the real data pipeline without requiring heavy ML dependencies
This tests the data fetching and basic processing without AI classification
"""

import sys
import os
import json
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_data_fetching():
    """Test fetching real crisis data"""
    try:
        from argus.data_ingestion import get_crisis_articles
        
        print("🔍 Testing real crisis data fetching...")
        print("=" * 50)
        
        # Fetch articles with RSS preference
        articles = get_crisis_articles(
            hours_back=24, 
            use_cache=False, 
            prefer_rss=True
        )
        
        if not articles:
            print("❌ No articles fetched")
            return False
        
        print(f"✅ Successfully fetched {len(articles)} articles")
        print()
        
        # Analyze the articles
        rss_articles = [a for a in articles if a.get('fetched_via') == 'rss']
        demo_articles = [a for a in articles if a['url'].startswith('https://example.com')]
        gdelt_articles = [a for a in articles if a.get('fetched_via') != 'rss' and not a['url'].startswith('https://example.com')]
        
        print(f"📊 Article Sources:")
        print(f"   RSS articles: {len(rss_articles)}")
        print(f"   GDELT articles: {len(gdelt_articles)}")
        print(f"   Demo articles: {len(demo_articles)}")
        print()
        
        # Show sample articles
        print("📰 Sample Articles:")
        for i, article in enumerate(articles[:3], 1):
            source_type = "RSS" if article.get('fetched_via') == 'rss' else "GDELT" if not article['url'].startswith('https://example.com') else "DEMO"
            print(f"{i}. [{source_type}] {article['title']}")
            print(f"   Source: {article.get('source_name', article['source'])}")
            print(f"   URL: {article['url']}")
            print()
        
        # Check if we have real data
        has_real_data = len(rss_articles) > 0 or len(gdelt_articles) > 0
        
        if has_real_data:
            print("🎉 SUCCESS: Real crisis data is being fetched!")
            print("   Your crisis monitor will show actual news events.")
        else:
            print("⚠️  Only demo data found. Check RSS feeds and GDELT API.")
        
        return has_real_data
        
    except Exception as e:
        print(f"❌ Error testing data fetching: {e}")
        return False

def test_geographic_processing():
    """Test geographic processing without full ML pipeline"""
    try:
        from argus.geo_extractor import extract_article_locations
        
        print("\n🌍 Testing geographic processing...")
        print("=" * 50)
        
        # Create sample article for testing
        test_article = {
            'title': 'Earthquake Strikes Turkey Near Ankara',
            'content': 'A 6.2 magnitude earthquake struck central Turkey near the capital Ankara, causing damage in Istanbul and surrounding areas.',
            'url': 'https://example.com/test',
            'source': 'test'
        }
        
        # Process geographic entities
        processed = extract_article_locations([test_article])
        
        if processed and processed[0].get('locations'):
            locations = processed[0]['locations']
            print(f"✅ Found {len(locations)} geographic entities")
            
            for loc in locations[:3]:
                print(f"   • {loc.get('text', 'Unknown')}: {loc.get('found_name', 'Not geocoded')}")
            
            geocoded_count = sum(1 for loc in locations if loc.get('geocoded', False))
            print(f"   Geocoded: {geocoded_count}/{len(locations)}")
            
            return geocoded_count > 0
        else:
            print("❌ No geographic entities found")
            return False
            
    except Exception as e:
        print(f"❌ Error testing geographic processing: {e}")
        print("💡 This may require: pip install spacy geopy")
        return False

def create_simple_map():
    """Create a simple map with real data (without AI classification)"""
    try:
        from argus.data_ingestion import get_crisis_articles
        from argus.geo_extractor import extract_article_locations
        import folium
        
        print("\n🗺️  Creating simple crisis map...")
        print("=" * 50)
        
        # Fetch articles
        articles = get_crisis_articles(hours_back=24, use_cache=False, prefer_rss=True)
        
        if not articles:
            print("❌ No articles to map")
            return False
        
        # Process geographic entities for first few articles
        mappable_articles = []
        for article in articles[:5]:  # Limit to avoid processing too many
            try:
                processed = extract_article_locations([article])
                if processed and processed[0].get('locations'):
                    article['locations'] = processed[0]['locations']
                    mappable_articles.append(article)
            except:
                continue
        
        if not mappable_articles:
            print("❌ No articles with geographic data")
            return False
        
        # Create simple map
        m = folium.Map(location=[20, 0], zoom_start=2)
        
        marker_count = 0
        for article in mappable_articles:
            for location in article.get('locations', []):
                if location.get('geocoded', False):
                    lat = location.get('latitude')
                    lon = location.get('longitude')
                    
                    if lat and lon:
                        # Determine if this is real or demo data
                        is_real = not article['url'].startswith('https://example.com')
                        color = 'green' if is_real else 'red'
                        
                        folium.Marker(
                            [lat, lon],
                            popup=f"{'[REAL]' if is_real else '[DEMO]'} {article['title'][:50]}...",
                            tooltip=f"{article['source']}: {location.get('found_name', 'Unknown')}",
                            icon=folium.Icon(color=color)
                        ).add_to(m)
                        
                        marker_count += 1
        
        # Save map
        map_file = "test_real_data_map.html"
        m.save(map_file)
        
        print(f"✅ Created map with {marker_count} markers")
        print(f"   Green markers: Real crisis data")
        print(f"   Red markers: Demo data")
        print(f"   Saved to: {map_file}")
        
        return marker_count > 0
        
    except Exception as e:
        print(f"❌ Error creating map: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Real Crisis Data Pipeline")
    print("=" * 60)
    
    # Test data fetching
    data_success = test_data_fetching()
    
    # Test geographic processing
    geo_success = test_geographic_processing()
    
    # Create simple map
    map_success = create_simple_map()
    
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY:")
    print(f"   Data Fetching: {'✅ PASS' if data_success else '❌ FAIL'}")
    print(f"   Geographic Processing: {'✅ PASS' if geo_success else '❌ FAIL'}")
    print(f"   Map Creation: {'✅ PASS' if map_success else '❌ FAIL'}")
    
    if data_success:
        print("\n🎉 REAL DATA INTEGRATION WORKING!")
        print("   Your crisis monitor is now fetching real news instead of demo data.")
        print("   To run the full pipeline: pip install -r requirements.txt")
        if map_success:
            print("   Open test_real_data_map.html to see the results!")
    else:
        print("\n⚠️  Real data integration needs debugging.")
        print("   Check internet connection and RSS feed availability.")

if __name__ == "__main__":
    main()
