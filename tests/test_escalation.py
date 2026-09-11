"""
Tests for the escalation policy.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from app.escalation import EscalationPolicy
from app.intents import is_escalation_intent, can_auto_handle

def test_escalation_intent():
    """Test escalation intent detection."""
    assert is_escalation_intent("escalation_required") == True
    assert is_escalation_intent("order_status") == False
    print("✓ Escalation intent detection test passed")

def test_auto_handle_intent():
    """Test auto-handle intent detection."""
    assert can_auto_handle("order_status") == True
    assert can_auto_handle("escalation_required") == False
    print("✓ Auto-handle intent detection test passed")

def test_escalation_decision():
    """Test escalation decision making."""
    policy = EscalationPolicy()
    
    # Test escalation for escalation_required intent
    result = policy.decide("escalation_required", 0.9, [])
    assert result['decision'] == 'ESCALATE'
    assert 'escalation_required' in result['reason'].lower()
    
    # Test escalation for low confidence
    result = policy.decide("order_status", 0.4, [])
    assert result['decision'] == 'ESCALATE'
    assert 'confidence' in result['reason'].lower()
    
    # Test auto-handle for high confidence with evidence
    evidence = [{'similarity': 0.8}]
    result = policy.decide("order_status", 0.8, evidence)
    assert result['decision'] == 'AUTO_HANDLE'
    
    print("✓ Escalation decision test passed")

def test_escalation_signals():
    """Test escalation decision signals."""
    policy = EscalationPolicy()
    
    result = policy.decide("order_status", 0.7, [{'similarity': 0.5}])
    
    assert 'signals' in result
    assert 'intent' in result['signals']
    assert 'confidence' in result['signals']
    assert 'has_evidence' in result['signals']
    assert 'max_similarity' in result['signals']
    assert result['signals']['confidence'] == 0.7
    assert result['signals']['max_similarity'] == 0.5
    
    print("✓ Escalation signals test passed")

if __name__ == "__main__":
    test_escalation_intent()
    test_auto_handle_intent()
    test_escalation_decision()
    test_escalation_signals()
    print("\nAll escalation tests passed!")
