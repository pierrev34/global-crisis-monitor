#!/usr/bin/env python3
"""
Global Crisis Monitor Demo Script

A comprehensive demonstration of the Global Crisis Monitor system.
This script shows the capabilities of each component and creates a sample
crisis map for portfolio demonstration.
"""

import logging
import json
from datetime import datetime
from argus.data_ingestion import GDELTIngester
from argus.classifier import CrisisClassifier
from argus.geo_extractor import GeographicExtractor
from argus.mapper import CrisisMapper

# Set up logging for demo
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def create_sample_data():
    """Create minimal sample data for demonstration when GDELT is unavailable"""
    return [
        {
            'title': 'Earthquake Strikes Turkey, Magnitude 7.2',
            'content': 'A powerful earthquake struck Turkey causing significant damage. Emergency services are responding with international aid.',
            'url': 'https://example.com/turkey-earthquake',
            'source': 'reuters.com',
            'published_date': '20241001120000',
            'language': 'en',
            'tone': -5.2
        },
        {
            'title': 'Humanitarian Crisis in Sudan',
            'content': 'The ongoing conflict in Sudan has created a severe humanitarian crisis with over 2 million displaced.',
            'url': 'https://example.com/sudan-crisis',
            'source': 'bbc.com',
            'published_date': '20241001100000',
            'language': 'en',
            'tone': -7.8
        }
    ]


def demo_data_ingestion():
    """Demonstrate the data ingestion capabilities"""
    print("\n" + "="*60)
    print("🔍 DEMO: Data Ingestion from GDELT")
    print("="*60)
    
    ingester = GDELTIngester()
    
    try:
        # Try to fetch real data first
        print("Attempting to fetch real-time data from GDELT...")
        articles = ingester.fetch_recent_articles(hours_back=6, max_articles=5)
        
        if not articles:
            print("No real-time data available, using sample data for demonstration...")
            articles = create_sample_data()
        else:
            print(f"✅ Successfully fetched {len(articles)} real articles from GDELT")
    
    except Exception as e:
        print(f"⚠️  GDELT unavailable ({e}), using sample data for demonstration...")
        articles = create_sample_data()
    
    print(f"\n📊 Data Summary:")
    print(f"   • Total articles: {len(articles)}")
    print(f"   • Sample article: {articles[0]['title'][:60]}...")
    print(f"   • Sources: {', '.join(set(a['source'] for a in articles))}")
    
    return articles


def demo_classification(articles):
    """Demonstrate AI-powered crisis classification"""
    print("\n" + "="*60)
    print("🤖 DEMO: AI-Powered Crisis Classification")
    print("="*60)
    
    try:
        # Use singleton instance to avoid model reloading
        from argus.classifier import get_classifier_instance
        classifier = get_classifier_instance()
        print("✅ AI classification model loaded successfully")
        
        print("\nClassifying articles...")
        results = classifier.classify_batch(articles, confidence_threshold=0.2)
        
        print(f"\n📊 Classification Results:")
        category_counts = {}
        for result in results:
            category = result['predicted_category']
            category_counts[category] = category_counts.get(category, 0) + 1
            
            print(f"\n📰 {result['article']['title'][:50]}...")
            print(f"   Category: {category}")
            print(f"   Confidence: {result['confidence']:.2f}")
            print(f"   Is Crisis: {'✅' if result['is_crisis'] else '❌'}")
        
        print(f"\n📈 Category Distribution:")
        for category, count in category_counts.items():
            print(f"   • {category}: {count}")
        
        return results
        
    except Exception as e:
        print(f"❌ Classification demo failed: {e}")
        print("This might be due to model download requirements or memory constraints.")
        return []


def demo_geographic_extraction(articles):
    """Demonstrate geographic entity extraction and geocoding"""
    print("\n" + "="*60)
    print("🌍 DEMO: Geographic Entity Extraction")
    print("="*60)
    
    try:
        # Use singleton instance to avoid model reloading
        from argus.geo_extractor import get_extractor_instance
        extractor = get_extractor_instance()
        print("✅ Geographic extraction model loaded successfully")
        
        print("\nExtracting locations from articles...")
        enhanced_articles = extractor.process_batch_locations(articles)
        
        total_locations = 0
        geocoded_locations = 0
        
        for article in enhanced_articles:
            locations = article.get('locations', [])
            total_locations += len(locations)
            
            print(f"\n📍 {article['title'][:50]}...")
            print(f"   Locations found: {len(locations)}")
            
            for location in locations[:3]:  # Show first 3 locations
                if location.get('geocoded'):
                    geocoded_locations += 1
                    print(f"   • {location['text']} → {location['found_name']}")
                    print(f"     Coordinates: ({location['latitude']:.4f}, {location['longitude']:.4f})")
                else:
                    print(f"   • {location['text']} (not geocoded)")
        
        print(f"\n📊 Geographic Summary:")
        print(f"   • Total locations extracted: {total_locations}")
        print(f"   • Successfully geocoded: {geocoded_locations}")
        if total_locations > 0:
            success_rate = geocoded_locations / total_locations * 100
            print(f"   • Geocoding success rate: {success_rate:.1f}%")
        
        return enhanced_articles
        
    except Exception as e:
        print(f"❌ Geographic extraction demo failed: {e}")
        print("This might be due to spaCy model requirements or network issues.")
        return articles


