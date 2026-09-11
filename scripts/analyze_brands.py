#!/usr/bin/env python3
"""
Analyze brands in the Customer Support on Twitter dataset to select the best brand.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter
import json

def load_data():
    """Load the dataset."""
    data_dir = Path("data/raw")
    
    # Try different possible file names
    possible_files = [
        data_dir / "twcs.csv",
        data_dir / "customer-support-on-twitter.csv",
        data_dir / "tweets.csv"
    ]
    
    for file_path in possible_files:
        if file_path.exists():
            print(f"Loading data from {file_path}")
            return pd.read_csv(file_path)
    
    raise FileNotFoundError("Dataset file not found. Expected one of: " + 
                          ", ".join([str(f) for f in possible_files]))

def analyze_brands(df):
    """Analyze brands and generate selection report."""
    
    print("Analyzing brands...")
    
    # Extract brand from tweet text (usually @brand mentions)
    # The dataset has 'author_id' field - brands are typically the support accounts
    
    # Get unique authors
    authors = df['author_id'].value_counts()
    
    # Filter for likely support accounts (high tweet count)
    top_authors = authors.head(50)
    
    print(f"\nTop 50 authors by tweet count:")
    print(top_authors.to_string())
    
    # Analyze conversation completeness
    # Group by conversation_id
    conversations = df.groupby('tweet_id').size()
    
    # Calculate metrics for each author
    brand_metrics = []
    
    for author_id in top_authors.index:
        author_tweets = df[df['author_id'] == author_id]
        
        # Count conversations this author participated in
        conversation_ids = author_tweets['in_response_to_tweet_id'].dropna()
        
        metrics = {
            'author_id': author_id,
            'total_tweets': len(author_tweets),
            'unique_conversations': conversation_ids.nunique(),
            'avg_tweets_per_conversation': len(author_tweets) / max(conversation_ids.nunique(), 1),
            'response_rate': len(conversation_ids) / len(author_tweets) if len(author_tweets) > 0 else 0
        }
        
        brand_metrics.append(metrics)
    
    brand_df = pd.DataFrame(brand_metrics)
    brand_df = brand_df.sort_values('total_tweets', ascending=False)
    
    print("\nBrand metrics:")
    print(brand_df.to_string())
    
    # Save report
    report_path = Path("reports/brand_analysis.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    brand_df.to_json(report_path, orient='records', indent=2)
    print(f"\nBrand analysis saved to {report_path}")
    
    return brand_df

def select_brand(brand_df):
    """Select the best brand based on metrics."""
    
    print("\nSelecting brand...")
    
    # Criteria: high tweet count, high conversation count, good response rate
    # Filter for brands with at least 1000 tweets and 500 conversations
    candidates = brand_df[
        (brand_df['total_tweets'] >= 1000) &
        (brand_df['unique_conversations'] >= 500)
    ]
    
    if len(candidates) == 0:
        print("No brands meet minimum criteria. Using top brand by tweet count.")
        selected = brand_df.iloc[0]
    else:
        # Score candidates
        candidates['score'] = (
            candidates['total_tweets'] / candidates['total_tweets'].max() * 0.4 +
            candidates['unique_conversations'] / candidates['unique_conversations'].max() * 0.4 +
            candidates['response_rate'] / candidates['response_rate'].max() * 0.2
        )
        selected = candidates.sort_values('score', ascending=False).iloc[0]
    
    print(f"\nSelected brand: {selected['author_id']}")
    print(f"  - Total tweets: {selected['total_tweets']}")
    print(f"  - Unique conversations: {selected['unique_conversations']}")
    print(f"  - Response rate: {selected['response_rate']:.2%}")
    
    return selected['author_id']

def main():
    """Main analysis function."""
    
    # Load data
    df = load_data()
    
    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    
    # Analyze brands
    brand_df = analyze_brands(df)
    
    # Select brand
    selected_brand = select_brand(brand_df)
    
    # Save selection
    selection_path = Path("data/selected_brand.txt")
    selection_path.parent.mkdir(parents=True, exist_ok=True)
    selection_path.write_text(str(selected_brand))
    
    print(f"\nSelected brand saved to {selection_path}")

if __name__ == "__main__":
    main()
