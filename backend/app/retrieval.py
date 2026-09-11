"""
Historical retrieval system using semantic search.
Supports both sentence-transformers + FAISS and TF-IDF fallback.
"""

import numpy as np
import pandas as pd
from pathlib import Path
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

try:
    from sentence_transformers import SentenceTransformer
    import faiss
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except (ImportError, OSError, Exception) as e:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print(f"Warning: sentence-transformers or faiss not available ({type(e).__name__}). Using TF-IDF fallback.")

class RetrievalSystem:
    """Retrieval system for historical support conversations."""
    
    def __init__(self, use_semantic=True, model_path=None):
        """
        Initialize retrieval system.
        
        Args:
            use_semantic: Whether to use sentence-transformers (falls back to TF-IDF if unavailable)
            model_path: Path to saved retrieval models
        """
        self.use_semantic = use_semantic and SENTENCE_TRANSFORMERS_AVAILABLE
        self.corpus_df = None
        self.embeddings = None
        self.index = None
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.is_loaded = False
        
        if model_path:
            self.load(model_path)
    
    def build_index(self, corpus_df):
        """
        Build retrieval index from corpus.
        
        Args:
            corpus_df: DataFrame with 'customer_text' and 'brand_text' columns
        """
        print(f"Building retrieval index from {len(corpus_df)} examples...")
        
        self.corpus_df = corpus_df.copy()
        self.corpus_df['customer_text'] = self.corpus_df['customer_text'].fillna('')
        self.corpus_df['brand_text'] = self.corpus_df['brand_text'].fillna('')
        
        if self.use_semantic:
            self._build_semantic_index()
        else:
            self._build_tfidf_index()
        
        self.is_loaded = True
        print("Index built successfully!")
    
    def _build_semantic_index(self):
        """Build semantic search index using sentence-transformers + FAISS."""
        print("Building semantic index...")
        
        # Load sentence transformer model
        print("Loading sentence transformer model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Generate embeddings
        print("Generating embeddings...")
        texts = self.corpus_df['customer_text'].tolist()
        self.embeddings = self.model.encode(texts, show_progress_bar=True)
        
        # Build FAISS index
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.embeddings.astype('float32'))
        
        print(f"Semantic index built with {self.index.ntotal} vectors")
    
    def _build_tfidf_index(self):
        """Build TF-IDF index as fallback."""
        print("Building TF-IDF index (fallback mode)...")
        
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            stop_words='english'
        )
        
        texts = self.corpus_df['customer_text'].fillna('').tolist()
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
        
        print(f"TF-IDF index built with {self.tfidf_matrix.shape[0]} documents")
    
    def retrieve(self, query, k=5):
        """
        Retrieve top-k similar historical examples.
        
        Args:
            query: Customer message text
            k: Number of examples to retrieve
            
        Returns:
            List of dictionaries with retrieved examples
        """
        if not self.is_loaded:
            raise ValueError("Retrieval system not loaded. Call build_index() or load() first.")
        
        if self.use_semantic:
            return self._retrieve_semantic(query, k)
        else:
            return self._retrieve_tfidf(query, k)
    
    def _retrieve_semantic(self, query, k):
        """Retrieve using semantic search."""
        # Encode query
        query_embedding = self.model.encode([query])
        
        # Search
        distances, indices = self.index.search(query_embedding.astype('float32'), k)
        
        # Convert distances to similarity scores (L2 distance to similarity)
        similarities = 1 / (1 + distances[0])
        
        # Build results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.corpus_df):
                row = self.corpus_df.iloc[idx]
                results.append({
                    'customer_message': row['customer_text'],
                    'brand_response': row['brand_text'],
                    'similarity': float(similarities[i]),
                    'conversation_id': row.get('conversation_id', f"conv_{idx}")
                })
        
        return results
    
    def _retrieve_tfidf(self, query, k):
        """Retrieve using TF-IDF cosine similarity."""
        # Ensure vectorizer is fitted
        if not hasattr(self.tfidf_vectorizer, 'idf_'):
            print("Vectorizer not fitted, refitting...")
            self._build_tfidf_index()
        
        # Transform query
        query_tfidf = self.tfidf_vectorizer.transform([query])
        
        # Compute similarities
        similarities = cosine_similarity(query_tfidf, self.tfidf_matrix)[0]
        
        # Get top-k
        top_indices = similarities.argsort()[-k:][::-1]
        
        # Build results
        results = []
        for idx in top_indices:
            row = self.corpus_df.iloc[idx]
            results.append({
                'customer_message': row['customer_text'],
                'brand_response': row['brand_text'],
                'similarity': float(similarities[idx]),
                'conversation_id': row.get('conversation_id', f"conv_{idx}")
            })
        
        return results
    
    def save(self, model_dir):
        """
        Save retrieval models to disk.
        
        Args:
            model_dir: Directory to save models
        """
        model_dir = Path(model_dir)
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Save corpus
        self.corpus_df.to_csv(model_dir / 'retrieval_corpus.csv', index=False)
        
        if self.use_semantic:
            # Save embeddings
            np.save(model_dir / 'embeddings.npy', self.embeddings)
            # Save FAISS index
            faiss.write_index(self.index, str(model_dir / 'faiss.index'))
            # Save model config
            with open(model_dir / 'retrieval_config.pkl', 'wb') as f:
                pickle.dump({'use_semantic': True}, f)
        else:
            # Save TF-IDF
            joblib.dump(self.tfidf_vectorizer, model_dir / 'tfidf_vectorizer.joblib')
            joblib.dump(self.tfidf_matrix, model_dir / 'tfidf_matrix.joblib')
            with open(model_dir / 'retrieval_config.pkl', 'wb') as f:
                pickle.dump({'use_semantic': False}, f)
        
        print(f"Retrieval models saved to {model_dir}")
    
    def load(self, model_dir):
        """
        Load retrieval models from disk.
        
        Args:
            model_dir: Directory containing models
        """
        model_dir = Path(model_dir)
        
        # Load corpus
        self.corpus_df = pd.read_csv(model_dir / 'retrieval_corpus.csv')
        
        # Load config
        with open(model_dir / 'retrieval_config.pkl', 'rb') as f:
            config = pickle.load(f)
        
        self.use_semantic = config.get('use_semantic', False) and SENTENCE_TRANSFORMERS_AVAILABLE
        
        if self.use_semantic:
            self.embeddings = np.load(model_dir / 'embeddings.npy')
            self.index = faiss.read_index(str(model_dir / 'faiss.index'))
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        else:
            # Always rebuild TF-IDF index to avoid sklearn version compatibility issues
            print("Rebuilding TF-IDF index from corpus to ensure compatibility...")
            self._build_tfidf_index()
        
        self.is_loaded = True
        print(f"Retrieval models loaded from {model_dir}")
