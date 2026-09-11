#!/usr/bin/env python3
"""
Prepare data for the support agent system.
Processes raw dataset, selects brand, creates conversations, and generates splits.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from sklearn.model_selection import train_test_split
import re

def load_data():
    """Load the dataset or generate synthetic data for demo."""
    data_dir = Path("data/raw")
    
    possible_files = [
        data_dir / "twcs.csv",
        data_dir / "customer-support-on-twitter.csv",
        data_dir / "tweets.csv"
    ]
    
    for file_path in possible_files:
        if file_path.exists():
            print(f"Loading data from {file_path}")
            return pd.read_csv(file_path, nrows=100000)  # Load sample for faster processing
    
    print("No dataset file found. Generating synthetic sample data for demo...")
    return generate_synthetic_data()

def generate_synthetic_data(n=5000):
    """Generate synthetic customer support conversations for demo."""
    import random
    
    messages = [
        "Where is my order?", "I received the wrong item", "I can't log into my account",
        "What are your business hours?", "I need a refund", "My package is damaged",
        "When will my order arrive?", "I was charged twice", "How do I change my password?",
        "Is this product in stock?", "I want to cancel my order", "The delivery is late"
    ]
    
    responses = [
        "I'll help you track your order. Please provide your order number.",
        "I apologize for the mistake. Let me arrange a replacement for you.",
        "Let me help you reset your password. Please click the link I'll send.",
        "Our business hours are 9 AM to 5 PM EST, Monday through Friday.",
        "I can process your refund. Please confirm the order details.",
        "I'm sorry to hear that. I'll arrange a replacement shipment.",
        "Your order is expected to arrive in 2-3 business days.",
        "I'll investigate the duplicate charge and issue a refund.",
        "You can change your password in your account settings.",
        "This product is currently in stock and available for shipping.",
        "I can cancel your order. Please confirm you want to proceed.",
        "I apologize for the delay. Let me check the status for you."
    ]
    
    data = []
    for i in range(n):
        data.append({
            'tweet_id': f'tweet_{i}',
            'author_id': 'customer',
            'text': random.choice(messages),
            'in_response_to_tweet_id': None,
            'conversation_id': f'conv_{i//2}'
        })
        data.append({
            'tweet_id': f'tweet_{i}_resp',
            'author_id': 'AmazonHelp',
            'text': random.choice(responses),
            'in_response_to_tweet_id': f'tweet_{i}',
            'conversation_id': f'conv_{i//2}'
        })
    
    return pd.DataFrame(data)

def clean_text(text):
    """Clean tweet text."""
    if pd.isna(text):
        return ""
    
    text = str(text)
    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    # Remove mentions but keep the text after
    text = re.sub(r'@\w+', '', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text.strip()

def select_brand_data(df, brand_id=None):
    """Select data for a specific brand."""
    
    if brand_id is None:
        # Try to load from file
        brand_file = Path("data/selected_brand.txt")
        if brand_file.exists():
            brand_id = brand_file.read_text().strip()
        else:
            # Use a common support account
            brand_id = "AmazonHelp"
    
    print(f"Selecting data for brand: {brand_id}")
    
    # Filter for this brand's tweets
    brand_tweets = df[df['author_id'] == brand_id]
    
    print(f"Brand tweets: {len(brand_tweets)}")
    
    return brand_tweets, brand_id

def build_conversations(df, brand_id):
    """Build conversation threads."""
    
    print("Building conversations...")
    
    # Get all tweets that are responses to brand
    customer_tweets = df[df['in_response_to_tweet_id'].notna()]
    
    # Build conversation mapping
    conversations = []
    
    # Group by response tweet ID to find brand responses
    for idx, row in customer_tweets.iterrows():
        response_to = row['in_response_to_tweet_id']
        
        # Find the brand's response
        brand_response = df[df['tweet_id'] == response_to]
        
        if len(brand_response) > 0:
            conv = {
                'customer_tweet_id': row['tweet_id'],
                'customer_text': clean_text(row['text']),
                'brand_tweet_id': response_to,
                'brand_text': clean_text(brand_response.iloc[0]['text']),
                'conversation_id': row.get('conversation_id', f"conv_{idx}")
            }
            conversations.append(conv)
    
    print(f"Built {len(conversations)} conversations")
    
    return pd.DataFrame(conversations)

def create_splits(conversations_df):
    """Create train/dev/test splits."""
    
    print("Creating train/dev/test splits...")
    
    # Split: 70% train, 15% dev, 15% test
    train, temp = train_test_split(conversations_df, test_size=0.3, random_state=42)
    dev, test = train_test_split(temp, test_size=0.5, random_state=42)
    
    print(f"Train: {len(train)}, Dev: {len(dev)}, Test: {len(test)}")
    
    return train, dev, test

def save_processed_data(train, dev, test, brand_id):
    """Save processed data."""
    
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    train.to_csv(output_dir / f"{brand_id}_train.csv", index=False)
    dev.to_csv(output_dir / f"{brand_id}_dev.csv", index=False)
    test.to_csv(output_dir / f"{brand_id}_test.csv", index=False)
    
    # Also save combined for retrieval
    combined = pd.concat([train, dev])
    combined.to_csv(output_dir / f"{brand_id}_retrieval_corpus.csv", index=False)
    
    print(f"Saved processed data to {output_dir}")

def create_sample_data(conversations_df, n=1000):
    """Create a smaller sample for quick testing."""
    
    print(f"Creating sample data with {n} conversations...")
    
    sample = conversations_df.sample(n=min(n, len(conversations_df)), random_state=42)
    
    output_dir = Path("data/processed")
    sample.to_csv(output_dir / "sample_conversations.csv", index=False)
    
    print(f"Sample saved to {output_dir}/sample_conversations.csv")

def main():
    """Main preparation function."""
    
    # Load data
    df = load_data()
    print(f"Loaded {len(df)} tweets")
    
    # Select brand
    brand_tweets, brand_id = select_brand_data(df)
    
    # Build conversations
    conversations_df = build_conversations(df, brand_id)
    
    if len(conversations_df) == 0:
        print("No conversations found. Trying alternative approach...")
        # Alternative: use all tweets as individual examples
        conversations_df = pd.DataFrame({
            'customer_tweet_id': df['tweet_id'],
            'customer_text': df['text'].apply(clean_text),
            'brand_tweet_id': '',
            'brand_text': '',
            'conversation_id': df['tweet_id']
        })
    
    # Create splits
    train, dev, test = create_splits(conversations_df)
    
    # Save
    save_processed_data(train, dev, test, brand_id)
    
    # Create sample
    create_sample_data(conversations_df)
    
    print("\nData preparation complete!")

if __name__ == "__main__":
    main()
