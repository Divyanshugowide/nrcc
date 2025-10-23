"""
AraBERT-v3 Integration for Enhanced Arabic Search
Phase 10 - Next Sprint Hooks
"""

import torch
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import numpy as np
from pathlib import Path

class AraBERTIntegration:
    """
    AraBERT-v3 integration for enhanced Arabic semantic search
    """
    
    def __init__(self, model_name: str = "aubmindlab/bert-base-arabertv2"):
        """
        Initialize AraBERT model
        
        Args:
            model_name: AraBERT model name (default: aubmindlab/bert-base-arabertv2)
        """
        self.model_name = model_name
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def load_model(self):
        """Load AraBERT model"""
        try:
            self.model = SentenceTransformer(self.model_name, device=self.device)
            print(f"AraBERT model loaded: {self.model_name}")
            return True
        except Exception as e:
            print(f"Failed to load AraBERT model: {e}")
            return False
    
    def encode_texts(self, texts: List[str]) -> np.ndarray:
        """
        Encode texts using AraBERT
        
        Args:
            texts: List of Arabic texts to encode
            
        Returns:
            numpy array of embeddings
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        # Preprocess texts for AraBERT
        processed_texts = [self._preprocess_text(text) for text in texts]
        
        # Encode texts
        embeddings = self.model.encode(processed_texts, convert_to_numpy=True)
        return embeddings
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text for AraBERT
        
        Args:
            text: Input Arabic text
            
        Returns:
            Preprocessed text
        """
        # Basic preprocessing for AraBERT
        # Remove extra whitespace
        text = " ".join(text.split())
        
        # AraBERT works better with some normalization
        # This is a basic implementation - can be enhanced
        return text
    
    def create_arabert_index(self, texts: List[str], output_path: str):
        """
        Create FAISS index using AraBERT embeddings
        
        Args:
            texts: List of texts to index
            output_path: Path to save the index
        """
        import faiss
        
        # Encode all texts
        embeddings = self.encode_texts(texts)
        
        # Normalize embeddings
        faiss.normalize_L2(embeddings)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)  # Inner product for normalized vectors
        
        # Add embeddings to index
        index.add(embeddings.astype('float32'))
        
        # Save index
        faiss.write_index(index, output_path)
        print(f"AraBERT FAISS index saved to: {output_path}")
        
        return index

class HybridSearchWithAraBERT:
    """
    Enhanced hybrid search combining mE5 and AraBERT
    """
    
    def __init__(self, me5_model, arabert_model, bm25_index, faiss_me5, faiss_arabert, meta):
        self.me5_model = me5_model
        self.arabert_model = arabert_model
        self.bm25_index = bm25_index
        self.faiss_me5 = faiss_me5
        self.faiss_arabert = faiss_arabert
        self.meta = meta
        
    def search(self, query: str, topk: int = 10, 
               me5_weight: float = 0.4, arabert_weight: float = 0.3, bm25_weight: float = 0.3):
        """
        Perform hybrid search with mE5, AraBERT, and BM25
        
        Args:
            query: Search query
            topk: Number of results to return
            me5_weight: Weight for mE5 semantic search
            arabert_weight: Weight for AraBERT semantic search
            bm25_weight: Weight for BM25 keyword search
            
        Returns:
            List of search results
        """
        # Normalize weights
        total_weight = me5_weight + arabert_weight + bm25_weight
        me5_weight /= total_weight
        arabert_weight /= total_weight
        bm25_weight /= total_weight
        
        # Get BM25 results
        bm25_scores = self.bm25_index.get_scores(query.split())
        bm25_indices = np.argsort(bm25_scores)[::-1][:topk*2]
        
        # Get mE5 results
        me5_query_embedding = self.me5_model.encode([query])
        me5_scores, me5_indices = self.faiss_me5.search(me5_query_embedding, topk*2)
        
        # Get AraBERT results
        arabert_query_embedding = self.arabert_model.encode_texts([query])
        arabert_scores, arabert_indices = self.faiss_arabert.search(arabert_query_embedding, topk*2)
        
        # Combine results
        combined_scores = {}
        
        # Add BM25 scores
        for i, idx in enumerate(bm5_indices):
            if idx < len(self.meta):
                score = bm25_scores[idx] * bm25_weight
                combined_scores[idx] = combined_scores.get(idx, 0) + score
        
        # Add mE5 scores
        for i, idx in enumerate(me5_indices[0]):
            if idx < len(self.meta):
                score = me5_scores[0][i] * me5_weight
                combined_scores[idx] = combined_scores.get(idx, 0) + score
        
        # Add AraBERT scores
        for i, idx in enumerate(arabert_indices[0]):
            if idx < len(self.meta):
                score = arabert_scores[0][i] * arabert_weight
                combined_scores[idx] = combined_scores.get(idx, 0) + score
        
        # Sort by combined score
        sorted_results = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Return top results
        results = []
        for idx, score in sorted_results[:topk]:
            if idx < len(self.meta):
                result = self.meta[idx].copy()
                result['score'] = float(score)
                results.append(result)
        
        return results

def prepare_arabert_index(data_path: str = "data/processed/chunks.jsonl", 
                         output_path: str = "data/idx/arabert.faiss"):
    """
    Prepare AraBERT index for the dataset
    
    Args:
        data_path: Path to processed chunks
        output_path: Path to save AraBERT index
    """
    import json
    
    # Load chunks
    texts = []
    with open(data_path, 'r', encoding='utf-8') as f:
        for line in f:
            chunk = json.loads(line)
            texts.append(chunk['text'])
    
    # Initialize AraBERT
    arabert = AraBERTIntegration()
    if not arabert.load_model():
        print("Failed to load AraBERT model")
        return False
    
    # Create index
    arabert.create_arabert_index(texts, output_path)
    print(f"AraBERT index created with {len(texts)} chunks")
    
    return True

if __name__ == "__main__":
    # Example usage
    prepare_arabert_index()
