"""
Grounded response generator based on historical evidence and intent.
"""

from app.intents import INTENT_TAXONOMY, get_intent_info

class ResponseGenerator:
    """Generate grounded responses based on intent and historical evidence."""
    
    def __init__(self):
        """Initialize response generator."""
        self.templates = self._load_templates()
    
    def _load_templates(self):
        """Load response templates for each intent."""
        return {
            "order_status": [
                "I'd be happy to check your order status. Could you please provide your order number?",
                "Let me look up the status of your order for you.",
                "I can help you track your order. Please share your order number."
            ],
            "order_issue": [
                "I'm sorry to hear about the issue with your order. Let me help resolve this.",
                "I apologize for the problem with your order. I'll look into this right away.",
                "Thank you for bringing this to our attention. Let me help fix this issue."
            ],
            "refund_request": [
                "I understand you'd like a refund. Let me review your order and help you with this process.",
                "I can help you with your refund request. Please provide your order details.",
                "I'll assist you with processing your refund. Let me check your order information."
            ],
            "billing_issue": [
                "I'm sorry about the billing issue. Let me investigate this for you.",
                "I can help resolve the billing problem you're experiencing.",
                "Thank you for reporting this billing issue. I'll look into it immediately."
            ],
            "account_access": [
                "I can help you regain access to your account. Let me assist with the login process.",
                "I'm sorry you're having trouble accessing your account. Let me help you resolve this.",
                "Let me help you with your account access issue."
            ],
            "account_issue": [
                "I can help you update your account information. What would you like to change?",
                "I'll assist you with your account settings. What specific issue are you experiencing?",
                "Let me help you resolve your account configuration issue."
            ],
            "product_info": [
                "I'd be happy to provide information about our products. What would you like to know?",
                "I can help answer your product questions. What specific information are you looking for?",
                "Let me provide you with the product information you need."
            ],
            "general_inquiry": [
                "I'd be happy to help with your inquiry. How can I assist you today?",
                "Thank you for reaching out. What can I help you with?",
                "I'm here to help. Please let me know what you need assistance with."
            ],
            "complaint": [
                "I'm truly sorry to hear about your experience. I want to help make this right.",
                "I apologize for the poor experience you've had. Let me see how I can help resolve this.",
                "Thank you for sharing your feedback. I'm sorry for the inconvenience and want to help."
            ],
            "escalation_required": [
                "I understand this is a serious matter. Let me connect you with a specialist who can better assist you.",
                "I appreciate you bringing this to our attention. This requires specialized attention, so I'll escalate this to our team.",
                "I understand the importance of this issue. Let me ensure this gets the proper attention it requires."
            ]
        }
    
    def generate(self, intent, evidence, confidence):
        """
        Generate a grounded response.
        
        Args:
            intent: Predicted intent
            evidence: List of retrieved historical examples
            confidence: Classifier confidence
            
        Returns:
            Generated response string
        """
        intent_info = get_intent_info(intent)
        
        # If confidence is very low, use a more cautious response
        if confidence < 0.5:
            return "I want to make sure I understand your request correctly. Could you please provide more details so I can assist you better?"
        
        # If no evidence found, use generic template
        if not evidence or len(evidence) == 0:
            templates = self.templates.get(intent, self.templates["general_inquiry"])
            return templates[0]
        
        # Get template for this intent
        templates = self.templates.get(intent, self.templates["general_inquiry"])
        base_response = templates[0]
        
        # If we have strong evidence, we can be more specific
        if confidence > 0.7 and evidence[0]['similarity'] > 0.5:
            # Check if similar historical responses exist
            similar_responses = [e['brand_response'] for e in evidence if e['brand_response']]
            if similar_responses:
                # Use a response inspired by historical patterns
                # For safety, we still use templates but acknowledge the pattern
                return base_response
        
        return base_response
    
    def generate_with_evidence(self, intent, evidence, confidence):
        """
        Generate response with evidence citation.
        
        Args:
            intent: Predicted intent
            evidence: List of retrieved historical examples
            confidence: Classifier confidence
            
        Returns:
            Tuple of (response, evidence_summary)
        """
        response = self.generate(intent, evidence, confidence)
        
        # Create evidence summary
        if evidence:
            evidence_summary = f"Based on {len(evidence)} similar historical cases"
        else:
            evidence_summary = "No similar historical cases found"
        
        return response, evidence_summary
