#!/usr/bin/env python3
"""
ARGUS Example Script

Demonstrates how to use individual components of the ARGUS system
"""

import logging
from argus.data_ingestion import GDELTIngester
from argus.classifier import CrisisClassifier
from argus.geo_extractor import GeographicExtractor
from argus.mapper import CrisisMapper

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_data_ingestion():
    """Example of using the data ingestion module"""
    print("🔍 Example: Data Ingestion")
    print("-" * 40)
    
    ingester = GDELTIngester()
    
    # Fetch recent articles (limited for demo)
    articles = ingester.fetch_recent_articles(hours_back=6, max_articles=10)
    
    print(f"Fetched {len(articles)} articles")
    if articles:
        article = articles[0]
        print(f"Sample article: {article['title'][:100]}...")
        print(f"Source: {article['source']}")
        print(f"URL: {article['url']}")
    
    return articles


def example_classification(articles):
    """Example of using the classification module"""
    print("\n🤖 Example: Crisis Classification")
    print("-" * 40)
    
    if not articles:
        print("No articles to classify")
        return []
    
    classifier = CrisisClassifier()
    
    # Classify first few articles
    sample_articles = articles[:3]
    results = classifier.classify_batch(sample_articles)
    
    for result in results:
        article = result['article']
        category = result['predicted_category']
        confidence = result['confidence']
        
        print(f"\nTitle: {article['title'][:80]}...")
        print(f"Category: {category} (confidence: {confidence:.2f})")
        print(f"Is Crisis: {result['is_crisis']}")
    
    return results


def example_geo_extraction(articles):
    """Example of using the geographic extraction module"""
    print("\n🌍 Example: Geographic Entity Extraction")
    print("-" * 40)
    
    if not articles:
        print("No articles to process")
        return []
    
    extractor = GeographicExtractor()
    
    # Process first article
    sample_article = articles[0]
    enhanced_article = extractor.process_article_locations(sample_article)
    
    print(f"Article: {enhanced_article['title'][:80]}...")
    print(f"Locations found: {enhanced_article['location_count']}")
    print(f"Successfully geocoded: {enhanced_article['geocoded_count']}")
    
    for location in enhanced_article.get('locations', []):
        print(f"  • {location['text']}: {location.get('found_name', 'Not geocoded')}")
        if location.get('geocoded'):
            print(f"    Coordinates: ({location['latitude']:.4f}, {location['longitude']:.4f})")
    
    return [enhanced_article]


def example_mapping(crisis_data):
    """Example of creating a crisis map"""
    print("\n🗺️  Example: Crisis Mapping")
    print("-" * 40)
    
    if not crisis_data:
        print("No crisis data to map")
        return
    
    mapper = CrisisMapper()
    
    # Create a simple map with the data
    map_file = mapper.create_crisis_map(
        crisis_data, 
        output_file="example_map.html",
        include_heatmap=False,  # Disable for small dataset
        include_statistics=True
    )
    
    print(f"Example map created: {map_file}")
    print("Open the HTML file in your browser to view the map!")


def run_examples():
    """Run all examples"""
    print("🌍 ARGUS System Examples")
    print("=" * 50)
    
    try:
        # 1. Data Ingestion
        articles = example_data_ingestion()
        
        # 2. Classification
        classification_results = example_classification(articles)
        
        # 3. Geographic Extraction
        enhanced_articles = example_geo_extraction(articles)
        
        # 4. Create sample crisis data for mapping
        if classification_results and enhanced_articles:
            # Combine classification and location data
            sample_crisis_data = []
            for i, result in enumerate(classification_results[:1]):  # Just first result
                if i < len(enhanced_articles):
                    combined_result = result.copy()
                    combined_result['article'] = enhanced_articles[i]
                    sample_crisis_data.append(combined_result)
            
            # 5. Mapping
            example_mapping(sample_crisis_data)
        
        print("\n🎉 All examples completed successfully!")
        
    except Exception as e:
        logger.error(f"Example failed: {e}")
        print(f"\n❌ Example failed: {e}")


if __name__ == "__main__":
    run_examples()
