"""
Escalation policy for determining auto-handle vs human escalation.
"""

from app.intents import is_escalation_intent, can_auto_handle

class EscalationPolicy:
    """Policy for deciding when to escalate to a human."""
    
    def __init__(self, confidence_threshold=0.6, similarity_threshold=0.3):
        """
        Initialize escalation policy.
        
        Args:
            confidence_threshold: Minimum classifier confidence for auto-handling
            similarity_threshold: Minimum retrieval similarity for auto-handling
        """
        self.confidence_threshold = confidence_threshold
        self.similarity_threshold = similarity_threshold
    
    def decide(self, intent, confidence, evidence):
        """
        Make escalation decision.
        
        Args:
            intent: Predicted intent
            confidence: Classifier confidence
            evidence: Retrieved historical evidence
            
        Returns:
            Dictionary with decision and reason
        """
        decision = "AUTO_HANDLE"
        reason = ""
        signals = {
            'intent': intent,
            'confidence': confidence,
            'has_evidence': len(evidence) > 0,
            'max_similarity': max([e['similarity'] for e in evidence]) if evidence else 0,
            'is_escalation_intent': is_escalation_intent(intent),
            'can_auto_handle': can_auto_handle(intent)
        }
        
        # Rule 1: Always escalate for escalation-required intents
        if is_escalation_intent(intent):
            decision = "ESCALATE"
            reason = f"Intent '{intent}' requires human intervention due to complexity or risk"
        
        # Rule 2: Escalate if confidence is too low
        elif confidence < self.confidence_threshold:
            decision = "ESCALATE"
            reason = f"Classifier confidence ({confidence:.2f}) below threshold ({self.confidence_threshold})"
        
        # Rule 3: Escalate if no similar historical evidence
        elif not evidence or signals['max_similarity'] < self.similarity_threshold:
            decision = "ESCALATE"
            reason = f"Insufficient historical precedent (max similarity: {signals['max_similarity']:.2f})"
        
        # Rule 4: Escalate for intents that shouldn't be auto-handled
        elif not can_auto_handle(intent):
            decision = "ESCALATE"
            reason = f"Intent '{intent}' requires human review for proper resolution"
        
        # Otherwise, auto-handle
        else:
            reason = f"Confident prediction ({confidence:.2f}) with sufficient historical evidence ({signals['max_similarity']:.2f})"
        
        return {
            'decision': decision,
            'reason': reason,
            'signals': signals
        }
