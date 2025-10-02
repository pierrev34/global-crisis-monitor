# Contributing to ARGUS

Thank you for your interest in contributing to ARGUS - AI-Powered Global Crisis Monitor! This document provides guidelines for contributing to the project.

## Development Setup

1. **Fork and clone the repository:**
```bash
git clone https://github.com/yourusername/global-crisis-monitor.git
cd global-crisis-monitor
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install development dependencies:**
```bash
pip install -r requirements.txt
python setup.py
```

4. **Run tests to ensure everything works:**
```bash
python example.py
```

## Project Structure

```
argus/
├── __init__.py          # Package initialization
├── config.py            # Configuration settings
├── data_ingestion.py    # GDELT data fetching
├── classifier.py        # AI crisis classification
├── geo_extractor.py     # Geographic entity extraction
└── mapper.py           # Interactive map generation

main.py                  # Main pipeline orchestrator
setup.py                # Environment setup script
example.py              # Usage examples
requirements.txt        # Python dependencies
```

## Contribution Areas

### 1. Data Sources
- **Add new data sources** beyond GDELT
- **Improve data quality** filtering and validation
- **Support additional languages** and regions
- **Add social media** data integration

### 2. AI/ML Improvements
- **Better classification models** - experiment with different transformers
- **Custom fine-tuning** on crisis-specific datasets
- **Multilingual support** for non-English content
- **Sentiment analysis** integration
- **Event clustering** and deduplication

### 3. Geographic Features
- **Improved geocoding** accuracy and coverage
- **Administrative boundaries** integration
- **Population density** weighting
- **Infrastructure data** overlay
- **Historical crisis** data comparison

### 4. Visualization Enhancements
- **Real-time updates** and streaming
- **Mobile-responsive** design
- **Additional chart types** and analytics
- **Export capabilities** (PDF, PNG, data)
- **Embedding options** for other websites

### 5. Performance Optimizations
- **Caching strategies** for better performance
- **Parallel processing** for large datasets
- **Database integration** for persistence
- **API rate limiting** improvements
- **Memory optimization** for large-scale processing

## Coding Standards

### Python Style
- Follow **PEP 8** style guidelines
- Use **type hints** for function parameters and returns
- Include **docstrings** for all classes and functions
- Maximum line length: **88 characters** (Black formatter)

### Code Quality
- Write **unit tests** for new functionality
- Include **error handling** and logging
- Use **meaningful variable names**
- Keep functions **focused and small**
- Add **comments** for complex logic

### Example Function Structure
```python
def process_crisis_data(articles: List[Dict], 
                       confidence_threshold: float = 0.3) -> List[Dict]:
    """
    Process articles to identify and classify crises.
    
    Args:
        articles: List of article dictionaries from data ingestion
        confidence_threshold: Minimum confidence for crisis classification
        
    Returns:
        List of processed crisis data with classifications and locations
        
    Raises:
        ValueError: If articles list is empty or invalid
        ModelError: If AI classification fails
    """
    if not articles:
        raise ValueError("Articles list cannot be empty")
    
    try:
        # Implementation here
        logger.info(f"Processing {len(articles)} articles")
        # ... rest of function
        
    except Exception as e:
        logger.error(f"Error processing crisis data: {e}")
        raise
```

## Testing Guidelines

### Unit Tests
Create tests in a `tests/` directory:
```python
import unittest
from argus.classifier import CrisisClassifier

class TestCrisisClassifier(unittest.TestCase):
    def setUp(self):
        self.classifier = CrisisClassifier()
    
    def test_classify_article(self):
        article = {
            'title': 'Earthquake hits Japan',
            'content': 'A magnitude 7.0 earthquake struck...'
        }
        result = self.classifier.classify_article(article)
        self.assertIn('predicted_category', result)
        self.assertIsInstance(result['confidence'], float)
```

### Integration Tests
Test the complete pipeline with small datasets:
```python
def test_full_pipeline():
    # Test with a small sample of real data
    articles = get_crisis_articles(hours_back=1, max_articles=5)
    results = classify_crisis_articles(articles)
    enhanced = extract_article_locations(results)
    map_file = create_crisis_visualization(enhanced)
    
    assert os.path.exists(map_file)
```

## Submitting Changes

### Pull Request Process

1. **Create a feature branch:**
```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes** following the coding standards

3. **Test your changes:**
```bash
python example.py  # Basic functionality test
# Add specific tests for your changes
```

4. **Update documentation** if needed:
   - Update `README.md` for new features
   - Update `API.md` for API changes
   - Update `USAGE.md` for new usage patterns

5. **Commit your changes:**
```bash
git add .
git commit -m "feat: add new crisis classification model"
```

6. **Push and create pull request:**
```bash
git push origin feature/your-feature-name
```

### Commit Message Format
Use conventional commit format:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `perf:` - Performance improvements

Examples:
```
feat: add support for Twitter data ingestion
fix: resolve geocoding timeout issues
docs: update API documentation for new endpoints
perf: optimize batch processing for large datasets
```

## Feature Requests and Bug Reports

### Bug Reports
Include the following information:
- **Environment**: OS, Python version, package versions
- **Steps to reproduce** the issue
- **Expected behavior** vs actual behavior
- **Error messages** and stack traces
- **Sample data** if relevant (anonymized)

### Feature Requests
Include:
- **Use case**: Why is this feature needed?
- **Proposed solution**: How should it work?
- **Alternatives considered**: Other approaches you've thought about
- **Implementation ideas**: Technical approach if you have thoughts

## Development Tips

### Working with Large Datasets
- Use `max_articles` parameter to limit data during development
- Test with small datasets first
- Use caching to avoid repeated API calls
- Monitor memory usage with large datasets

### Debugging AI Models
- Use `verbose` logging to see model loading and processing
- Test with simple, known examples first
- Check model outputs manually for sanity
- Consider model size vs. accuracy tradeoffs

### Geographic Data
- Test geocoding with various location formats
- Handle edge cases (ambiguous locations, non-existent places)
- Consider rate limiting for geocoding services
- Cache geocoding results to improve performance

### Map Visualization
- Test with different data densities
- Ensure maps work on different screen sizes
- Consider color accessibility for different crisis types
- Test map performance with large numbers of markers

## Resources

### Useful Libraries and Tools
- **Transformers**: Hugging Face model documentation
- **spaCy**: NLP and NER documentation
- **Folium**: Interactive mapping documentation
- **GDELT**: API documentation and data formats
- **Geopy**: Geocoding services documentation

### Learning Resources
- **Crisis Informatics**: Research on technology in crisis response
- **NLP for Social Good**: Applications of NLP to humanitarian challenges
- **Geospatial Analysis**: Working with geographic data
- **Data Visualization**: Best practices for crisis data presentation

## Code of Conduct

This project follows a standard code of conduct:
- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Prioritize the humanitarian mission of the project

## Questions?

Feel free to open an issue for:
- Questions about contributing
- Technical discussions
- Feature brainstorming
- Getting help with development setup

Thank you for contributing to ARGUS and helping make crisis information more accessible!
