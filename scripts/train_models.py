#!/usr/bin/env python3
"""
Train lightweight models for Render build.
Uses TF-IDF + Logistic Regression for classifier and TF-IDF for retrieval.
"""

import pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.classifier import IntentClassifier
from app.retrieval import RetrievalSystem

def heuristic_label(text):
    """Apply heuristic rules to label customer messages."""
    if pd.isna(text) or text == '':
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

def load_training_data(max_samples=10000):
    """Load training data from golden set and sample conversations."""
    
    print("Loading training data...")
    
    # Load golden set for high-quality labeled examples
    golden_file = Path("golden/golden_200.csv")
    if golden_file.exists():
        golden_df = pd.read_csv(golden_file)
        print(f"Loaded {len(golden_df)} labeled examples from golden set")
        labeled_data = golden_df[['message', 'intent']].rename(columns={'message': 'text', 'intent': 'label'})
    else:
        labeled_data = pd.DataFrame(columns=['text', 'label'])
        print("Golden set not found, using only heuristic labeling")
    
    # Load sample conversations for additional training data
    sample_file = Path("data/processed/sample_conversations.csv")
    if sample_file.exists():
        sample_df = pd.read_csv(sample_file)
        print(f"Loaded {len(sample_df)} sample conversations")
        
        # Cap at max_samples for quick training
        if len(sample_df) > max_samples:
            sample_df = sample_df.head(max_samples)
            print(f"Capped to {max_samples} samples for quick training")
        
        # Apply heuristic labeling
        additional_labeled = []
        for idx, row in sample_df.iterrows():
            customer_text = row.get('customer_text', '')
            if pd.isna(customer_text) or customer_text == '':
                continue
            intent = heuristic_label(customer_text)
            additional_labeled.append({
                'text': customer_text,
                'label': intent
            })
        
        additional_df = pd.DataFrame(additional_labeled)
        print(f"Labeled {len(additional_df)} additional examples with heuristics")
        
        # Combine golden set with additional data
        combined = pd.concat([labeled_data, additional_df], ignore_index=True)
        print(f"Total training examples: {len(combined)}")
    else:
        combined = labeled_data
        print(f"Using only golden set: {len(combined)} examples")
    
    return combined

def load_retrieval_corpus(max_samples=10000):
    """Load corpus for retrieval from sample conversations."""
    
    print("Loading retrieval corpus...")
    
    sample_file = Path("data/processed/sample_conversations.csv")
    if not sample_file.exists():
        raise FileNotFoundError("Sample conversations not found")
    
    corpus_df = pd.read_csv(sample_file)
    
    # Cap at max_samples for quick indexing
    if len(corpus_df) > max_samples:
        corpus_df = corpus_df.head(max_samples)
        print(f"Capped to {max_samples} samples for quick indexing")
    
    print(f"Retrieval corpus: {len(corpus_df)} conversations")
    
    return corpus_df

def train_classifier():
    """Train intent classifier."""
    
    print("\n" + "="*50)
    print("TRAINING CLASSIFIER")
    print("="*50)
    
    # Load training data
    train_df = load_training_data(max_samples=10000)
    
    # Extract texts and labels
    train_df = train_df.dropna(subset=['text'])
    texts = train_df['text'].tolist()
    labels = train_df['label'].tolist()
    
    print(f"\nTraining with {len(texts)} examples")
    print(f"Intent distribution:")
    for intent in train_df['label'].unique():
        count = (train_df['label'] == intent).sum()
        print(f"  {intent}: {count} ({count/len(train_df)*100:.1f}%)")
    
    # Initialize and train classifier
    classifier = IntentClassifier()
    classifier.train(texts, labels)
    
    # Save model
    model_dir = Path("models")
    model_dir.mkdir(parents=True, exist_ok=True)
    classifier.save(model_dir)
    
    # Also save training data for rebuilding on startup (to avoid sklearn version issues)
    train_df.to_csv(model_dir / 'training_data.csv', index=False)
    
    print(f"\nClassifier trained and saved to {model_dir}")
    print(f"Training data also saved for rebuilding on startup")
    
    # Test on a few examples
    print("\nTesting classifier on sample messages:")
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

def build_retrieval():
    """Build retrieval index using TF-IDF."""
    
    print("\n" + "="*50)
    print("BUILDING RETRIEVAL INDEX")
    print("="*50)
    
    # Load corpus
    corpus_df = load_retrieval_corpus(max_samples=10000)
    
    # Initialize retrieval system with TF-IDF (force fallback for speed)
    retrieval = RetrievalSystem(use_semantic=False)
    
    # Build index
    retrieval.build_index(corpus_df)
    
    # Save only corpus (TF-IDF will be rebuilt on load to avoid version issues)
    model_dir = Path("models")
    model_dir.mkdir(parents=True, exist_ok=True)
    corpus_df.to_csv(model_dir / 'retrieval_corpus.csv', index=False)
    with open(model_dir / 'retrieval_config.pkl', 'wb') as f:
        import pickle
        pickle.dump({'use_semantic': False}, f)
    
    print(f"\nRetrieval corpus saved to {model_dir} (TF-IDF will be rebuilt on load)")
    
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
            print(f"     Customer: {result['customer_message'][:80]}...")
            print(f"     Brand: {result['brand_response'][:80]}...")

def main():
    """Main training function."""
    
    print("="*50)
    print("LIGHTWEIGHT MODEL TRAINING FOR RENDER")
    print("="*50)
    print(f"Current working directory: {Path.cwd()}")
    
    try:
        # Train classifier
        train_classifier()
        
        # Build retrieval index
        build_retrieval()
        
        print("\n" + "="*50)
        print("ALL MODELS TRAINED SUCCESSFULLY")
        print("="*50)
        
        # Verify models were created
        model_dir = Path("models")
        print(f"\nVerifying models in {model_dir}:")
        if model_dir.exists():
            for item in model_dir.iterdir():
                print(f"  - {item.name} ({item.stat().st_size} bytes)")
        else:
            print(f"  ERROR: Models directory not found at {model_dir}")
            raise FileNotFoundError("Models directory not created")
            
    except Exception as e:
        print(f"\n" + "="*50)
        print(f"ERROR: Training failed with exception: {e}")
        print("="*50)
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()
