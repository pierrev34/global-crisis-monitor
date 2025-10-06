#!/usr/bin/env python3
"""
ARGUS - Global Crisis Monitor (Enhanced v2.0)
Main Pipeline Orchestrator

This script orchestrates the complete pipeline:
1. Fetch crisis articles from diverse sources (NGOs, human rights orgs, media)
2. Classify using rule-based system (no LLM needed)
3. Extract geographic entities
4. Create interactive crisis map with comprehensive global coverage
"""

import argparse
import logging
import json
import sys
import time
from datetime import datetime
from pathlib import Path

# Import ARGUS modules - Enhanced v2
from argus.rss_fetcher_v2 import fetch_crisis_news
from argus.simple_classifier import classify_crisis_articles, get_crisis_summary
from argus.geo_extractor import extract_article_locations
from argus.mapper import create_crisis_visualization
from argus.config import OUTPUT_MAP_FILE

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('argus.log')
    ]
)
logger = logging.getLogger(__name__)


def run_crisis_monitor(hours_back: int = 168, 
                      max_articles: int = 150,
                      confidence_threshold: float = 0.3,
                      output_file: str = None) -> str:
    """
    Run the enhanced ARGUS crisis monitoring pipeline (v2.0)
    
    Args:
        hours_back: How many hours back to search (default 168 = 7 days for ongoing crises)
        max_articles: Maximum number of articles to process
        confidence_threshold: Minimum confidence for crisis classification
        output_file: Optional custom output file path
    
    Returns:
        Path to generated crisis map
    """
    start_time = time.time()
    
    logger.info("🚀 Starting Enhanced Global Crisis Monitor Pipeline v2.0")
    logger.info(f"📊 Configuration: hours_back={hours_back}, max_articles={max_articles}, "
                f"confidence_threshold={confidence_threshold}")
    logger.info(f"✨ NEW: Using diverse sources (NGOs, human rights orgs, regional media)")
    logger.info(f"⚡ NEW: Fast rule-based classification (no LLM overhead)")
    
    try:
        # Step 1: Fetch from Diverse Sources
        logger.info(f"📰 Step 1: Fetching from 15+ diverse crisis sources...")
        logger.info(f"  • Human Rights: HRW, Amnesty International, UN OCHA")
        logger.info(f"  • Humanitarian: ReliefWeb, UNHCR, MSF, ICRC")
        logger.info(f"  • Regional: Radio Free Asia, Middle East Eye, Al Jazeera")
        logger.info(f"  • Disasters: GDACS, USGS Earthquakes")
        
        articles = fetch_crisis_news(max_articles=max_articles, hours_back=hours_back)
        
        if not articles:
            logger.error("No articles found. Exiting pipeline.")
            return None
        
        logger.info(f"✅ Fetched {len(articles)} articles from {len(set(a['source_name'] for a in articles))} sources")
        
        # Step 2: Rule-Based Classification (No LLM)
        logger.info("🤖 Step 2: Classifying articles (rule-based, no LLM)...")
        classification_results = classify_crisis_articles(articles)
        
        # Filter to only crisis articles
        crisis_articles = [
            result for result in classification_results 
            if result.get('is_crisis', False) and result.get('confidence', 0) >= confidence_threshold
        ]
        
        classification_summary = get_crisis_summary(classification_results)
        logger.info(f"✅ Classified {len(classification_results)} articles, "
                   f"found {len(crisis_articles)} crisis-related")
        logger.info(f"   Category breakdown: {classification_summary.get('category_distribution', {})}")
        
        # Step 3: Geographic Entity Extraction
        logger.info("🌍 Step 3: Extracting geographic entities...")
        
        # Extract all articles at once for better batching efficiency
        crisis_article_list = [result['article'] for result in crisis_articles]
        enhanced_article_list = extract_article_locations(crisis_article_list)
        
        # Combine classification and location data
        enhanced_articles = []
        for i, crisis_result in enumerate(crisis_articles):
            enhanced_crisis_result = crisis_result.copy()
            enhanced_crisis_result['article'] = enhanced_article_list[i]
            enhanced_articles.append(enhanced_crisis_result)
        
        # Filter to articles with geocoded locations, but be more flexible
        mappable_articles = [
            result for result in enhanced_articles
            if result['article'].get('geocoded_count', 0) > 0
        ]
        
        # If no perfectly geocoded articles, use intelligent fallbacks
        if not mappable_articles and enhanced_articles:
            logger.info("No perfectly geocoded articles found. Using intelligent fallbacks...")
            mappable_articles = enhanced_articles  # Use all articles with fallback logic
        
        logger.info(f"✅ Processed geographic entities, "
                   f"{len(mappable_articles)} articles available for mapping")
        
        # Step 4: Create Interactive Map
        logger.info("🗺️  Step 4: Creating interactive crisis map...")
        
        if not mappable_articles:
            logger.warning("No articles available for mapping. Cannot create map.")
            return None
        
        map_file = create_crisis_visualization(
            mappable_articles, 
            output_file or OUTPUT_MAP_FILE
        )
        
        logger.info(f"✅ Created interactive map: {map_file}")
        
        # Step 5: Generate Summary Report
        logger.info("📊 Step 5: Generating summary report...")
        
        summary = generate_pipeline_summary(
            articles, classification_results, enhanced_articles, mappable_articles
        )
        
        # Save summary to file
        summary_file = "crisis_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
        
        # Print summary to console
        print_pipeline_summary(summary)
        
        # Calculate total runtime
        total_time = time.time() - start_time
        logger.info(f"🎉 Pipeline completed successfully in {total_time:.2f} seconds")
        logger.info(f"📋 Summary saved to: {summary_file}")
        logger.info(f"🗺️  Interactive map: {map_file}")
        
        return map_file
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed with error: {e}")
        import traceback
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        raise

