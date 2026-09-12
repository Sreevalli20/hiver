"""
Intent classifier using TF-IDF + Logistic Regression.
"""

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from pathlib import Path
import pickle

# Get repository root (parent of backend directory)
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = REPO_ROOT / "models"

class IntentClassifier:
    """TF-IDF + Logistic Regression intent classifier."""
    
    def __init__(self, model_path=None):
        """
        Initialize classifier.
        
        Args:
            model_path: Path to saved model files (defaults to MODELS_DIR)
        """
        self.vectorizer = None
        self.classifier = None
        self.label_encoder = None
        self.is_trained = False
        
        if model_path is None:
            model_path = MODELS_DIR
        
        if model_path:
            self.load(model_path)
    
    def train(self, texts, labels):
        """
        Train the classifier.
        
        Args:
            texts: List of training text samples
            labels: List of corresponding intent labels
        """
        print("Training intent classifier...")
        
        # Encode labels
        self.label_encoder = LabelEncoder()
        encoded_labels = self.label_encoder.fit_transform(labels)
        
        # Adjust min_df based on dataset size to handle small datasets
        min_df = min(2, max(1, len(texts) // 10))
        
        # Create TF-IDF features
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            min_df=min_df,
            stop_words='english'
        )
        X_train = self.vectorizer.fit_transform(texts)
        
        # Train classifier
        self.classifier = LogisticRegression(
            max_iter=1000,
            class_weight='balanced',
            random_state=42
        )
        self.classifier.fit(X_train, encoded_labels)
        
        self.is_trained = True
        print(f"Training complete. Classes: {len(self.label_encoder.classes_)}")
    
    def predict(self, text):
        """
        Predict intent for a single text.
        
        Args:
            text: Input text to classify
            
        Returns:
            Dictionary with intent, confidence, and probabilities
        """
        if not self.is_trained:
            raise ValueError("Classifier not trained. Call train() first.")
        
        # Transform text
        X = self.vectorizer.transform([text])
        
        # Get prediction
        encoded_pred = self.classifier.predict(X)[0]
        intent = self.label_encoder.inverse_transform([encoded_pred])[0]
        
        # Get confidence (probability of predicted class)
        probabilities = self.classifier.predict_proba(X)[0]
        confidence = np.max(probabilities)
        
        # Get all class probabilities
        class_probs = {
            self.label_encoder.inverse_transform([i])[0]: prob
            for i, prob in enumerate(probabilities)
        }
        
        return {
            'intent': intent,
            'confidence': float(confidence),
            'probabilities': class_probs
        }
    
    def predict_batch(self, texts):
        """
        Predict intents for multiple texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of prediction dictionaries
        """
        if not self.is_trained:
            raise ValueError("Classifier not trained. Call train() first.")
        
        X = self.vectorizer.transform(texts)
        encoded_preds = self.classifier.predict(X)
        intents = self.label_encoder.inverse_transform(encoded_preds)
        probabilities = self.classifier.predict_proba(X)
        
        results = []
        for i, intent in enumerate(intents):
            confidence = np.max(probabilities[i])
            class_probs = {
                self.label_encoder.inverse_transform([j])[0]: prob
                for j, prob in enumerate(probabilities[i])
            }
            results.append({
                'intent': intent,
                'confidence': float(confidence),
                'probabilities': class_probs
            })
        
        return results
    
    def save(self, model_dir):
        """
        Save trained model to disk.
        
        Args:
            model_dir: Directory to save model files
        """
        model_dir = Path(model_dir)
        model_dir.mkdir(parents=True, exist_ok=True)
        
        joblib.dump(self.vectorizer, model_dir / 'vectorizer.joblib')
        joblib.dump(self.classifier, model_dir / 'classifier.joblib')
        joblib.dump(self.label_encoder, model_dir / 'label_encoder.joblib')
        
        print(f"Model saved to {model_dir}")
    
    def load(self, model_dir):
        """
        Load trained model from disk.
        
        Args:
            model_dir: Directory containing model files
        """
        model_dir = Path(model_dir)
        
        try:
            self.vectorizer = joblib.load(model_dir / 'vectorizer.joblib')
            self.classifier = joblib.load(model_dir / 'classifier.joblib')
            self.label_encoder = joblib.load(model_dir / 'label_encoder.joblib')
            self.is_trained = True
            print(f"Model loaded from {model_dir}")
        except Exception as e:
            print(f"Error loading classifier: {e}")
            print("Classifier not loaded - will need to be trained")
            self.is_trained = False
    
