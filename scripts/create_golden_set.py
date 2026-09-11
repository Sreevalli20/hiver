#!/usr/bin/env python3
"""
Create a genuinely curated golden set from real AmazonHelp conversations.
This script samples real conversations and applies heuristic labeling for evaluation.
"""

import pandas as pd
from pathlib import Path
import json
import re

def load_conversations():
    """Load processed conversations."""
    data_dir = Path("data/processed")
    
    # Load all splits to get maximum real data
    train_file = data_dir / "AmazonHelp_train.csv"
    dev_file = data_dir / "AmazonHelp_dev.csv"
    test_file = data_dir / "AmazonHelp_test.csv"
    
    dfs = []
    for file in [train_file, dev_file, test_file]:
        if file.exists():
            df = pd.read_csv(file)
            dfs.append(df)
            print(f"Loaded {len(df)} from {file.name}")
    
    if not dfs:
        raise FileNotFoundError("No processed conversations found")
    
    combined = pd.concat(dfs, ignore_index=True)
    print(f"Total conversations: {len(combined)}")
    
    return combined

def load_intent_taxonomy():
    """Load the intent taxonomy."""
    taxonomy_file = Path("data/intent_taxonomy.json")
    if taxonomy_file.exists():
        with open(taxonomy_file, 'r') as f:
            return json.load(f)
    return None

def heuristic_label(text):
    """
    Apply heuristic rules to label customer messages.
    This is a deterministic approach for creating the golden set.
    """
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

def determine_expected_action(intent):
    """Determine expected action based on intent."""
    if intent == 'escalation_required':
        return 'ESCALATE'
    elif intent in ['complaint', 'order_issue', 'billing_issue', 'refund_request']:
        return 'ESCALATE'
    else:
        return 'AUTO_HANDLE'

def determine_difficulty(intent, text):
    """Determine difficulty based on intent and text complexity."""
    if pd.isna(text):
        text = ""
    text_lower = str(text).lower()
    
    if intent == 'escalation_required':
        return 'Hard'
    
    # Check for complexity indicators
    if len(text) > 150 or text.count('?') > 1 or 'but' in text_lower or 'however' in text_lower:
        return 'Medium'
    
    if intent in ['complaint', 'order_issue', 'billing_issue']:
        return 'Medium'
    
    return 'Easy'

def create_golden_set(df, n=200):
    """Create golden set from real conversations with stratified sampling."""
    
    print(f"\nCreating golden set with {n} real examples...")
    
    # First, label all conversations
    all_labeled = []
    for idx, row in df.iterrows():
        customer_text = row['customer_text']
        intent = heuristic_label(customer_text)
        all_labeled.append({
            'customer_text': customer_text,
            'intent': intent,
            'conversation_id': row['conversation_id'],
            'brand_text': row.get('brand_text', '')
        })
    
    labeled_df = pd.DataFrame(all_labeled)
    
    # Target distribution: roughly equal across 10 intents
    target_per_intent = n // 10
    
    golden_data = []
    intent_counts = {}
    
    # Stratified sample by intent
    for intent in labeled_df['intent'].unique():
        intent_df = labeled_df[labeled_df['intent'] == intent]
        available = len(intent_df)
        
        # Sample min(available, target_per_intent)
        n_sample = min(available, target_per_intent)
        if n_sample == 0:
            continue
        
        sampled = intent_df.sample(n=n_sample, random_state=42)
        
        for idx, row in sampled.iterrows():
            expected_action = determine_expected_action(intent)
            difficulty = determine_difficulty(intent, row['customer_text'])
            
            golden_data.append({
                'id': len(golden_data) + 1,
                'message': row['customer_text'],
                'intent': intent,
                'expected_action': expected_action,
                'difficulty': difficulty,
                'notes': f'Heuristically labeled from real conversation {row["conversation_id"]}'
            })
            
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
    
    # If we have fewer than n, fill with remaining data
    if len(golden_data) < n:
        remaining = n - len(golden_data)
        used_ids = set([item['conversation_id'] for item in golden_data])
        remaining_df = labeled_df[~labeled_df['conversation_id'].isin(used_ids)]
        
        if len(remaining_df) > 0:
            extra_sample = remaining_df.sample(n=min(remaining, len(remaining_df)), random_state=42)
            for idx, row in extra_sample.iterrows():
                intent = row['intent']
                expected_action = determine_expected_action(intent)
                difficulty = determine_difficulty(intent, row['customer_text'])
                
                golden_data.append({
                    'id': len(golden_data) + 1,
                    'message': row['customer_text'],
                    'intent': intent,
                    'expected_action': expected_action,
                    'difficulty': difficulty,
                    'notes': f'Heuristically labeled from real conversation {row["conversation_id"]}'
                })
                
                intent_counts[intent] = intent_counts.get(intent, 0) + 1
    
    # Create DataFrame
    golden_df = pd.DataFrame(golden_data)
    
    print(f"\nIntent distribution in golden set:")
    for intent, count in sorted(intent_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {intent}: {count} ({count/len(golden_df)*100:.1f}%)")
    
    return golden_df

def main():
    """Main function to create golden set."""
    
    # Load conversations
    df = load_conversations()
    
    # Load taxonomy
    taxonomy = load_intent_taxonomy()
    if taxonomy:
        print(f"\nIntent taxonomy loaded with {len(taxonomy)} intents")
    
    # Create golden set
    golden_df = create_golden_set(df, n=200)
    
    # Save golden set
    output_dir = Path("golden")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "golden_200.csv"
    golden_df.to_csv(output_file, index=False)
    
    print(f"\nGolden set saved to {output_file}")
    print(f"Total examples: {len(golden_df)}")
    
    # Save metadata
    metadata = {
        'source': 'Real AmazonHelp conversations from Customer Support on Twitter dataset',
        'size': len(golden_df),
        'labeling_method': 'Heuristic keyword-based labeling (not manually labeled)',
        'sampling_method': 'Random sample from processed conversations',
        'date': '2024-09-11',
        'note': 'This is a heuristically labeled set for evaluation. For production, manual human labeling is recommended.'
    }
    
    metadata_file = output_dir / "golden_metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Metadata saved to {metadata_file}")

if __name__ == "__main__":
    main()