def generate_pipeline_summary(articles: list, 
                            classification_results: list,
                            enhanced_articles: list, 
                            mappable_articles: list) -> dict:
    """Generate a comprehensive summary of the pipeline results"""
    
    # Count unique sources
    unique_sources = len(set(a.get('source_name', 'Unknown') for a in articles))
    
    # Basic statistics
    summary = {
        'timestamp': datetime.now().isoformat(),
        'pipeline_stats': {
            'total_articles_fetched': len(articles),
            'unique_sources': unique_sources,
            'articles_classified': len(classification_results),
            'crisis_articles_found': len([r for r in classification_results if r.get('is_crisis', False)]),
            'mappable_crisis_articles': len(mappable_articles)
        }
    }
    
    # Classification statistics
    category_counts = {}
    total_confidence = 0
    
    for result in classification_results:
        category = result.get('predicted_category', 'Unknown')
        category_counts[category] = category_counts.get(category, 0) + 1
        total_confidence += result.get('confidence', 0)
    
    summary['classification_stats'] = {
        'category_distribution': category_counts,
        'average_confidence': total_confidence / len(classification_results) if classification_results else 0
    }
    
    # Geographic statistics
    total_locations = 0
    geocoded_locations = 0
    unique_countries = set()
    
    for result in enhanced_articles:
        article = result['article']
        locations = article.get('locations', [])
        total_locations += len(locations)
        
        for location in locations:
            if location.get('geocoded', False):
                geocoded_locations += 1
                # Try to extract country from address
                address = location.get('found_name', '')
                # Ensure address is a string
                if address and isinstance(address, str):
                    # Simple heuristic to extract country (last part of address)
                    parts = address.split(', ')
                    if parts:
                        unique_countries.add(parts[-1])
    
    summary['geographic_stats'] = {
        'total_locations_extracted': total_locations,
        'successfully_geocoded': geocoded_locations,
        'geocoding_success_rate': geocoded_locations / total_locations if total_locations > 0 else 0,
        'unique_countries_affected': len(unique_countries),
        'countries_list': sorted(list(unique_countries))
    }
    
    # Top crisis locations
    location_counts = {}
    for result in mappable_articles:
        article = result['article']
        for location in article.get('locations', []):
            if location.get('geocoded', False):
                name = location.get('found_name', location.get('text', 'Unknown'))
                # Ensure name is a string
                if not isinstance(name, str):
                    name = str(name) if name is not None else 'Unknown'
                location_counts[name] = location_counts.get(name, 0) + 1
    
    top_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    summary['top_crisis_locations'] = top_locations
    
    return summary


