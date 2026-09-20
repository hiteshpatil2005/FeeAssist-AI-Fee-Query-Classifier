"""
FeeAssist AI — NLP Service

Integrates the trained ML intent classification model into the FastAPI backend.
Discovers the model artifacts directory whether running inside Docker or on the host machine,
caches artifacts globally for high-throughput inference, and returns structured predictions.
"""

import os
import sys
from typing import Dict, Any, Optional

# Locate project ML module and models directory
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Possible search locations for ml package and models
_CANDIDATE_ROOTS = [
    os.path.abspath(os.path.join(_CURRENT_DIR, "..", "..", "..")),  # d:\Github Desktop\FeeAssist-AI
    "/app",                                                          # Docker container root
    os.getcwd(),                                                     # Current working directory
    os.path.abspath(os.path.join(os.getcwd(), "..")),                # Parent directory
]

ML_DIR = None
MODELS_DIR = None

for root in _CANDIDATE_ROOTS:
    cand_ml = os.path.join(root, "ml")
    cand_models = os.path.join(cand_ml, "models")
    if os.path.isdir(cand_models) and os.path.exists(os.path.join(cand_models, "best_model.joblib")):
        ML_DIR = cand_ml
        MODELS_DIR = cand_models
        if root not in sys.path:
            sys.path.insert(0, root)
        break

if ML_DIR is None:
    # Fallback default
    MODELS_DIR = os.path.join(_CANDIDATE_ROOTS[0], "ml", "models")
    if _CANDIDATE_ROOTS[0] not in sys.path:
        sys.path.insert(0, _CANDIDATE_ROOTS[0])

# Import prediction function from ml.predict
try:
    from ml.predict import predict_intent
except ImportError:
    # If ml is inside current dir or directly accessible
    sys.path.insert(0, os.path.abspath(os.path.join(_CURRENT_DIR, "..", "..")))
    from ml.predict import predict_intent


def classify_intent(text: str) -> Dict[str, Any]:
    """
    Classify the fee-related intent of a student message using the trained ML model.

    Args:
        text: Raw natural language query in English, Hindi, or Marathi.

    Returns:
        dict with keys:
        - "intent": Recognized fee intent (e.g. "PENDING_FEE")
        - "confidence": Calibrated prediction confidence float (e.g. 0.85)
        - "all_scores": Confidence distribution across candidate intents
    """
    result = predict_intent(text=text, models_dir=MODELS_DIR, return_all_scores=True)
    return {
        "intent": result["intent"],
        "confidence": result["confidence"],
        "all_scores": result.get("all_scores", {}),
    }
