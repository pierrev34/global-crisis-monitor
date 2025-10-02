#!/usr/bin/env python3
"""
Setup script for ARGUS Global Crisis Monitor
Downloads required models and sets up the environment
"""

import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def install_requirements():
    """Install Python requirements"""
    logger.info("Installing Python requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        logger.info("✅ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to install requirements: {e}")
        return False
    return True


def download_spacy_model():
    """Download spaCy language model"""
    logger.info("Downloading spaCy English model...")
    try:
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        logger.info("✅ spaCy model downloaded successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to download spaCy model: {e}")
        return False
    return True


def test_imports():
    """Test that all required modules can be imported"""
    logger.info("Testing module imports...")
    
    required_modules = [
        'pandas', 'numpy', 'requests', 'transformers', 'torch', 
        'spacy', 'geopy', 'folium', 'tqdm', 'bs4'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            __import__(module)
            logger.info(f"  ✅ {module}")
        except ImportError as e:
            logger.error(f"  ❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        logger.error(f"Failed to import: {', '.join(failed_imports)}")
        return False
    
    logger.info("✅ All modules imported successfully")
    return True


def test_spacy_model():
    """Test that spaCy model is available"""
    logger.info("Testing spaCy model...")
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        doc = nlp("Test sentence with New York as a location.")
        entities = [ent.text for ent in doc.ents if ent.label_ in ['GPE', 'LOC']]
        if entities:
            logger.info(f"✅ spaCy model working (found entities: {entities})")
            return True
        else:
            logger.warning("⚠️  spaCy model loaded but no entities detected in test")
            return True
    except Exception as e:
        logger.error(f"❌ spaCy model test failed: {e}")
        return False


def main():
    """Main setup function"""
    print("🚀 Setting up ARGUS Global Crisis Monitor")
    print("="*50)
    
    success = True
    
    # Install requirements
    if not install_requirements():
        success = False
    
    # Download spaCy model
    if not download_spacy_model():
        success = False
    
    # Test imports
    if not test_imports():
        success = False
    
    # Test spaCy model
    if not test_spacy_model():
        success = False
    
    print("\n" + "="*50)
    if success:
        print("🎉 Setup completed successfully!")
        print("\nYou can now run the crisis monitor with:")
        print("  python main.py")
        print("\nFor help with options:")
        print("  python main.py --help")
    else:
        print("❌ Setup encountered errors. Please check the logs above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
