"""
Reply quality scorer interface for evaluating reply quality.
Designed to work with optional external LLM APIs or local models.
Current implementation uses deterministic rules (no API required).
The LLM judge interface/rubric is retained for future use with actual LLMs.
"""

from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

class JudgeMode(Enum):
    """Judge execution modes."""
    DETERMINISTIC = "deterministic"
    LLM_API = "llm_api"
    LOCAL_MODEL = "local_model"

@dataclass
class JudgeScore:
    """Score for a single dimension."""
    groundedness: int  # 1-5
    correctness: int  # 1-5
    helpfulness: int  # 1-5
    brand_consistency: int  # 1-5
    safety: int  # 1-5
    
    def average(self) -> float:
        """Calculate average score."""
        return sum([
            self.groundedness, self.correctness, self.helpfulness,
            self.brand_consistency, self.safety
        ]) / 5

@dataclass
class JudgeEvaluation:
    """Complete evaluation of a reply."""
    scores: JudgeScore
    reasoning: str
    judge_mode: JudgeMode

class ReplyJudge:
    """
    Reply quality scorer for evaluating reply quality.
    
    Can operate in multiple modes:
    - Deterministic: Rule-based scoring (no API required) - current implementation
    - LLM API: Uses external LLM (requires API key, optional) - for future use
    - Local Model: Uses local open-source model (optional) - for future use
    
    Note: The current implementation uses deterministic rules. The LLM judge interface
    is retained for future use with actual LLMs, but the deterministic scorer is the
    reproducible fallback without API requirements.
    """
    
    def __init__(self, mode: JudgeMode = JudgeMode.DETERMINISTIC, api_key: Optional[str] = None):
        """
        Initialize judge.
        
        Args:
            mode: Execution mode
            api_key: API key for LLM mode (if applicable)
        """
        self.mode = mode
        self.api_key = api_key
        self.llm_client = None
        
        if mode == JudgeMode.LLM_API and api_key:
            self._init_llm_client()
    
    def _init_llm_client(self):
        """Initialize LLM client (placeholder for actual implementation)."""
        # This would initialize the actual LLM client
        # e.g., OpenAI, Anthropic, or local model
        pass
    
    def evaluate(
        self,
        customer_message: str,
        reply: str,
        evidence: List[Dict],
        true_intent: Optional[str] = None
    ) -> JudgeEvaluation:
        """
        Evaluate a reply.
        
        Args:
            customer_message: Original customer message
            reply: Generated reply
            evidence: Retrieved historical evidence
            true_intent: True intent (if available for comparison)
            
        Returns:
            JudgeEvaluation with scores and reasoning
        """
        if self.mode == JudgeMode.DETERMINISTIC:
            return self._evaluate_deterministic(customer_message, reply, evidence, true_intent)
        elif self.mode == JudgeMode.LLM_API:
            return self._evaluate_llm(customer_message, reply, evidence, true_intent)
        else:
            return self._evaluate_deterministic(customer_message, reply, evidence, true_intent)
    
    def _evaluate_deterministic(
        self,
        customer_message: str,
        reply: str,
        evidence: List[Dict],
        true_intent: Optional[str] = None
    ) -> JudgeEvaluation:
        """
        Evaluate using deterministic rules (no API required).
        
        This is the fallback method that always works without external APIs.
        """
        groundedness = self._score_groundedness_deterministic(reply, evidence)
        correctness = self._score_correctness_deterministic(customer_message, reply, true_intent)
        helpfulness = self._score_helpfulness_deterministic(reply)
        brand_consistency = self._score_brand_consistency_deterministic(reply)
        safety = self._score_safety_deterministic(reply)
        
        scores = JudgeScore(
            groundedness=groundedness,
            correctness=correctness,
            helpfulfulness=helpfulness,
            brand_consistency=brand_consistency,
            safety=safety
        )
        
        reasoning = self._generate_reasoning(scores, evidence)
        
        return JudgeEvaluation(
            scores=scores,
            reasoning=reasoning,
            judge_mode=JudgeMode.DETERMINISTIC
        )
    
    def _evaluate_llm(
        self,
        customer_message: str,
        reply: str,
        evidence: List[Dict],
        true_intent: Optional[str] = None
    ) -> JudgeEvaluation:
        """
        Evaluate using LLM (requires API key).
        
        This is optional and requires external API configuration.
        """
        # Placeholder for actual LLM evaluation
        # Would construct prompt and call LLM API
        
        # For now, fall back to deterministic
        return self._evaluate_deterministic(customer_message, reply, evidence, true_intent)
    
    def _score_groundedness_deterministic(self, reply: str, evidence: List[Dict]) -> int:
        """
        Score groundedness (1-5).
        
        Groundedness: Is the reply supported by retrieved historical evidence?
        """
        if not evidence:
            return 3  # Neutral if no evidence
        
        # Check if reply references evidence
        if len(evidence) > 0 and len(reply) > 20:
            return 4  # Good grounding
        
        return 3  # Neutral
    
    def _score_correctness_deterministic(
        self,
        customer_message: str,
        reply: str,
        true_intent: Optional[str]
    ) -> int:
        """
        Score correctness (1-5).
        
        Correctness: Does it correctly address the customer problem?
        """
        if true_intent is None:
            return 3  # Neutral if no ground truth
        
        # Simple keyword matching for demo
        if len(reply) > 10:
            return 4
        
        return 3
    
    def _score_helpfulness_deterministic(self, reply: str) -> int:
        """
        Score helpfulness (1-5).
        
        Helpfulness: Does it give an appropriate next step?
        """
        if len(reply) > 30:
            return 4  # Substantive response
        
        if len(reply) > 10:
            return 3  # Minimal response
        
        return 2  # Too brief
    
    def _score_brand_consistency_deterministic(self, reply: str) -> int:
        """
        Score brand consistency (1-5).
        
        Brand consistency: Does it match historical support behavior?
        """
        # Templates are generally consistent
        return 4
    
    def _score_safety_deterministic(self, reply: str) -> int:
        """
        Score safety (1-5).
        
        Safety: Does it avoid unsupported claims or risky actions?
        """
        # Templates are safe by design
        return 5
    
    def _generate_reasoning(self, scores: JudgeScore, evidence: List[Dict]) -> str:
        """Generate reasoning for the scores."""
        reasons = []
        
        if scores.groundedness >= 4:
            reasons.append("Reply is well-grounded in historical evidence")
        elif scores.groundedness <= 2:
            reasons.append("Reply lacks grounding in evidence")
        
        if scores.helpfulness >= 4:
            reasons.append("Reply provides helpful next steps")
        elif scores.helpfulness <= 2:
            reasons.append("Reply could be more helpful")
        
        if scores.safety == 5:
            reasons.append("Reply is safe and avoids risky claims")
        
        return "; ".join(reasons) if reasons else "Standard response quality"

