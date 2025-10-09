"""
Chat handler with Ollama integration.
Falls back to keyword matching if Ollama unavailable.
"""

import json
import logging
from typing import Dict, List
import requests

logger = logging.getLogger(__name__)

class CrisisChat:
    def __init__(self, crisis_data: List[Dict] = None):
        """Initialize chat handler with crisis data."""
        self.crisis_data = crisis_data or []
        self.ollama_available = self._check_ollama()
        
        if self.ollama_available:
            logger.info("Ollama detected - using LLM mode")
        else:
            logger.info("Ollama not available - using keyword fallback")
    
    def _check_ollama(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def query(self, user_message: str) -> str:
        """Process user query with LLM or fallback."""
        if self.ollama_available:
            return self._llm_query(user_message)
        else:
            return self._keyword_query(user_message)
    
    def _llm_query(self, user_message: str) -> str:
        """Query using Ollama LLM."""
        # Build context from crisis data
        context = self._build_context()
        
        prompt = f"""You are a crisis monitoring assistant. Answer questions about global crises based ONLY on this data:

{context}

User question: {user_message}

Provide a concise, helpful answer. If asked about a location, mention if it's in the data and zoom instructions. Keep responses under 100 words."""

        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2:3b",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get("response", "Sorry, couldn't generate response.")
            else:
                return self._keyword_query(user_message)
                
        except Exception as e:
            logger.error(f"Ollama query failed: {e}")
            return self._keyword_query(user_message)
    
    def _keyword_query(self, user_message: str) -> str:
        """Fallback keyword matching."""
        q = user_message.lower()
        
        # Build quick stats
        total = len(self.crisis_data)
        locations = list(set(item.get('location_name', '') for item in self.crisis_data))[:10]
        
        if 'how many' in q or 'total' in q or 'count' in q:
            return f"Found {total} crisis locations across the dataset."
        
        if 'list' in q or q == 'all':
            return f"Top locations: {', '.join(locations[:5])}"
        
        # Location search
        for item in self.crisis_data:
            loc = item.get('location_name', '').lower()
            if any(word in loc for word in q.split() if len(word) > 2):
                return f"Found {loc}: {item.get('category', 'Unknown')} crisis"
        
        return f"Try asking: 'how many total', 'list all', or mention a location like '{locations[0]}'"
    
    def _build_context(self) -> str:
        """Build LLM context from crisis data."""
        # Aggregate by location
        location_map = {}
        for item in self.crisis_data:
            loc = item.get('location_name', 'Unknown')
            cat = item.get('category', 'Unknown')
            
            if loc not in location_map:
                location_map[loc] = {'category': cat, 'count': 0}
            location_map[loc]['count'] += 1
        
        # Build context string
        context_parts = []
        for loc, info in sorted(location_map.items(), key=lambda x: x[1]['count'], reverse=True)[:20]:
            context_parts.append(f"- {loc}: {info['count']} {info['category']} incident(s)")
        
        return "\n".join(context_parts)
    
    def get_js_config(self) -> Dict:
        """Get JavaScript configuration for frontend."""
        return {
            'ollama_available': self.ollama_available,
            'crisis_count': len(self.crisis_data),
            'locations': [item.get('location_name', '') for item in self.crisis_data[:20]]
        }
