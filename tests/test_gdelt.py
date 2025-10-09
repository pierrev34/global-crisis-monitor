#!/usr/bin/env python3
"""
Test script to verify GDELT API integration
"""

import requests
import json
from datetime import datetime, timedelta

def test_gdelt_api():
    """Test the GDELT API with our crisis query"""
    
    # GDELT API configuration
    base_url = "http://api.gdeltproject.org/api/v2/doc/doc"
    
    # Calculate time range (last 24 hours)
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=24)
    
    params = {
        "query": "(earthquake OR flood OR hurricane OR wildfire OR tsunami OR drought OR famine OR war OR conflict OR refugee OR humanitarian OR economic crisis OR recession OR pandemic OR outbreak) AND (news OR breaking OR alert OR emergency) -game -gaming -video -mod",
        "mode": "artlist",
        "format": "json",
        "maxrecords": 10,
        "sort": "datedesc",
        "sourcelang": "english",
        "startdatetime": start_time.strftime("%Y%m%d%H%M%S"),
        "enddatetime": end_time.strftime("%Y%m%d%H%M%S")
    }
    
    try:
        print("🔍 Testing GDELT API...")
        print(f"Query: {params['query']}")
        print(f"Time range: {start_time} to {end_time}")
        print()
        
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        articles = data.get('articles', [])
        
        print(f"✅ Successfully fetched {len(articles)} articles")
        print()
        
        # Display first few articles
        for i, article in enumerate(articles[:5], 1):
            title = article.get('title', 'No title')
            url = article.get('url', 'No URL')
            domain = article.get('domain', 'No domain')
            language = article.get('language', 'Unknown')
            
            print(f"{i}. {title}")
            print(f"   Source: {domain}")
            print(f"   Language: {language}")
            print(f"   URL: {url}")
            print()
        
        # Check for gaming content
        gaming_count = 0
        for article in articles:
            title = article.get('title', '').lower()
            domain = article.get('domain', '').lower()
            if any(keyword in title or keyword in domain 
                   for keyword in ['game', 'gaming', 'mod', 'patch', '生化危机']):
                gaming_count += 1
        
        print(f"📊 Analysis:")
        print(f"   Total articles: {len(articles)}")
        print(f"   Gaming-related: {gaming_count}")
        print(f"   News articles: {len(articles) - gaming_count}")
        
        return len(articles) > 0 and (len(articles) - gaming_count) > 0
        
    except Exception as e:
        print(f"❌ Error testing GDELT API: {e}")
        return False

if __name__ == "__main__":
    success = test_gdelt_api()
    if success:
        print("\n🎉 GDELT API test successful! Real crisis data should now work.")
    else:
        print("\n⚠️ GDELT API test failed. System will use demo data.")
