"""
Simple Rule-Based Crisis Classifier
NO LLM NEEDED - Uses source trust + keyword matching

This is faster, more reliable, and better for underreported crises
than zero-shot classification which was trained on mainstream news.
"""

import logging
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)


class SimpleCrisisClassifier:
    """
    Rule-based classifier using source credibility + keyword matching
    Much faster than LLM and better for systemic/underreported crises
    """
    
    def __init__(self):
        # Category-specific keywords
        self.category_keywords = {
            'Natural Disasters': [
                'earthquake', 'quake', 'seismic', 'tsunami',
                'flood', 'flooding', 'hurricane', 'typhoon', 'cyclone',
                'wildfire', 'fire', 'blaze', 'volcano', 'volcanic', 'eruption',
                'landslide', 'mudslide', 'avalanche', 'drought',
                'storm', 'tornado', 'heatwave', 'cold snap'
            ],
            
            'Political Conflicts': [
                'war', 'conflict', 'fighting', 'battle', 'combat',
                'military', 'troops', 'invasion', 'occupation',
                'coup', 'regime', 'civil war', 'insurgency',
                'rebel', 'armed conflict', 'airstrike', 'bombing',
                'missile', 'artillery', 'ceasefire', 'peace talks'
            ],
            
            'Human Rights Violations': [
                'genocide', 'ethnic cleansing', 'persecution',
                'torture', 'extrajudicial', 'disappearance',
                'arbitrary detention', 'mass detention', 'concentration camp',
                'forced labor', 'slavery', 'human trafficking',
                'apartheid', 'discrimination', 'oppression',
                'atrocities', 'war crimes', 'crimes against humanity',
                'crackdown', 'repression', 'authoritarian'
            ],
            
            'Humanitarian Crises': [
                'refugee', 'displaced', 'internally displaced', 'idp',
                'humanitarian crisis', 'famine', 'starvation', 'malnutrition',
                'hunger crisis', 'food insecurity', 'aid', 'relief',
                'humanitarian aid', 'emergency response', 'evacuation',
                'shelter', 'asylum', 'migration crisis'
            ],
            
            'Health Emergencies': [
                'outbreak', 'epidemic', 'pandemic', 'disease',
                'virus', 'infection', 'contagious', 'cholera',
                'ebola', 'measles', 'malaria', 'tuberculosis',
                'polio', 'covid', 'coronavirus', 'health crisis',
                'medical emergency', 'hospital', 'healthcare collapse'
            ],
            
            'Economic Crises': [
                'economic crisis', 'recession', 'depression', 'collapse',
                'inflation', 'hyperinflation', 'unemployment', 'poverty',
                'financial crisis', 'debt crisis', 'bankruptcy',
                'economic collapse', 'market crash', 'currency'
            ],
            
            'Environmental Issues': [
                'climate crisis', 'global warming', 'climate change',
                'pollution', 'deforestation', 'biodiversity',
                'extinction', 'environmental disaster', 'toxic',
                'chemical spill', 'oil spill', 'contamination'
            ]
        }
        
        # Specific crisis zones and their primary issues
        self.crisis_zone_mapping = {
            'uyghur': 'Human Rights Violations',
            'xinjiang': 'Human Rights Violations',
            'uighur': 'Human Rights Violations',
            'el salvador': 'Human Rights Violations',
            'tigray': 'Humanitarian Crises',
            'yemen': 'Humanitarian Crises',
            'rohingya': 'Human Rights Violations',
            'myanmar': 'Human Rights Violations',
            'darfur': 'Human Rights Violations',
            'nagorno-karabakh': 'Political Conflicts',
            'west papua': 'Human Rights Violations',
            'gaza': 'Political Conflicts',
            'palestine': 'Political Conflicts',
            'ukraine': 'Political Conflicts',
            'syria': 'Political Conflicts',
            'afghanistan': 'Humanitarian Crises',
            'somalia': 'Humanitarian Crises',
            'sudan': 'Humanitarian Crises',
            'haiti': 'Humanitarian Crises',
        }
    
    def classify_article(self, article: Dict) -> Dict:
        """
        Classify article using source + keywords (no LLM)
        
        Returns:
            Classification result with category and confidence
        """
        text = f"{article.get('title', '')} {article.get('content', '')}".lower()
        source_category = article.get('source_category', 'Mixed')
        priority = article.get('priority', 'medium')
        
        # Step 1: If source already categorized it (NGO/specialized feed)
        if source_category != 'Mixed':
            confidence = 0.9 if priority == 'high' else 0.7
            return self._create_result(article, source_category, confidence, 'source_trust')
        
        # Step 2: Check for specific crisis zones
        for zone, category in self.crisis_zone_mapping.items():
            if zone in text:
                return self._create_result(article, category, 0.85, 'crisis_zone')
        
        # Step 3: Keyword matching for each category
        category_scores = {}
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                # Normalize by keyword count
                category_scores[category] = score / len(keywords)
        
        if category_scores:
            top_category = max(category_scores, key=category_scores.get)
            confidence = min(category_scores[top_category] * 2, 0.95)  # Scale up but cap
            
            # Require minimum keyword density
            if confidence >= 0.15:
                return self._create_result(article, top_category, confidence, 'keyword_match')
        
        # Step 4: Default to unknown
        return self._create_result(article, 'Unknown', 0.0, 'no_match')
    
    def classify_batch(self, articles: List[Dict]) -> List[Dict]:
        """
        Classify multiple articles (much faster than LLM)
        """
        logger.info(f"Classifying {len(articles)} articles using rule-based classifier...")
        results = []
        
        for i, article in enumerate(articles):
            result = self.classify_article(article)
            results.append(result)
            
            if (i + 1) % 50 == 0:
                logger.info(f"Processed {i + 1}/{len(articles)} articles")
        
        # Count crises
        crisis_count = sum(1 for r in results if r['is_crisis'])
        logger.info(f"✓ Found {crisis_count} crisis articles using simple classifier")
        
        return results
    
    def _create_result(self, article: Dict, category: str, 
                      confidence: float, method: str) -> Dict:
        """Create classification result"""
        return {
            'article': article,
            'predicted_category': category,
            'confidence': confidence,
            'is_crisis': category != 'Unknown' and confidence >= 0.15,
            'classification_method': method,
            'all_scores': {category: confidence}
        }


def classify_crisis_articles(articles: List[Dict]) -> List[Dict]:
    """
    Classify articles using simple rule-based method
    
    Returns:
        List of classification results
    """
    classifier = SimpleCrisisClassifier()
    return classifier.classify_batch(articles)


def get_crisis_summary(classified_articles: List[Dict]) -> Dict:
    """Generate summary statistics"""
    crisis_articles = [r for r in classified_articles if r['is_crisis']]
    
    # Category distribution
    category_counts = {}
    total_confidence = 0.0
    
    for result in crisis_articles:
        category = result['predicted_category']
        category_counts[category] = category_counts.get(category, 0) + 1
        total_confidence += result['confidence']
    
    return {
        'total_articles': len(classified_articles),
        'crisis_count': len(crisis_articles),
        'category_distribution': category_counts,
        'average_confidence': total_confidence / len(crisis_articles) if crisis_articles else 0.0
    }
