#!/usr/bin/env python3
"""
Simple training script to generate lightweight model artifacts.
Uses TF-IDF + Logistic Regression with the existing sample data.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
import pickle

def main():
    print("Training lightweight models...")
    
    # Load sample data
    data_path = Path("data/processed/sample_conversations.csv")
    if not data_path.exists():
        print(f"Error: {data_path} not found")
        return
    
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} conversations")
    
    # Create simple intent labels based on customer text
    intents = []
    for text in df['customer_text']:
        if pd.isna(text):
            intents.append('general_inquiry')
            continue
        text_lower = str(text).lower()
        if 'order' in text_lower or 'delivery' in text_lower or 'package' in text_lower:
            intents.append('order_status')
        elif 'refund' in text_lower or 'money' in text_lower or 'charge' in text_lower:
            intents.append('refund_request')
        elif 'account' in text_lower or 'password' in text_lower or 'login' in text_lower:
            intents.append('account_issue')
        elif 'cancel' in text_lower:
            intents.append('cancellation')
        else:
            intents.append('general_inquiry')
    
    df['intent'] = intents
    
    print(f"Intent distribution: {pd.Series(intents).value_counts().to_dict()}")
    
    # Train classifier
    print("\nTraining classifier...")
    label_encoder = LabelEncoder()
    encoded_labels = label_encoder.fit_transform(intents)
    
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        min_df=1,
        stop_words='english'
    )
    X_train = vectorizer.fit_transform(df['customer_text'].fillna(''))
    
    classifier = LogisticRegression(
        max_iter=1000,
        class_weight='balanced',
        random_state=42
    )
    classifier.fit(X_train, encoded_labels)
    
    print("Classifier trained successfully")
    
    # Create models directory
    models_dir = Path("models")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Save classifier artifacts
    joblib.dump(vectorizer, models_dir / 'vectorizer.joblib')
    joblib.dump(classifier, models_dir / 'classifier.joblib')
    joblib.dump(label_encoder, models_dir / 'label_encoder.joblib')
    
    print(f"Saved classifier artifacts to {models_dir}")
    
    # Build retrieval corpus only (TF-IDF will be rebuilt on load for compatibility)
    print("\nBuilding retrieval corpus...")
    retrieval_corpus = df[['customer_text', 'brand_text', 'conversation_id']].copy()
    retrieval_corpus['customer_text'] = retrieval_corpus['customer_text'].fillna('')
    retrieval_corpus['brand_text'] = retrieval_corpus['brand_text'].fillna('')
    retrieval_corpus.to_csv(models_dir / 'retrieval_corpus.csv', index=False)
    
    # Save retrieval config (TF-IDF mode)
    config = {'use_semantic': False}
    with open(models_dir / 'retrieval_config.pkl', 'wb') as f:
        pickle.dump(config, f)
    
    print(f"Saved retrieval artifacts to {models_dir}")
    
    # Verify files
    print("\nVerifying artifacts...")
    for file in models_dir.iterdir():
        size = file.stat().st_size
        print(f"  {file.name}: {size} bytes")
    
    print("\nTraining complete!")

if __name__ == "__main__":
    main()
