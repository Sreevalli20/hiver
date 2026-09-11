"""
FastAPI backend for the AI Support Agent.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import pandas as pd

from app.classifier import IntentClassifier
from app.retrieval import RetrievalSystem
from app.response_generator import ResponseGenerator
from app.escalation import EscalationPolicy
from app.intents import INTENT_TAXONOMY, INTENT_LABELS

# Initialize FastAPI app
app = FastAPI(
    title="Hiver AI Support Agent",
    description="AI-powered customer support agent with intent classification and grounded response generation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model instances
classifier = None
retrieval_system = None
response_generator = None
escalation_policy = None
models_loaded = False

# Pydantic models
class PredictRequest(BaseModel):
    message: str
    use_semantic: Optional[bool] = True

class PredictResponse(BaseModel):
    intent: str
    confidence: float
    decision: str
    reason: str
    reply: str
    evidence: List[dict]
    signals: dict

class MetricsResponse(BaseModel):
    intent_macro_f1: Optional[float] = None
    intent_accuracy: Optional[float] = None
    escalation_f1: Optional[float] = None
    escalation_recall: Optional[float] = None
    reply_quality: Optional[float] = None
    baseline_comparison: Optional[dict] = None

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

def load_models():
    """Load all models on startup."""
    global classifier, retrieval_system, response_generator, escalation_policy, models_loaded
    
    try:
        # Backend now runs from repository root, models are in models/
        model_dir = Path("models")
        print(f"Looking for models in: {model_dir}")
        print(f"Model directory exists: {model_dir.exists()}")
        print(f"Current working directory: {Path.cwd()}")
        
        # Load classifier
        if (model_dir / 'classifier.joblib').exists():
            print("Found classifier.joblib, loading...")
            classifier = IntentClassifier(model_dir)
            print("Classifier loaded successfully")
        else:
            print(f"Warning: Classifier not found at {model_dir / 'classifier.joblib'}. Models need to be trained.")
        
        # Load retrieval system
        if (model_dir / 'retrieval_corpus.csv').exists():
            print("Found retrieval_corpus.csv, loading...")
            retrieval_system = RetrievalSystem()
            retrieval_system.load(model_dir)
            print("Retrieval system loaded successfully")
        else:
            print(f"Warning: Retrieval system not found at {model_dir / 'retrieval_corpus.csv'}. Models need to be trained.")
        
        # Initialize response generator
        response_generator = ResponseGenerator()
        
        # Initialize escalation policy
        escalation_policy = EscalationPolicy()
        
        # Only set models_loaded to true if both classifier and retrieval are loaded
        models_loaded = classifier is not None and retrieval_system is not None
        print(f"Final state: models_loaded={models_loaded}, classifier={classifier is not None}, retrieval={retrieval_system is not None}")
        if models_loaded:
            print("All models loaded successfully")
        else:
            print(f"Models partially loaded: classifier={classifier is not None}, retrieval={retrieval_system is not None}")
        
    except Exception as e:
        print(f"Error loading models: {e}")
        import traceback
        traceback.print_exc()
        models_loaded = False

@app.on_event("startup")
async def startup_event():
    """Load models on startup."""
    load_models()

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    model_dir = Path("models")
    model_files = {
        "models_dir_exists": model_dir.exists(),
        "classifier_joblib": (model_dir / 'classifier.joblib').exists(),
        "label_encoder_joblib": (model_dir / 'label_encoder.joblib').exists(),
        "vectorizer_joblib": (model_dir / 'vectorizer.joblib').exists(),
        "retrieval_corpus_csv": (model_dir / 'retrieval_corpus.csv').exists(),
        "tfidf_vectorizer_joblib": (model_dir / 'tfidf_vectorizer.joblib').exists(),
        "tfidf_matrix_joblib": (model_dir / 'tfidf_matrix.joblib').exists(),
        "retrieval_config_pkl": (model_dir / 'retrieval_config.pkl').exists(),
    }
    return {
        "status": "healthy",
        "models_loaded": models_loaded,
        "classifier_loaded": classifier is not None,
        "retrieval_loaded": retrieval_system is not None,
        "model_files": model_files
    }

@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    """
    Main prediction endpoint.
    
    Classifies intent, retrieves historical evidence, generates response,
    and makes escalation decision.
    """
    if not models_loaded:
        raise HTTPException(status_code=503, detail="Models not loaded. Please train models first.")
    
    try:
        # Classify intent
        classification = classifier.predict(request.message)
        intent = classification['intent']
        confidence = classification['confidence']
        
        # Retrieve historical evidence
        evidence = retrieval_system.retrieve(request.message, k=5)
        
        # Generate response
        reply, evidence_summary = response_generator.generate_with_evidence(
            intent, evidence, confidence
        )
        
        # Make escalation decision
        escalation_decision = escalation_policy.decide(intent, confidence, evidence)
        
        return PredictResponse(
            intent=intent,
            confidence=confidence,
            decision=escalation_decision['decision'],
            reason=escalation_decision['reason'],
            reply=reply,
            evidence=evidence,
            signals=escalation_decision['signals']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Get evaluation metrics."""
    # Load metrics from evaluation results if available
    metrics_file = Path("evaluation/results/metrics.json")
    
    if metrics_file.exists():
        import json
        with open(metrics_file, 'r') as f:
            metrics_data = json.load(f)
        
        return MetricsResponse(
            intent_macro_f1=metrics_data.get('intent', {}).get('macro_f1'),
            intent_accuracy=metrics_data.get('intent', {}).get('accuracy'),
            escalation_f1=metrics_data.get('escalation', {}).get('f1'),
            escalation_recall=metrics_data.get('escalation', {}).get('recall'),
            reply_quality=metrics_data.get('reply_quality'),
            baseline_comparison=metrics_data.get('baseline_comparison')
        )
    
    return MetricsResponse(
        intent_macro_f1=None,
        intent_accuracy=None,
        escalation_f1=None,
        escalation_recall=None,
        reply_quality=None,
        baseline_comparison=None
    )

