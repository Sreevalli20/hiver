#!/usr/bin/env python3
"""
Derive intent taxonomy from real AmazonHelp conversations.
"""

import pandas as pd
from pathlib import Path
from collections import Counter
import re

def load_conversations():
    """Load processed conversations."""
    data_dir = Path("data/processed")
    
    # Load sample conversations for analysis
    sample_file = data_dir / "sample_conversations.csv"
    if sample_file.exists():
        df = pd.read_csv(sample_file)
        print(f"Loaded {len(df)} sample conversations")
        return df
    
    # Fallback to train set
    train_file = data_dir / "AmazonHelp_train.csv"
    if train_file.exists():
        df = pd.read_csv(train_file)
        print(f"Loaded {len(df)} training conversations")
        return df
    
    raise FileNotFoundError("No processed conversations found")

def analyze_customer_messages(df):
    """Analyze customer messages to identify intent patterns."""
    
    print("\nAnalyzing customer messages...")
    
    # Extract customer texts
    customer_texts = df['customer_text'].dropna().tolist()
    
    print(f"Total customer messages: {len(customer_texts)}")
    
    # Sample some messages for manual review
    print("\nSample customer messages:")
    for i, text in enumerate(customer_texts[:30], 1):
        print(f"{i}. {text[:200]}")
    
    # Analyze keywords and patterns
    keywords = {
        'order': ['order', 'delivery', 'package', 'shipped', 'tracking', 'arrive', 'delivered'],
        'refund': ['refund', 'return', 'money back', 'chargeback'],
        'billing': ['charge', 'payment', 'billing', 'credit card', 'charged', 'payment'],
        'account': ['account', 'login', 'password', 'access', 'sign in', 'locked'],
        'product': ['product', 'item', 'quality', 'defective', 'wrong', 'damaged'],
        'complaint': ['terrible', 'horrible', 'worst', 'awful', 'disappointed', 'angry', 'frustrated'],
        'escalation': ['sue', 'legal', 'lawyer', 'attorney', 'authorities', 'bbb', 'regulatory', 'threat'],
        'general': ['question', 'how', 'what', 'where', 'when', 'policy', 'hours', 'contact']
    }
    
    keyword_counts = {}
    for category, words in keywords.items():
        count = 0
        for text in customer_texts:
            text_lower = text.lower()
            for word in words:
                if word in text_lower:
                    count += 1
                    break
        keyword_counts[category] = count
    
    print("\nKeyword category frequencies:")
    for category, count in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {category}: {count} ({count/len(customer_texts)*100:.1f}%)")
    
    return customer_texts

def propose_intent_taxonomy():
    """Propose intent taxonomy based on real data analysis."""
    
    print("\n" + "="*60)
    print("PROPOSED INTENT TAXONOMY FOR AMAZONHELP")
    print("="*60)
    
    taxonomy = {
        'order_status': {
            'description': 'Customer asking about order location, tracking, delivery time, delivery status',
            'examples': [
                "Where is my order?",
                "When will my package arrive?",
                "My order is supposed to be delivered today",
                "Tracking hasn't updated",
                "Scheduled delivery date passed"
            ]
        },
        'order_issue': {
            'description': 'Customer reporting problems with received orders (wrong item, damaged, missing, lost)',
            'examples': [
                "Received wrong item",
                "Package was damaged",
                "Missing items from order",
                "Item not as described",
                "Package lost in transit"
            ]
        },
        'refund_request': {
            'description': 'Customer requesting refunds, returns, or cancellations',
            'examples': [
                "I want a refund",
                "Need to return this item",
                "Cancel my order",
                "Refund for damaged item",
                "When will I get my money back?"
            ]
        },
        'billing_issue': {
            'description': 'Customer reporting payment problems, charges, billing disputes, EMI issues',
            'examples': [
                "Charged wrong amount",
                "Duplicate charge on card",
                "Payment failed",
                "EMI issue",
                "Unexpected charge"
            ]
        },
        'account_access': {
            'description': 'Customer having trouble logging in, password reset, account locked, verification',
            'examples': [
                "Can't log into my account",
                "Password reset not working",
                "Account locked",
                "Can't access my profile",
                "Verification failing"
            ]
        },
        'account_issue': {
            'description': 'Customer needing to update account information, settings, preferences',
            'examples': [
                "Update email address",
                "Change phone number",
                "Update shipping address",
                "Account settings not saving",
                "Close my account"
            ]
        },
        'product_info': {
            'description': 'Customer asking about product details, specifications, availability, compatibility',
            'examples': [
                "Is this item in stock?",
                "What are the specifications?",
                "Does this come in other colors?",
                "Product compatibility question",
                "Warranty information"
            ]
        },
        'general_inquiry': {
            'description': 'General questions about policies, hours, services, contact information',
            'examples': [
                "What are your business hours?",
                "How do I contact support?",
                "Do you ship internationally?",
                "Return policy question",
                "Payment methods accepted"
            ]
        },
        'complaint': {
            'description': 'Customer expressing dissatisfaction, frustration, negative feedback about service',
            'examples': [
                "Terrible customer service",
                "Horrible experience",
                "Very disappointed",
                "Worst company ever",
                "Your team is rude"
            ]
        },
        'escalation_required': {
            'description': 'Legal threats, security issues, regulatory complaints, requests for managers, serious allegations',
            'examples': [
                "I'm going to sue you",
                "Legal action will be taken",
                "This is a scam",
                "Reporting to authorities",
                "I need to speak to a manager"
            ]
        }
    }
    
    for intent, info in taxonomy.items():
        print(f"\n{intent}:")
        print(f"  Description: {info['description']}")
        print(f"  Examples:")
        for ex in info['examples']:
            print(f"    - {ex}")
    
    return taxonomy

def main():
    """Main analysis function."""
    
    # Load conversations
    df = load_conversations()
    
    # Analyze customer messages
    customer_texts = analyze_customer_messages(df)
    
    # Propose taxonomy
    taxonomy = propose_intent_taxonomy()
    
    # Save taxonomy
    output_file = Path("data/intent_taxonomy.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    import json
    with open(output_file, 'w') as f:
        json.dump(taxonomy, f, indent=2)
    
    print(f"\nIntent taxonomy saved to {output_file}")

if __name__ == "__main__":
    main()