def demo_crisis_mapping(crisis_data):
    """Demonstrate interactive crisis map creation"""
    print("\n" + "="*60)
    print("🗺️  DEMO: Interactive Crisis Map Creation")
    print("="*60)
    
    try:
        mapper = CrisisMapper()
        print("✅ Crisis mapper initialized successfully")
        
        # Filter to only articles with locations for mapping
        mappable_data = []
        for item in crisis_data:
            article = item if isinstance(item, dict) and 'locations' in item else item.get('article', {})
            if article.get('geocoded_count', 0) > 0:
                if isinstance(item, dict) and 'predicted_category' in item:
                    mappable_data.append(item)
                else:
                    # Create a mock classification result for demo
                    mock_result = {
                        'article': article,
                        'predicted_category': 'Natural Disasters',  # Default for demo
                        'confidence': 0.8,
                        'is_crisis': True,
                        'all_scores': {'Natural Disasters': 0.8}
                    }
                    mappable_data.append(mock_result)
        
        if mappable_data:
            print(f"Creating map with {len(mappable_data)} crisis locations...")
            
            map_file = mapper.create_crisis_map(
                mappable_data,
                output_file="demo_crisis_map.html",
                include_heatmap=len(mappable_data) > 2,
                include_statistics=True
            )
            
            print(f"✅ Interactive crisis map created: {map_file}")
            print("🌐 Open the HTML file in your browser to explore the map!")
            
            return map_file
        else:
            print("⚠️  No mappable crisis locations found for demonstration")
            return None
            
    except Exception as e:
        print(f"❌ Crisis mapping demo failed: {e}")
        return None


def create_demo_summary(articles, classification_results, enhanced_articles, map_file):
    """Create a summary of the demonstration"""
    print("\n" + "="*60)
    print("📋 DEMO SUMMARY")
    print("="*60)
    
    summary = {
        'demo_timestamp': datetime.now().isoformat(),
        'articles_processed': len(articles),
        'classifications_completed': len(classification_results) if classification_results else 0,
        'locations_extracted': sum(len(a.get('locations', [])) for a in enhanced_articles),
        'geocoded_locations': sum(a.get('geocoded_count', 0) for a in enhanced_articles),
        'map_generated': map_file is not None,
        'map_file': map_file
    }
    
    print(f"📊 Processing Statistics:")
    print(f"   • Articles processed: {summary['articles_processed']}")
    print(f"   • Classifications completed: {summary['classifications_completed']}")
    print(f"   • Locations extracted: {summary['locations_extracted']}")
    print(f"   • Locations geocoded: {summary['geocoded_locations']}")
    print(f"   • Map generated: {'✅' if summary['map_generated'] else '❌'}")
    
    if classification_results:
        crisis_count = sum(1 for r in classification_results if r.get('is_crisis', False))
        print(f"   • Crisis articles identified: {crisis_count}")
    
    # Save summary
    with open('demo_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n📄 Demo summary saved to: demo_summary.json")
    
    return summary


def main():
    """Run the complete Global Crisis Monitor demonstration"""
    print("🌍 Global Crisis Monitor")
    print("🎯 COMPREHENSIVE SYSTEM DEMONSTRATION")
    print("="*60)
    print("This demo showcases all components of the Global Crisis Monitor system:")
    print("• Real-time data ingestion from GDELT")
    print("• AI-powered crisis classification")
    print("• Geographic entity extraction and geocoding")
    print("• Interactive crisis map visualization")
    print("="*60)
    
    try:
        # Step 1: Data Ingestion
        articles = demo_data_ingestion()
        
        # Step 2: Crisis Classification
        classification_results = demo_classification(articles)
        
        # Step 3: Geographic Extraction
        enhanced_articles = demo_geographic_extraction(articles)
        
        # Step 4: Crisis Mapping
        crisis_data = classification_results if classification_results else enhanced_articles
        map_file = demo_crisis_mapping(crisis_data)
        
        # Step 5: Summary
        summary = create_demo_summary(articles, classification_results, enhanced_articles, map_file)
        
        print("\n" + "="*60)
        print("🎉 DEMONSTRATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\n🚀 Next Steps:")
        print("• Run 'python main.py' for the full pipeline")
        print("• Check 'python main.py --help' for options")
        print("• Read USAGE.md for detailed instructions")
        print("• Explore API.md for development guidance")
        
        if map_file:
            print(f"• Open {map_file} to see the crisis map!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
    except Exception as e:
        logger.error(f"Demo failed with error: {e}")
        print(f"\n❌ Demo encountered an error: {e}")
        print("Check the logs above for details.")


if __name__ == "__main__":
    main()
