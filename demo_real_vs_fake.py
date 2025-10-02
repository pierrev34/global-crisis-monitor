#!/usr/bin/env python3
"""
Demonstration script showing the difference between real and demo data
"""

import sys
import os
import json

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def show_real_vs_demo():
    """Show the difference between real and demo data"""
    
    print("🔍 CRISIS MONITOR: Real vs Demo Data Comparison")
    print("=" * 60)
    
    try:
        from argus.data_ingestion import get_crisis_articles
        
        # Get real data (RSS preferred)
        print("📡 Fetching REAL crisis data from RSS feeds...")
        real_articles = get_crisis_articles(
            hours_back=24, 
            use_cache=False, 
            prefer_rss=True
        )
        
        # Get demo data (force fallback)
        print("🎭 Getting DEMO crisis data...")
        from argus.data_ingestion import GDELTIngester
        ingester = GDELTIngester()
        demo_articles = ingester._get_demo_data()
        
        print("\n" + "=" * 60)
        print("📊 COMPARISON RESULTS")
        print("=" * 60)
        
        # Analyze real articles
        rss_articles = [a for a in real_articles if a.get('fetched_via') == 'rss']
        
        print(f"\n🌐 REAL DATA ({len(rss_articles)} articles):")
        if rss_articles:
            for i, article in enumerate(rss_articles[:3], 1):
                print(f"  {i}. {article['title']}")
                print(f"     Source: {article.get('source_name', article['source'])}")
                print(f"     URL: {article['url']}")
                print(f"     Type: ✅ REAL (clickable link)")
                print()
        else:
            print("  ❌ No real articles fetched (check internet connection)")
        
        print(f"🎭 DEMO DATA ({len(demo_articles)} articles):")
        for i, article in enumerate(demo_articles[:3], 1):
            print(f"  {i}. {article['title']}")
            print(f"     Source: {article['source']}")
            print(f"     URL: {article['url']}")
            print(f"     Type: ⚠️  SAMPLE (example.com)")
            print()
        
        # Summary
        print("=" * 60)
        print("📋 SUMMARY:")
        
        if rss_articles:
            print("✅ SUCCESS: Your crisis monitor is now using REAL crisis data!")
            print("   • Articles come from actual news sources")
            print("   • URLs are clickable and lead to real articles")
            print("   • Data reflects current global events")
            print("   • No more 'sample domain' messages")
        else:
            print("⚠️  FALLBACK: System is using demo data")
            print("   • Check internet connection")
            print("   • RSS feeds may be temporarily unavailable")
            print("   • System will retry real data on next run")
        
        print(f"\n🔄 Data Source Priority:")
        print(f"   1. RSS Feeds (Real news) → {'✅ WORKING' if rss_articles else '❌ FAILED'}")
        print(f"   2. GDELT API (Backup) → ⚠️  Limited")
        print(f"   3. Demo Data (Fallback) → ✅ Available")
        
        # Save comparison to file
        comparison = {
            'timestamp': str(sys.modules['datetime'].datetime.now()) if 'datetime' in sys.modules else 'unknown',
            'real_articles_count': len(rss_articles),
            'demo_articles_count': len(demo_articles),
            'real_articles': [
                {
                    'title': a['title'],
                    'source': a.get('source_name', a['source']),
                    'url': a['url'],
                    'type': 'real'
                } for a in rss_articles[:5]
            ],
            'demo_articles': [
                {
                    'title': a['title'],
                    'source': a['source'],
                    'url': a['url'],
                    'type': 'demo'
                } for a in demo_articles[:5]
            ]
        }
        
        with open('data_comparison.json', 'w') as f:
            json.dump(comparison, f, indent=2)
        
        print(f"\n💾 Comparison saved to: data_comparison.json")
        
        return len(rss_articles) > 0
        
    except Exception as e:
        print(f"❌ Error in comparison: {e}")
        return False

if __name__ == "__main__":
    success = show_real_vs_demo()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 REAL DATA INTEGRATION SUCCESSFUL!")
        print("Your crisis monitor will now show actual global events.")
    else:
        print("⚠️  Using demo data. Real integration needs debugging.")
    print("=" * 60)
