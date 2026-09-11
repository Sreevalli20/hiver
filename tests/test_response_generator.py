"""
Tests for the response generator.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from app.response_generator import ResponseGenerator

def test_response_generation():
    """Test response generation."""
    generator = ResponseGenerator()
    
    response = generator.generate("order_status", [], 0.8)
    
    assert isinstance(response, str)
    assert len(response) > 0
    assert len(response) > 10  # Should be substantive
    print("✓ Response generation test passed")

def test_response_with_evidence():
    """Test response generation with evidence."""
    generator = ResponseGenerator()
    
    evidence = [
        {
            'customer_message': 'Where is my order?',
            'brand_response': 'Your order is in transit',
            'similarity': 0.8,
            'conversation_id': 'conv_1'
        }
    ]
    
    response, summary = generator.generate_with_evidence("order_status", evidence, 0.8)
    
    assert isinstance(response, str)
    assert len(response) > 0
    assert isinstance(summary, str)
    assert len(summary) > 0
    print("✓ Response with evidence test passed")

def test_low_confidence_response():
    """Test response for low confidence."""
    generator = ResponseGenerator()
    
    response = generator.generate("order_status", [], 0.3)
    
    assert isinstance(response, str)
    assert len(response) > 0
    # Low confidence should trigger cautious response
    assert 'understand' in response.lower() or 'details' in response.lower()
    print("✓ Low confidence response test passed")

def test_all_intents_have_templates():
    """Test that all intents have response templates."""
    generator = ResponseGenerator()
    
    for intent in generator.templates.keys():
        response = generator.generate(intent, [], 0.8)
        assert len(response) > 0
    
    print("✓ All intents have templates test passed")

if __name__ == "__main__":
    test_response_generation()
    test_response_with_evidence()
    test_low_confidence_response()
    test_all_intents_have_templates()
    print("\nAll response generator tests passed!")
