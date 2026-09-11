"""
Pydantic models for API requests and responses.
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class PredictRequest(BaseModel):
    message: str
    use_semantic: Optional[bool] = True

class EvidenceItem(BaseModel):
    customer_message: str
    brand_response: str
    similarity: float
    conversation_id: str

class PredictResponse(BaseModel):
    intent: str
    confidence: float
    decision: str
    reason: str
    reply: str
    evidence: List[EvidenceItem]
    signals: Dict[str, Any]

class MetricsResponse(BaseModel):
    intent_macro_f1: Optional[float] = None
    intent_accuracy: Optional[float] = None
    escalation_f1: Optional[float] = None
    escalation_recall: Optional[float] = None
    reply_quality: Optional[float] = None
    baseline_comparison: Optional[Dict[str, Any]] = None

class ExampleResponse(BaseModel):
    id: str
    message: str
    intent: str
    expected_action: str
    difficulty: str

class MetadataResponse(BaseModel):
    brand: str
    intents: List[str]
    num_intents: int
    model_version: str
    dataset_size: Optional[int] = None
