#!/usr/bin/env python3
"""
Test RSS integration without requiring all dependencies
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_rss_fetcher():
    """Test the RSS fetcher directly"""
    try:
        from argus.rss_fetcher import get_real_crisis_news
        
        print("🔍 Testing RSS crisis news fetcher...")
        articles = get_real_crisis_news(max_articles=5, hours_back=48)
        
        if articles:
            print(f"✅ Successfully fetched {len(articles)} real crisis articles!")
            print()
            
            for i, article in enumerate(articles, 1):
                print(f"{i}. {article['title']}")
                print(f"   Source: {article.get('source_name', article['source'])}")
                print(f"   URL: {article['url']}")
                print(f"   Published: {article.get('published_date', 'Unknown')}")
                print()
            
            # Check if these are real articles (not example.com)
            real_articles = [a for a in articles if not a['url'].startswith('https://example.com')]
            print(f"📊 Analysis:")
            print(f"   Total articles: {len(articles)}")
            print(f"   Real articles: {len(real_articles)}")
            print(f"   Demo articles: {len(articles) - len(real_articles)}")
            
            return len(real_articles) > 0
        else:
            print("❌ No articles fetched from RSS feeds")
            return False
            
    except ImportError as e:
        print(f"❌ RSS fetcher not available: {e}")
        print("💡 Try: pip install feedparser")
        return False
    except Exception as e:
        print(f"❌ Error testing RSS fetcher: {e}")
        return False

def test_integration():
    """Test the integrated data ingestion"""
    try:
        from argus.data_ingestion import get_crisis_articles
        
        print("\n🔗 Testing integrated data ingestion...")
        articles = get_crisis_articles(hours_back=24, use_cache=False, prefer_rss=True)
        
        if articles:
            print(f"✅ Successfully fetched {len(articles)} articles through integration!")
            
            # Check data source
            rss_articles = [a for a in articles if a.get('fetched_via') == 'rss']
            demo_articles = [a for a in articles if a['url'].startswith('https://example.com')]
            
            print(f"📊 Data source analysis:")
            print(f"   RSS articles: {len(rss_articles)}")
            print(f"   Demo articles: {len(demo_articles)}")
            print(f"   Other sources: {len(articles) - len(rss_articles) - len(demo_articles)}")
            
            if rss_articles:
                print("\n🎉 SUCCESS: Real crisis news is now being fetched!")
                print("   Your map will now show real crisis events instead of demo data.")
            elif demo_articles:
                print("\n⚠️  Still using demo data. RSS fetching may have failed.")
            
            return len(rss_articles) > 0
        else:
            print("❌ No articles fetched through integration")
            return False
            
    except Exception as e:
        print(f"❌ Error testing integration: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Real Crisis News Integration")
    print("=" * 50)
    
    # Test RSS fetcher directly
    rss_success = test_rss_fetcher()
    
    # Test integration
    integration_success = test_integration()
    
    print("\n" + "=" * 50)
    if rss_success and integration_success:
        print("🎉 ALL TESTS PASSED!")
        print("Your crisis monitor will now use real crisis news instead of demo data.")
        print("Run: python3 main.py --no-cache --verbose")
    elif rss_success:
        print("⚠️  RSS works but integration needs debugging")
        print("Install dependencies: pip install -r requirements.txt")
    else:
        print("❌ RSS fetching failed")
        print("Install feedparser: pip install feedparser")
        print("Check internet connection and RSS feed availability")