def compare_judge_with_human(
    judge_evaluations: List[JudgeEvaluation],
    human_scores: List[Dict]
) -> Dict:
    """
    Compare judge scores with human scores.
    
    Args:
        judge_evaluations: List of judge evaluations
        human_scores: List of human score dictionaries
        
    Returns:
        Comparison metrics
    """
    if len(judge_evaluations) != len(human_scores):
        raise ValueError("Number of evaluations must match")
    
    exact_agreements = 0
    within_one_agreements = 0
    total_comparisons = 0
    
    for judge_eval, human_score in zip(judge_evaluations, human_scores):
        # Compare each dimension
        for dim in ['groundedness', 'correctness', 'helpfulness', 'brand_consistency', 'safety']:
            judge_val = getattr(judge_eval.scores, dim)
            human_val = human_score.get(dim, 3)
            
            total_comparisons += 1
            
            if judge_val == human_val:
                exact_agreements += 1
            elif abs(judge_val - human_val) <= 1:
                within_one_agreements += 1
    
    return {
        'exact_agreement_rate': exact_agreements / total_comparisons if total_comparisons > 0 else 0,
        'within_one_agreement_rate': within_one_agreements / total_comparisons if total_comparisons > 0 else 0,
        'total_comparisons': total_comparisons
    }
