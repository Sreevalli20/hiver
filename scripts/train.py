#!/usr/bin/env python3
"""
Train the intent classifier and retrieval models.
"""

import sys
import pandas as pd
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from app.classifier import IntentClassifier
from app.intents import INTENT_LABELS

def load_training_data():
    """Load training data."""
    
    data_dir = Path("data/processed")
    
    # Try to load processed data
    train_file = data_dir / "sample_conversations.csv"
    
    if not train_file.exists():
        # Try brand-specific file
        for file in data_dir.glob("*_train.csv"):
            train_file = file
            break
    
    if not train_file.exists():
        raise FileNotFoundError(f"No training data found in {data_dir}")
    
    df = pd.read_csv(train_file)
    print(f"Loaded {len(df)} training examples")
    
    return df

def create_synthetic_labels(df, n_samples=1000):
    """
    Create synthetic intent labels for training.
    In production, this would be replaced with actual labeled data.
    """
    
    print("Creating synthetic intent labels for training...")
    print("Note: In production, use actual human-labeled data.")
    
    # For this demo, we'll create synthetic labels based on keywords
    # This is a simplification - real data would be properly labeled
    
    import random
    
    texts = df['customer_text'].fillna('').tolist()
    labels = []
    
    for text in texts[:n_samples]:
        text_lower = text.lower()
        
        # Simple keyword-based labeling for demo
        if any(word in text_lower for word in ['status', 'where', 'when', 'track', 'shipped']):
            labels.append('order_status')
        elif any(word in text_lower for word in ['wrong', 'damaged', 'missing', 'defective', 'never arrived']):
            labels.append('order_issue')
        elif any(word in text_lower for word in ['refund', 'money back', 'return']):
            labels.append('refund_request')
        elif any(word in text_lower for word in ['charged', 'payment', 'billing', 'declined']):
            labels.append('billing_issue')
        elif any(word in text_lower for word in ['log in', 'password', 'access', 'locked']):
            labels.append('account_access')
        elif any(word in text_lower for word in ['address', 'settings', 'profile', 'update']):
            labels.append('account_issue')
        elif any(word in text_lower for word in ['stock', 'specification', 'compatible', 'color']):
            labels.append('product_info')
        elif any(word in text_lower for word in ['policy', 'hours', 'international', 'contact']):
            labels.append('general_inquiry')
        elif any(word in text_lower for word in ['terrible', 'disappointed', 'awful', 'unhappy']):
            labels.append('complaint')
        else:
            # Random assignment for remaining
            labels.append(random.choice(INTENT_LABELS))
    
    return texts[:n_samples], labels

def train_classifier():
    """Train the intent classifier."""
    
    # Load data
    df = load_training_data()
    
    # Create labels (synthetic for demo)
    texts, labels = create_synthetic_labels(df)
    
    # Train classifier
    classifier = IntentClassifier()
    classifier.train(texts, labels)
    
    # Save model
    model_dir = Path("models")
    classifier.save(model_dir)
    
    print("\nClassifier training complete!")
    
    return classifier

def main():
    """Main training function."""
    
    print("Starting model training...")
    
    # Train classifier
    classifier = train_classifier()
    
    print("\nAll models trained successfully!")

if __name__ == "__main__":
    main()