@app.get("/examples", response_model=List[ExampleResponse])
async def get_examples():
    """Get example messages from golden set."""
    golden_file = Path("golden/golden_200.csv")
    
    if not golden_file.exists():
        return []
    
    df = pd.read_csv(golden_file)
    examples = []
    
    for _, row in df.head(10).iterrows():
        examples.append(ExampleResponse(
            id=str(row.get('id', '')),
            message=row.get('message', ''),
            intent=row.get('intent', ''),
            expected_action=row.get('expected_action', ''),
            difficulty=row.get('difficulty', '')
        ))
    
    return examples

@app.get("/metadata", response_model=MetadataResponse)
async def get_metadata():
    """Get system metadata."""
    brand_file = Path("data/selected_brand.txt")
    brand = "Unknown"
    if brand_file.exists():
        brand = brand_file.read_text().strip()
    
    dataset_size = None
    corpus_file = Path("models/retrieval_corpus.csv")
    if corpus_file.exists():
        df = pd.read_csv(corpus_file)
        dataset_size = len(df)
    
    return MetadataResponse(
        brand=brand,
        intents=INTENT_LABELS,
        num_intents=len(INTENT_LABELS),
        model_version="1.0.0",
        dataset_size=dataset_size
    )

@app.post("/evaluate")
async def run_evaluation(background_tasks: BackgroundTasks):
    """Trigger evaluation run in background."""
    # In a real implementation, this would trigger the evaluation script
    return {"status": "Evaluation triggered", "message": "Check evaluation/results/ for output"}

@app.get("/api/golden")
async def get_golden_data():
    """Get golden set annotation data."""
    annotation_file = Path("golden/golden_annotation.csv")
    
    if not annotation_file.exists():
        # Fall back to original golden_200.csv if annotation file doesn't exist
        annotation_file = Path("golden/golden_200.csv")
    
    if not annotation_file.exists():
        return []
    
    df = pd.read_csv(annotation_file)
    
    # Map column names if using original file
    if 'heuristic_intent' not in df.columns and 'intent' in df.columns:
        df = df.rename(columns={'intent': 'heuristic_intent', 'expected_action': 'heuristic_action'})
        df['human_intent'] = ''
        df['human_action'] = ''
        df['annotation_notes'] = ''
    
    return df.to_dict(orient='records')

@app.post("/api/golden")
async def save_golden_data(data: dict):
    """Save golden set annotation data."""
    annotation_file = Path("golden/golden_annotation.csv")
    
    try:
        df = pd.DataFrame(data['data'])
        df.to_csv(annotation_file, index=False)
        return {"status": "success", "message": "Annotation data saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
