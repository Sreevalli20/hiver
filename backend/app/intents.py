"""
Intent taxonomy for customer support classification.
Derived from historical customer support conversations.
"""

INTENT_TAXONOMY = {
    "order_status": {
        "name": "Order Status",
        "description": "Customer asking about the status of their order, including shipping, delivery, or tracking information.",
        "examples": [
            "Where is my order?",
            "Has my package shipped yet?",
            "Can you check the status of order #12345?",
            "I haven't received my delivery yet",
            "When will my order arrive?"
        ],
        "boundary": "Distinct from 'order_issue' which involves problems with the order. This is purely informational requests."
    },
    "order_issue": {
        "name": "Order Issue",
        "description": "Customer reporting problems with their order such as wrong items, damaged goods, missing items, or delivery problems.",
        "examples": [
            "I received the wrong item",
            "My package arrived damaged",
            "Missing items from my order",
            "Order never arrived but tracking says delivered",
            "Received defective product"
        ],
        "boundary": "Distinct from 'order_status' which is informational. This involves actual problems requiring resolution."
    },
    "refund_request": {
        "name": "Refund Request",
        "description": "Customer requesting a refund for a purchase, whether due to dissatisfaction, returns, or billing errors.",
        "examples": [
            "I want a refund",
            "Can I get my money back?",
            "Please refund my order",
            "Charge appeared twice on my card",
            "I need to return this for a refund"
        ],
        "boundary": "Distinct from 'billing_issue' which is about payment processing problems. This is about returning money."
    },
    "billing_issue": {
        "name": "Billing Issue",
        "description": "Customer experiencing problems with payment processing, incorrect charges, payment failures, or account balance issues.",
        "examples": [
            "My payment was declined",
            "I was charged the wrong amount",
            "Payment failed but I have funds",
            "Why was I charged twice?",
            "Billing statement doesn't match my order"
        ],
        "boundary": "Distinct from 'refund_request' which is about getting money back. This is about payment processing problems."
    },
    "account_access": {
        "name": "Account Access",
        "description": "Customer having trouble accessing their account, logging in, or managing account settings.",
        "examples": [
            "I can't log into my account",
            "Forgot my password",
            "Account locked",
            "Can't access my profile",
            "Need to reset my credentials"
        ],
        "boundary": "Distinct from 'account_issue' which is about account configuration. This is purely access-related."
    },
    "account_issue": {
        "name": "Account Issue",
        "description": "Customer reporting problems with their account configuration, settings, or account-related features.",
        "examples": [
            "My address is wrong",
            "Can't update my payment method",
            "Account settings not saving",
            "Profile information is incorrect",
            "Need to change account details"
        ],
        "boundary": "Distinct from 'account_access' which is about logging in. This is about account configuration."
    },
    "product_info": {
        "name": "Product Information",
        "description": "Customer asking for information about products, features, specifications, or availability.",
        "examples": [
            "Is this product in stock?",
            "What are the specifications?",
            "Does this come in other colors?",
            "Is this compatible with X?",
            "Can you tell me more about this product?"
        ],
        "boundary": "Distinct from 'order_issue' which involves problems. This is purely informational queries."
    },
    "general_inquiry": {
        "name": "General Inquiry",
        "description": "Customer asking general questions that don't fit into specific categories, including policies, hours, or general support.",
        "examples": [
            "What are your business hours?",
            "Do you ship internationally?",
            "What's your return policy?",
            "How do I contact support?",
            "General question about your service"
        ],
        "boundary": "Catch-all for inquiries that don't fit other specific categories."
    },
    "complaint": {
        "name": "Complaint",
        "description": "Customer expressing dissatisfaction or frustration about their experience, service, or product without a specific actionable request.",
        "examples": [
            "Terrible service",
            "Very disappointed with my experience",
            "Your customer service is awful",
            "I'm very unhappy with this",
            "This is unacceptable"
        ],
        "boundary": "Distinct from specific issue categories. This is general dissatisfaction without a clear resolution request."
    },
    "escalation_required": {
        "name": "Escalation Required",
        "description": "Issues that require human intervention due to complexity, security concerns, legal threats, or account-specific sensitive matters.",
        "examples": [
            "I'm going to sue",
            "This is a security issue",
            "I need to speak to a manager",
            "Legal action will be taken",
            "This involves my personal data security"
        ],
        "boundary": "Reserved for high-risk or complex cases that should never be auto-handled."
    }
}

INTENT_LABELS = list(INTENT_TAXONOMY.keys())
NUM_INTENTS = len(INTENT_LABELS)

# Intents that should always trigger escalation
ESCALATION_INTENTS = ["escalation_required"]

# Intents that may be auto-handled with sufficient confidence
AUTO_HANDLE_INTENTS = [
    "order_status",
    "product_info",
    "general_inquiry"
]

def get_intent_info(intent_label):
    """Get detailed information about an intent."""
    return INTENT_TAXONOMY.get(intent_label, {})

def is_escalation_intent(intent_label):
    """Check if an intent should always trigger escalation."""
    return intent_label in ESCALATION_INTENTS

def can_auto_handle(intent_label):
    """Check if an intent can potentially be auto-handled."""
    return intent_label in AUTO_HANDLE_INTENTS