def print_pipeline_summary(summary: dict):
    """Print a formatted summary to the console"""
    
    print("\n" + "="*70)
    print("🌍 ENHANCED GLOBAL CRISIS MONITOR v2.0 - PIPELINE SUMMARY")
    print("="*70)
    
    stats = summary['pipeline_stats']
    print(f"\n📊 PROCESSING STATISTICS:")
    print(f"   • Articles fetched: {stats['total_articles_fetched']}")
    print(f"   • Unique sources: {stats.get('unique_sources', 'N/A')}")
    print(f"   • Articles classified: {stats['articles_classified']}")
    print(f"   • Crisis articles found: {stats['crisis_articles_found']}")
    print(f"   • Mappable crisis articles: {stats['mappable_crisis_articles']}")
    print(f"   • NGO/Human Rights sources: HRW, Amnesty, UNHCR, ReliefWeb, MSF, etc.")
    
    class_stats = summary['classification_stats']
    print(f"\n🤖 CLASSIFICATION RESULTS (Rule-Based, No LLM):")
    print(f"   • Average confidence: {class_stats['average_confidence']:.2f}")
    print(f"   • Category distribution:")
    # Sort by count descending
    for category, count in sorted(class_stats['category_distribution'].items(), 
                                   key=lambda x: x[1], reverse=True):
        if count > 0:  # Only show categories with articles
            print(f"     - {category}: {count}")
    
    geo_stats = summary['geographic_stats']
    print(f"\n🌍 GEOGRAPHIC ANALYSIS:")
    print(f"   • Locations extracted: {geo_stats['total_locations_extracted']}")
    print(f"   • Successfully geocoded: {geo_stats['successfully_geocoded']}")
    print(f"   • Geocoding success rate: {geo_stats['geocoding_success_rate']:.1%}")
    print(f"   • Countries affected: {geo_stats['unique_countries_affected']}")
    
    if summary['top_crisis_locations']:
        print(f"\n🔥 TOP CRISIS LOCATIONS:")
        for i, (location, count) in enumerate(summary['top_crisis_locations'][:8], 1):
            print(f"   {i}. {location}: {count} incidents")
    
    print("\n" + "="*70)


def main():
    """Main entry point with command line argument parsing"""
    
    parser = argparse.ArgumentParser(
        description="Enhanced Global Crisis Monitor v2.0 - NGO & Human Rights Focused",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                          # Run with default settings (7 days, 150 articles)
  python main.py --hours 336 --max 200    # Fetch 2 weeks of data, max 200 articles
  python main.py --confidence 0.2         # Lower threshold for broader coverage
        """
    )
    
    parser.add_argument(
        '--hours', type=int, default=168,
        help='Hours back to search for articles (default: 168 = 7 days for ongoing crises)'
    )
    
    parser.add_argument(
        '--max-articles', '-m', type=int, default=150,
        help='Maximum number of articles to process (default: 150)'
    )
    
    parser.add_argument(
        '--confidence', '-c', type=float, default=0.3,
        help='Minimum confidence threshold for crisis classification (default: 0.3)'
    )
    
    parser.add_argument(
        '--output', '-o', type=str, default=None,
        help='Output HTML file for the crisis map (default: crisis_map.html)'
    )
    
    parser.add_argument(
        '--verbose', '-v', action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Run the enhanced pipeline
        map_file = run_crisis_monitor(
            hours_back=args.hours,
            max_articles=args.max_articles,
            confidence_threshold=args.confidence,
            output_file=args.output
        )
        
        if map_file:
            print(f"\n🎉 Success! Open {map_file} in your browser to view the crisis map.")
        else:
            print("\n⚠️  No crisis map generated. Check the logs for details.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
