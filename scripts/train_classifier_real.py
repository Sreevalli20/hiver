#!/usr/bin/env python3
"""
Train intent classifier using real labeled data from golden set.
"""

import pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.classifier import IntentClassifier

def heuristic_label(text):
    """Apply heuristic rules to label customer messages."""
    if pd.isna(text):
        return 'general_inquiry'
    
    text_lower = str(text).lower()
    
    # Escalation required (highest priority)
    escalation_keywords = ['sue', 'legal', 'lawyer', 'attorney', 'authorities', 'bbb', 'regulatory', 'threat', 'scam', 'fraud', 'police', 'court', 'lawsuit']
    if any(kw in text_lower for kw in escalation_keywords):
        return 'escalation_required'
    
    # Complaint
    complaint_keywords = ['terrible', 'horrible', 'worst', 'awful', 'disappointed', 'angry', 'frustrated', 'useless', 'rude', 'corrupt', 'mannerless', 'shame', 'disgrace']
    if any(kw in text_lower for kw in complaint_keywords):
        return 'complaint'
    
    # Order status
    order_status_keywords = ['where is my order', 'when will', 'delivery', 'tracking', 'arrive', 'delivered', 'shipped', 'package', 'status', 'scheduled']
    if any(kw in text_lower for kw in order_status_keywords):
        return 'order_status'
    
    # Order issue
    order_issue_keywords = ['wrong item', 'damaged', 'missing', 'lost', 'not as described', 'defective', 'broken', 'never received', 'didn\'t receive']
    if any(kw in text_lower for kw in order_issue_keywords):
        return 'order_issue'
    
    # Refund request
    refund_keywords = ['refund', 'return', 'money back', 'chargeback', 'cancel']
    if any(kw in text_lower for kw in refund_keywords):
        return 'refund_request'
    
    # Billing issue
    billing_keywords = ['charge', 'payment', 'billing', 'credit card', 'charged', 'emi', 'transaction']
    if any(kw in text_lower for kw in billing_keywords):
        return 'billing_issue'
    
    # Account access
    account_access_keywords = ['log in', 'login', 'password', 'access', 'sign in', 'locked', 'verify', 'authentication']
    if any(kw in text_lower for kw in account_access_keywords):
        return 'account_access'
    
    # Account issue
    account_issue_keywords = ['update', 'change', 'email', 'phone', 'address', 'settings', 'close account', 'delete account']
    if any(kw in text_lower for kw in account_issue_keywords):
        return 'account_issue'
    
    # Product info
    product_keywords = ['stock', 'specification', 'color', 'size', 'compatible', 'warranty', 'available']
    if any(kw in text_lower for kw in product_keywords):
        return 'product_info'
    
    # Default to general inquiry
    return 'general_inquiry'

def load_training_data():
    """Load training data from processed conversations with heuristic labels."""
    
    print("Loading training data...")
    
    # Load golden set for labels
    golden_file = Path("golden/golden_200.csv")
    if not golden_file.exists():
        raise FileNotFoundError("Golden set not found. Run create_golden_set.py first.")
    
    golden_df = pd.read_csv(golden_file)
    print(f"Loaded {len(golden_df)} labeled examples from golden set")
    
    # Also load additional training data from processed conversations
    # and apply heuristic labeling
    data_dir = Path("data/processed")
    train_file = data_dir / "AmazonHelp_train.csv"
    
    if train_file.exists():
        train_df = pd.read_csv(train_file)
        print(f"Loaded {len(train_df)} additional training conversations")
        
        # Apply heuristic labeling to additional data
        additional_labeled = []
        for idx, row in train_df.iterrows():
            customer_text = row['customer_text']
            if pd.isna(customer_text):
                continue
            intent = heuristic_label(customer_text)
            additional_labeled.append({
                'message': customer_text,
                'intent': intent
            })
        
        additional_df = pd.DataFrame(additional_labeled)
        print(f"Labeled {len(additional_df)} additional examples")
        
        # Combine golden set with additional data
        combined = pd.concat([golden_df[['message', 'intent']], additional_df], ignore_index=True)
        print(f"Total training examples: {len(combined)}")
    else:
        combined = golden_df[['message', 'intent']]
        print(f"Using only golden set: {len(combined)} examples")
    
    return combined

def main():
    """Train classifier with real data."""
    
    # Load training data
    train_df = load_training_data()
    
    # Extract texts and labels
    # Filter out NaN values
    train_df = train_df.dropna(subset=['message'])
    texts = train_df['message'].tolist()
    labels = train_df['intent'].tolist()
    
    print(f"\nTraining with {len(texts)} examples")
    print(f"Intent distribution:")
    for intent in train_df['intent'].unique():
        count = (train_df['intent'] == intent).sum()
        print(f"  {intent}: {count} ({count/len(train_df)*100:.1f}%)")
    
    # Initialize and train classifier
    classifier = IntentClassifier()
    classifier.train(texts, labels)
    
    # Save model
    model_dir = Path("models")
    classifier.save(model_dir)
    
    print(f"\nModel trained and saved to {model_dir}")
    
    # Test on a few examples
    print("\nTesting on sample messages:")
    test_messages = [
        "Where is my order?",
        "I received the wrong item",
        "I want a refund",
        "I'm going to sue you",
        "What are your business hours?"
    ]
    
    for msg in test_messages:
        result = classifier.predict(msg)
        print(f"  '{msg}' -> {result['intent']} (confidence: {result['confidence']:.2f})")

if __name__ == "__main__":
    main()
