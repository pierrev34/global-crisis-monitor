"""
AI-Powered Crisis Classification Module

Uses Hugging Face transformers for zero-shot classification of news articles
into crisis categories.
"""

import logging
from typing import List, Dict, Tuple, Optional
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
from .config import CRISIS_CATEGORIES, CLASSIFICATION_MODEL

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CrisisClassifier:
    """Zero-shot classifier for crisis categorization using transformers"""
    
    def __init__(self, model_name: str = None):
        """
        Initialize the crisis classifier
        
        Args:
            model_name: Name of the Hugging Face model to use
        """
        self.model_name = model_name or CLASSIFICATION_MODEL
        self.categories = CRISIS_CATEGORIES
        self.classifier = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"Initializing CrisisClassifier with model: {self.model_name}")
        logger.info(f"Using device: {self.device}")
        
        self._load_model()
    
    def _load_model(self):
        """Load the classification model and tokenizer"""
        try:
            logger.info("Loading classification model...")
            self.classifier = pipeline(
                "zero-shot-classification",
                model=self.model_name,
                device=0 if self.device == "cuda" else -1,
                return_all_scores=True
            )
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def classify_article(self, article: Dict, confidence_threshold: float = 0.3) -> Dict:
        """
        Classify a single article into crisis categories
        
        Args:
            article: Article dictionary with 'title' and 'content' keys
            confidence_threshold: Minimum confidence score for classification
            
        Returns:
            Dictionary with classification results
        """
        try:
            # Prepare text for classification (combine title and content)
            title = article.get('title', '')
            content = article.get('content', '')
            
            # Truncate content if too long (model has token limits)
            max_length = 1000  # Adjust based on model capacity
            if len(content) > max_length:
                content = content[:max_length] + "..."
            
            text = f"{title}. {content}".strip()
            
            if not text:
                logger.warning("Empty text for classification")
                return self._create_classification_result(article, "Unknown", 0.0, {})
            
            # Perform zero-shot classification
            result = self.classifier(text, self.categories)
            
            # Extract top prediction
            top_label = result['labels'][0]
            top_score = result['scores'][0]
            
            # Create score dictionary for all categories
            all_scores = dict(zip(result['labels'], result['scores']))
            
            # Check if confidence meets threshold
            if top_score < confidence_threshold:
                top_label = "Unknown"
                top_score = 0.0

            return self._create_classification_result(
                article, top_label, top_score, all_scores, confidence_threshold
            )
            
        except Exception as e:
            logger.error(f"Error classifying article: {e}")
            return self._create_classification_result(article, "Error", 0.0, {})
    
    def classify_batch(self, articles: List[Dict], 
                      confidence_threshold: float = 0.3,
                      batch_size: int = 8) -> List[Dict]:
        """
        Classify multiple articles in batches
        
        Args:
            articles: List of article dictionaries
            confidence_threshold: Minimum confidence for classification
            batch_size: Number of articles to process at once
            
        Returns:
            List of classification results
        """
        results = []
        total_articles = len(articles)
        
        logger.info(f"Classifying {total_articles} articles in batches of {batch_size}")
        
        for i in range(0, total_articles, batch_size):
            batch = articles[i:i + batch_size]
            batch_results = []
            
            for article in batch:
                result = self.classify_article(article, confidence_threshold)
                batch_results.append(result)
            
            results.extend(batch_results)
            
            # Log progress
            processed = min(i + batch_size, total_articles)
            logger.info(f"Processed {processed}/{total_articles} articles")
        
        return results
    
    def _create_classification_result(self, article: Dict, category: str, 
                                    confidence: float, all_scores: Dict,
                                    min_confidence: float = 0.3) -> Dict:
        """Create standardized classification result"""
        return {
            'article': article,
            'predicted_category': category,
            'confidence': confidence,
            'all_scores': all_scores,
            'is_crisis': (
                category in self.categories and
                category != "Unknown" and
                confidence >= min_confidence
            ),
            'classification_metadata': {
                'model_used': self.model_name,
                'categories_available': self.categories,
                'device_used': self.device,
                'min_confidence': min_confidence
            }
        }
    
    def get_category_statistics(self, classification_results: List[Dict]) -> Dict:
        """
        Generate statistics about classification results
        
        Args:
            classification_results: List of classification results
            
        Returns:
            Dictionary with statistics
        """
        stats = {
            'total_articles': len(classification_results),
            'category_counts': {},
            'average_confidence': 0.0,
            'crisis_articles': 0,
            'unknown_articles': 0
        }
        
        total_confidence = 0.0
        
        for result in classification_results:
            category = result['predicted_category']
            confidence = result['confidence']
            
            # Count categories
            stats['category_counts'][category] = stats['category_counts'].get(category, 0) + 1
            
            # Track crisis vs non-crisis
            if result['is_crisis']:
                stats['crisis_articles'] += 1
            elif category == "Unknown":
                stats['unknown_articles'] += 1
            
            total_confidence += confidence
        
        # Calculate average confidence
        if classification_results:
            stats['average_confidence'] = total_confidence / len(classification_results)
        
        return stats
    
    def filter_crisis_articles(self, classification_results: List[Dict], 
                             min_confidence: float = 0.5) -> List[Dict]:
        """
        Filter results to only include high-confidence crisis articles
        
        Args:
            classification_results: List of classification results
            min_confidence: Minimum confidence threshold
            
        Returns:
            Filtered list of crisis articles
        """
        crisis_articles = []
        
        for result in classification_results:
            if (result['is_crisis'] and 
                result['confidence'] >= min_confidence and
                result['predicted_category'] != "Unknown"):
                
                crisis_articles.append(result)
        
        logger.info(f"Filtered to {len(crisis_articles)} high-confidence crisis articles")
        return crisis_articles


def classify_crisis_articles(articles: List[Dict], 
                           confidence_threshold: float = 0.3,
                           model_name: str = None) -> List[Dict]:
    """
    Convenience function to classify articles
    
    Args:
        articles: List of article dictionaries
        confidence_threshold: Minimum confidence for classification
        model_name: Optional custom model name
        
    Returns:
        List of classification results
    """
    classifier = CrisisClassifier(model_name)
    return classifier.classify_batch(articles, confidence_threshold)


def get_crisis_summary(classification_results: List[Dict]) -> Dict:
    """
    Get a summary of crisis classifications
    
    Args:
        classification_results: List of classification results
        
    Returns:
        Summary statistics
    """
    classifier = CrisisClassifier()
    return classifier.get_category_statistics(classification_results)
