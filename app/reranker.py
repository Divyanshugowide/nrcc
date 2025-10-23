"""
Multilingual Reranker for Enhanced Search Results
Phase 10 - Next Sprint Hooks
"""

import torch
from typing import List, Dict, Any, Tuple
import numpy as np
from sentence_transformers import CrossEncoder
from pathlib import Path

class MultilingualReranker:
    """
    Multilingual reranker for top-50 results
    """
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-12-v2"):
        """
        Initialize reranker model
        
        Args:
            model_name: Cross-encoder model name
        """
        self.model_name = model_name
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def load_model(self):
        """Load reranker model"""
        try:
            self.model = CrossEncoder(self.model_name, device=self.device)
            print(f"Reranker model loaded: {self.model_name}")
            return True
        except Exception as e:
            print(f"Failed to load reranker model: {e}")
            return False
    
    def rerank(self, query: str, documents: List[Dict[str, Any]], 
               top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Rerank documents based on query relevance
        
        Args:
            query: Search query
            documents: List of document dictionaries
            top_k: Number of top results to return
            
        Returns:
            Reranked list of documents
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        if not documents:
            return []
        
        # Prepare query-document pairs
        pairs = []
        for doc in documents:
            # Use excerpt or text for reranking
            text = doc.get('excerpt', doc.get('text', ''))
            pairs.append([query, text])
        
        # Get relevance scores
        scores = self.model.predict(pairs)
        
        # Sort documents by relevance score
        scored_docs = list(zip(documents, scores))
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        # Return top-k results with updated scores
        reranked_docs = []
        for doc, score in scored_docs[:top_k]:
            doc_copy = doc.copy()
            doc_copy['rerank_score'] = float(score)
            reranked_docs.append(doc_copy)
        
        return reranked_docs

class AdvancedReranker:
    """
    Advanced reranker with multiple strategies
    """
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-12-v2"):
        self.base_reranker = MultilingualReranker(model_name)
        self.loaded = False
        
    def load_model(self):
        """Load reranker model"""
        self.loaded = self.base_reranker.load_model()
        return self.loaded
    
    def rerank_with_weights(self, query: str, documents: List[Dict[str, Any]], 
                           top_k: int = 10, 
                           rerank_weight: float = 0.7,
                           original_weight: float = 0.3) -> List[Dict[str, Any]]:
        """
        Rerank with weighted combination of original and rerank scores
        
        Args:
            query: Search query
            documents: List of document dictionaries
            top_k: Number of top results to return
            rerank_weight: Weight for rerank score
            original_weight: Weight for original score
            
        Returns:
            Reranked list of documents
        """
        if not self.loaded:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        if not documents:
            return []
        
        # Get rerank scores
        reranked = self.base_reranker.rerank(query, documents, len(documents))
        
        # Combine with original scores
        for i, doc in enumerate(reranked):
            original_score = doc.get('score', 0.0)
            rerank_score = doc.get('rerank_score', 0.0)
            
            # Normalize scores to [0, 1] range
            original_score_norm = min(original_score, 1.0)
            rerank_score_norm = min(rerank_score, 1.0)
            
            # Weighted combination
            combined_score = (original_weight * original_score_norm + 
                            rerank_weight * rerank_score_norm)
            
            doc['combined_score'] = combined_score
            doc['original_score'] = original_score
            doc['rerank_score'] = rerank_score
        
        # Sort by combined score
        reranked.sort(key=lambda x: x['combined_score'], reverse=True)
        
        return reranked[:top_k]
    
    def rerank_by_article_relevance(self, query: str, documents: List[Dict[str, Any]], 
                                   top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Rerank with special attention to article-level relevance
        
        Args:
            query: Search query
            documents: List of document dictionaries
            top_k: Number of top results to return
            
        Returns:
            Reranked list of documents
        """
        if not self.loaded:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        if not documents:
            return []
        
        # Group documents by article
        article_groups = {}
        for doc in documents:
            article_key = f"{doc.get('doc_id', '')}_{doc.get('article_no', '')}"
            if article_key not in article_groups:
                article_groups[article_key] = []
            article_groups[article_key].append(doc)
        
        # Rerank within each article group
        reranked_articles = []
        for article_key, article_docs in article_groups.items():
            if len(article_docs) == 1:
                # Single document per article
                reranked_articles.extend(article_docs)
            else:
                # Multiple documents per article - rerank them
                reranked_article_docs = self.base_reranker.rerank(
                    query, article_docs, len(article_docs)
                )
                reranked_articles.extend(reranked_article_docs)
        
        # Final rerank across all documents
        final_reranked = self.base_reranker.rerank(query, reranked_articles, top_k)
        
        return final_reranked

def create_reranker_script():
    """
    Create a script to test reranker functionality
    """
    script_content = '''#!/usr/bin/env python3
"""
Test script for multilingual reranker
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from app.reranker import MultilingualReranker, AdvancedReranker

def test_reranker():
    """Test reranker functionality"""
    
    # Sample documents
    documents = [
        {
            'doc_id': 'Test Document 1',
            'article_no': 'Article 1',
            'text': 'This is about nuclear energy and safety regulations.',
            'excerpt': 'Nuclear energy safety regulations...',
            'score': 0.8
        },
        {
            'doc_id': 'Test Document 2', 
            'article_no': 'Article 2',
            'text': 'This discusses radiation protection measures.',
            'excerpt': 'Radiation protection measures...',
            'score': 0.7
        },
        {
            'doc_id': 'Test Document 3',
            'article_no': 'Article 3', 
            'text': 'This covers nuclear waste management procedures.',
            'excerpt': 'Nuclear waste management...',
            'score': 0.6
        }
    ]
    
    query = "nuclear safety regulations"
    
    # Test basic reranker
    print("Testing basic reranker...")
    reranker = MultilingualReranker()
    if reranker.load_model():
        reranked = reranker.rerank(query, documents, top_k=2)
        print("Reranked results:")
        for i, doc in enumerate(reranked):
            print(f"{i+1}. {doc['doc_id']} - Score: {doc.get('rerank_score', 0):.3f}")
    
    # Test advanced reranker
    print("\\nTesting advanced reranker...")
    advanced_reranker = AdvancedReranker()
    if advanced_reranker.load_model():
        reranked = advanced_reranker.rerank_with_weights(
            query, documents, top_k=2, rerank_weight=0.7, original_weight=0.3
        )
        print("Advanced reranked results:")
        for i, doc in enumerate(reranked):
            print(f"{i+1}. {doc['doc_id']} - Combined: {doc.get('combined_score', 0):.3f}")

if __name__ == "__main__":
    test_reranker()
'''
    
    with open("test_reranker.py", "w", encoding="utf-8") as f:
        f.write(script_content)
    
    print("Reranker test script created: test_reranker.py")

if __name__ == "__main__":
    create_reranker_script()
