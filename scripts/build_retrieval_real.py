#!/usr/bin/env python3
"""
Build retrieval index using real AmazonHelp conversations.
"""

import pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.retrieval import RetrievalSystem

def load_retrieval_corpus():
    """Load real conversations for retrieval corpus."""
    
    print("Loading retrieval corpus...")
    
    data_dir = Path("data/processed")
    
    # Combine train and dev for retrieval corpus
    dfs = []
    for split in ['train', 'dev']:
        file = data_dir / f"AmazonHelp_{split}.csv"
        if file.exists():
            df = pd.read_csv(file)
            dfs.append(df)
            print(f"Loaded {len(df)} from {file.name}")
    
    if not dfs:
        raise FileNotFoundError("No processed conversations found")
    
    combined = pd.concat(dfs, ignore_index=True)
    print(f"Total retrieval corpus: {len(combined)} conversations")
    
    return combined

def main():
    """Build retrieval index with real data."""
    
    # Load corpus
    corpus_df = load_retrieval_corpus()
    
    # Initialize retrieval system (will use TF-IDF fallback on Windows)
    retrieval = RetrievalSystem(use_semantic=False)
    
    # Build index
    retrieval.build_index(corpus_df)
    
    # Save models
    model_dir = Path("models")
    retrieval.save(model_dir)
    
    print(f"\nRetrieval index built and saved to {model_dir}")
    
    # Test retrieval
    print("\nTesting retrieval with sample queries:")
    test_queries = [
        "Where is my order?",
        "I received the wrong item",
        "I want a refund"
    ]
    
    for query in test_queries:
        results = retrieval.retrieve(query, k=3)
        print(f"\nQuery: '{query}'")
        for i, result in enumerate(results[:3], 1):
            print(f"  {i}. Similarity: {result['similarity']:.3f}")
            print(f"     Customer: {result['customer_message'][:100]}...")
            print(f"     Brand: {result['brand_response'][:100]}...")

if __name__ == "__main__":
    main()
