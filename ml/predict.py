"""
FeeAssist AI — Intent Prediction Module

Loads the champion trained classifier and TF-IDF vectorizer,
preprocesses incoming user queries (in English, Hindi, or Marathi),
and predicts the fee query intent along with mathematically sound
confidence scores derived from model probability distributions.
"""

import os
import sys
from typing import Dict, Any, Optional

# Ensure UTF-8 output encoding on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import joblib
import numpy as np

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Ensure root is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ml.preprocessing import preprocess

# Default model directory
DEFAULT_MODELS_DIR = os.path.join(BASE_DIR, "ml", "models")

# Module-level cache for lazy singleton loading
_CACHED_MODEL = None
_CACHED_VECTORIZER = None
_CACHED_ENCODER = None


def load_artifacts(models_dir: Optional[str] = None):
    """
    Load the trained classifier, vectorizer, and label encoder into memory.
    Caches artifacts globally to ensure fast subsequent inference.
    """
    global _CACHED_MODEL, _CACHED_VECTORIZER, _CACHED_ENCODER

    target_dir = models_dir or DEFAULT_MODELS_DIR

    model_path = os.path.join(target_dir, "best_model.joblib")
    vectorizer_path = os.path.join(target_dir, "tfidf_vectorizer.joblib")
    encoder_path = os.path.join(target_dir, "label_encoder.joblib")

    if not os.path.exists(model_path) or not os.path.exists(vectorizer_path) or not os.path.exists(encoder_path):
        raise FileNotFoundError(
            f"Required model artifacts missing in '{target_dir}'. "
            f"Please run 'python ml/train.py' first to train and save the champion model."
        )

    _CACHED_MODEL = joblib.load(model_path)
    _CACHED_VECTORIZER = joblib.load(vectorizer_path)
    _CACHED_ENCODER = joblib.load(encoder_path)

    return _CACHED_MODEL, _CACHED_VECTORIZER, _CACHED_ENCODER


def predict_intent(
    text: str,
    models_dir: Optional[str] = None,
    return_all_scores: bool = True,
) -> Dict[str, Any]:
    """
    Predict the fee-related intent of a raw user query with confidence scoring.

    Pipeline:
    1. Input Validation: Handles empty or whitespace-only queries gracefully.
    2. Text Preprocessing: Normalizes Unicode, filters domain stopwords, lemmatizes English.
    3. Feature Extraction: Transforms preprocessed text via fitted TF-IDF Vectorizer.
    4. Probabilistic Inference: Calculates calibrated probability distribution across all 10 intents.
    5. Ranking: Identifies argmax intent and associated confidence.

    Args:
        text: Raw natural language query in English, Hindi, or Marathi.
        models_dir: Optional custom path to model artifacts directory.
        return_all_scores: If True, includes probability breakdown for all intents.

    Returns:
        Structured dict with:
        - "intent": Name of predicted intent (e.g. "PENDING_FEE")
        - "confidence": Float between 0.0 and 1.0 (calibrated prediction confidence)
        - "all_scores": Optional dict mapping each intent to its confidence score
        - "preprocessed_text": Text after normalization and cleaning
    """
    global _CACHED_MODEL, _CACHED_VECTORIZER, _CACHED_ENCODER

    if _CACHED_MODEL is None or _CACHED_VECTORIZER is None or _CACHED_ENCODER is None:
        load_artifacts(models_dir)

    # 1. Edge Case: Empty or Non-string Input
    if not text or not isinstance(text, str) or not text.strip():
        fallback_scores = {cls_name: 0.0 for cls_name in _CACHED_ENCODER.classes_}
        fallback_scores["OTHER_FEE_QUERY"] = 1.0
        result = {
            "intent": "OTHER_FEE_QUERY",
            "confidence": 0.0,
            "preprocessed_text": "",
        }
        if return_all_scores:
            result["all_scores"] = fallback_scores
        return result

    # 2. Text Preprocessing
    clean_text = preprocess(text)

    # If preprocessing stripped everything (e.g. string was solely punctuation or non-retained stopwords)
    if not clean_text.strip():
        fallback_scores = {cls_name: 0.1 for cls_name in _CACHED_ENCODER.classes_}
        result = {
            "intent": "OTHER_FEE_QUERY",
            "confidence": 0.10,
            "preprocessed_text": clean_text,
        }
        if return_all_scores:
            result["all_scores"] = fallback_scores
        return result

    # 3. TF-IDF Feature Extraction
    features = _CACHED_VECTORIZER.transform([text])

    # 4. Probabilistic Prediction
    if hasattr(_CACHED_MODEL, "predict_proba"):
        probabilities = _CACHED_MODEL.predict_proba(features)[0]
    elif hasattr(_CACHED_MODEL, "decision_function"):
        # Softmax on decision function for non-probabilistic models
        dec = _CACHED_MODEL.decision_function(features)[0]
        exp_dec = np.exp(dec - np.max(dec))
        probabilities = exp_dec / exp_dec.sum()
    else:
        # Fallback to hard prediction
        pred_idx = _CACHED_MODEL.predict(features)[0]
        probabilities = np.zeros(len(_CACHED_ENCODER.classes_))
        probabilities[pred_idx] = 1.0

    best_idx = int(np.argmax(probabilities))
    confidence = float(probabilities[best_idx])
    predicted_intent = str(_CACHED_ENCODER.classes_[best_idx])

    result = {
        "intent": predicted_intent,
        "confidence": round(confidence, 4),
        "preprocessed_text": clean_text,
    }

    if return_all_scores:
        scores_dict = {
            str(_CACHED_ENCODER.classes_[i]): round(float(probabilities[i]), 4)
            for i in range(len(_CACHED_ENCODER.classes_))
        }
        # Sort descending by score
        result["all_scores"] = dict(sorted(scores_dict.items(), key=lambda item: item[1], reverse=True))

    return result


if __name__ == "__main__":
    # Test query demonstrations
    test_queries = [
        "How much fee is remaining for semester 4?",
        "मेरी फीस कितनी बाकी है?",
        "माझी किती फी बाकी आहे?",
        "Can I pay in installments?",
        "When is the last date to pay term fees?",
        "I need my payment receipt",
        "How to apply for EBC scholarship?",
    ]

    print("=" * 70)
    print("FeeAssist AI — Sample Query Predictions")
    print("=" * 70)
    for q in test_queries:
        res = predict_intent(q)
        print(f"\nQuery:      '{q}'")
        print(f"Intent:     {res['intent']} (Confidence: {res['confidence'] * 100:.1f}%)")
        print(f"Top 3:      {list(res['all_scores'].items())[:3]}")
