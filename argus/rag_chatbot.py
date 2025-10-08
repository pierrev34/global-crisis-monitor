"""
Optional RAG chatbot for conversational crisis queries.
Requires Ollama + langchain dependencies. Falls back to keyword matching if unavailable.
"""

import logging
import json
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class CrisisChatbot:
    """RAG chatbot for crisis queries with source attribution"""
    
    def __init__(self, crisis_data: List[Dict] = None):
        """Initialize chatbot with crisis data. Auto-detects Ollama availability."""
        self.crisis_data = crisis_data or []
        self.llm = None
        self.vector_store = None
        self.qa_chain = None
        self.is_initialized = False
        
        # Try to initialize LLM components
        try:
            self._initialize_llm()
        except Exception as e:
            logger.warning(f"LLM not available, using fallback mode: {e}")
            self.is_initialized = False
    
    def _initialize_llm(self):
        """Initialize Ollama LLM and ChromaDB vector store for RAG."""
        try:
            from langchain_community.llms import Ollama
            from langchain_community.embeddings import HuggingFaceEmbeddings
            from langchain_community.vectorstores import Chroma
            from langchain.chains import RetrievalQA
            from langchain.prompts import PromptTemplate
            from langchain.schema import Document
            
            # Initialize embeddings (lightweight)
            logger.info("Loading embeddings model...")
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
            
            # Prepare documents for indexing
            documents = self._prepare_documents()
            
            if len(documents) == 0:
                logger.warning("No documents to index")
                return
            
            # Create vector store
            logger.info(f"Indexing {len(documents)} crisis documents...")
            self.vector_store = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=".chromadb"
            )
            
            # Initialize Ollama LLM
            logger.info("Connecting to Ollama...")
            self.llm = Ollama(
                model="llama3.2:3b",  # Lightweight 3B model
                temperature=0.3,  # Lower = more factual
            )
            
            # Custom prompt for crisis monitoring
            prompt_template = """You are a crisis monitoring assistant. Answer questions about global crises using ONLY the provided context.

Context: {context}

Question: {question}

Instructions:
- Be concise and factual
- Always cite sources (organization names, locations)
- If you don't know, say "I don't have information about that"
- For "how to help" questions, mention relevant organizations
- Include incident counts when relevant

Answer:"""
            
            PROMPT = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"]
            )
            
            # Create RAG chain
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vector_store.as_retriever(
                    search_kwargs={"k": 5}  # Top 5 relevant docs
                ),
                return_source_documents=True,
                chain_type_kwargs={"prompt": PROMPT}
            )
            
            self.is_initialized = True
            logger.info("RAG chatbot initialized successfully")
            
        except ImportError as e:
            logger.error(f"Missing dependencies: {e}")
            logger.error("Install with: pip install langchain chromadb sentence-transformers")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise
    
    def _prepare_documents(self) -> List:
        """Convert crisis data to LangChain documents for vector indexing."""
        from langchain.schema import Document
        
        documents = []
        
        for item in self.crisis_data:
            article = item.get('article', {})
            category = item.get('predicted_category', 'Unknown')
            
            # Extract key info
            title = article.get('title', '')
            content = article.get('content', '')
            source = article.get('source_name', article.get('source', 'Unknown'))
            date = article.get('publish_date', 'Recent')
            
            # Get location
            locations = article.get('locations', [])
            location_names = []
            for loc in locations:
                if loc.get('geocoded'):
                    name = loc.get('found_name', loc.get('text', ''))
                    if name:
                        location_names.append(name)
            
            location_str = ', '.join(location_names[:3]) if location_names else 'Unknown'
            
            # Create document text
            doc_text = f"""
Crisis Type: {category}
Location: {location_str}
Title: {title}
Source: {source}
Date: {date}
Details: {content[:500]}
"""
            
            # Create document with metadata
            doc = Document(
                page_content=doc_text.strip(),
                metadata={
                    'category': category,
                    'location': location_str,
                    'source': source,
                    'title': title,
                    'date': date
                }
            )
            
            documents.append(doc)
        
        return documents
    
    def query(self, question: str) -> Dict:
        """Query crisis data. Returns answer with sources if RAG available, else keyword fallback."""
        if not self.is_initialized:
            return self._fallback_query(question)
        
        try:
            # Query the RAG chain
            result = self.qa_chain({"query": question})
            
            # Extract sources
            sources = []
            for doc in result.get('source_documents', []):
                sources.append({
                    'title': doc.metadata.get('title', 'Untitled'),
                    'category': doc.metadata.get('category', 'Unknown'),
                    'location': doc.metadata.get('location', 'Unknown'),
                    'source': doc.metadata.get('source', 'Unknown')
                })
            
            return {
                'answer': result['result'],
                'sources': sources,
                'mode': 'rag'
            }
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return {
                'answer': f"Sorry, I encountered an error: {str(e)}",
                'sources': [],
                'mode': 'error'
            }
    
    def _fallback_query(self, question: str) -> Dict:
        """Simple keyword-based responses when Ollama unavailable."""
        question_lower = question.lower()
        
        # Generate simple summary
        if not self.crisis_data:
            return {
                'answer': "No crisis data available to answer your question.",
                'sources': [],
                'mode': 'fallback'
            }
        
        # Count by category
        category_counts = {}
        for item in self.crisis_data:
            cat = item.get('predicted_category', 'Unknown')
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        # Simple keyword responses
        if any(word in question_lower for word in ['how many', 'count', 'number']):
            total = len(self.crisis_data)
            breakdown = ', '.join([f"{cat}: {count}" for cat, count in category_counts.items()])
            answer = f"There are {total} total crisis incidents. Breakdown: {breakdown}"
        
        elif any(word in question_lower for word in ['most', 'urgent', 'severe', 'worst']):
            top_cat = max(category_counts.items(), key=lambda x: x[1])
            answer = f"The most reported crisis type is {top_cat[0]} with {top_cat[1]} incidents."
        
        elif any(word in question_lower for word in ['help', 'donate', 'volunteer']):
            answer = "Organizations responding to these crises include: UNHCR, Doctors Without Borders (MSF), ICRC, Amnesty International, Human Rights Watch. Visit their websites for ways to help."
        
        else:
            answer = f"I found {len(self.crisis_data)} crisis incidents across {len(category_counts)} categories. Try asking: 'What are the most urgent crises?' or 'How can I help?'"
        
        return {
            'answer': answer,
            'sources': [],
            'mode': 'fallback'
        }
    
    def get_suggested_questions(self) -> List[str]:
        """Generate suggested questions based on current crisis data."""
        if not self.crisis_data:
            return []
        
        # Count categories and locations
        categories = set()
        locations = set()
        
        for item in self.crisis_data:
            categories.add(item.get('predicted_category', 'Unknown'))
            article = item.get('article', {})
            for loc in article.get('locations', [])[:1]:  # First location
                if loc.get('geocoded'):
                    name = loc.get('found_name', '')
                    if name and name != 'Unknown':
                        locations.add(name.split(',')[0])  # Just country/region
        
        suggestions = [
            "What are the most urgent crises right now?",
            "How many incidents are there in total?",
            "Which organizations are responding to these crises?",
            "How can I help?"
        ]
        
        # Add location-specific questions
        if locations:
            top_location = list(locations)[0]
            suggestions.insert(1, f"What's happening in {top_location}?")
        
        return suggestions[:5]


def create_chatbot_from_data(crisis_data: List[Dict]) -> CrisisChatbot:
    """Factory function to create chatbot instance from crisis data."""
    return CrisisChatbot(crisis_data)
