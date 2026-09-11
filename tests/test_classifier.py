"""
Tests for the intent classifier.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from app.classifier import IntentClassifier
from app.intents import INTENT_LABELS

def test_classifier_training():
    """Test that classifier can be trained."""
    texts = [
        "Where is my order?",
        "I received the wrong item",
        "I want a refund",
        "My payment was declined",
        "I can't log into my account"
    ]
    labels = ["order_status", "order_issue", "refund_request", "billing_issue", "account_access"]
    
    classifier = IntentClassifier()
    classifier.train(texts, labels)
    
    assert classifier.is_trained
    assert len(classifier.label_encoder.classes_) > 0
    print("✓ Classifier training test passed")

def test_classifier_prediction():
    """Test that classifier can make predictions."""
    texts = [
        "Where is my order?",
        "I received the wrong item",
        "I want a refund",
        "My payment was declined",
        "I can't log into my account"
    ]
    labels = ["order_status", "order_issue", "refund_request", "billing_issue", "account_access"]
    
    classifier = IntentClassifier()
    classifier.train(texts, labels)
    
    result = classifier.predict("Where is my package?")
    
    assert 'intent' in result
    assert 'confidence' in result
    assert 0 <= result['confidence'] <= 1
    assert result['intent'] in INTENT_LABELS
    print("✓ Classifier prediction test passed")

def test_classifier_batch_prediction():
    """Test batch prediction."""
    texts = [
        "Where is my order?",
        "I received the wrong item",
        "I want a refund",
        "My payment was declined",
        "I can't log into my account"
    ]
    labels = ["order_status", "order_issue", "refund_request", "billing_issue", "account_access"]
    
    classifier = IntentClassifier()
    classifier.train(texts, labels)
    
    results = classifier.predict_batch(["Where is my package?", "Wrong item received"])
    
    assert len(results) == 2
    for result in results:
        assert 'intent' in result
        assert 'confidence' in result
    print("✓ Batch prediction test passed")

def test_empty_input():
    """Test handling of empty input."""
    texts = ["Where is my order?", "I want a refund"]
    labels = ["order_status", "refund_request"]
    
    classifier = IntentClassifier()
    classifier.train(texts, labels)
    
    result = classifier.predict("")
    
    assert 'intent' in result
    print("✓ Empty input test passed")

if __name__ == "__main__":
    test_classifier_training()
    test_classifier_prediction()
    test_classifier_batch_prediction()
    test_empty_input()
    print("\nAll classifier tests passed!")
