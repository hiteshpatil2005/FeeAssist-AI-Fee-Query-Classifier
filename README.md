# FeeAssist AI

> **A Multilingual and Voice-Enabled Personal Fees Query Assistant Using NLP**

FeeAssist AI is a chat-based college fee assistant that allows students to ask natural language questions about their fee structure, pending fees, payment history, due dates, installments, scholarships, and more — in English, Hindi, or Marathi.

---

## Current Status

- **Phase 1 — Foundation & UI**: Completed ✅ (React + Vite + Tailwind CSS + FastAPI foundation)
- **Phase 2 — PostgreSQL Database & JWT Auth**: Completed ✅ (Dockerized PostgreSQL, SQLAlchemy models, Alembic migrations, JWT auth, Seed data)
- **Phase 3 — NLP Dataset, Preprocessing & Feature Extraction**: Completed ✅ (405 Multilingual Queries, Text Normalization, Domain Negation Preservation, POS Lemmatization, BoW, TF-IDF, Jupyter Notebook)
- **Phase 4 — ML Intent Classification Layer**: Completed ✅ (MultinomialNB, Logistic Regression, Calibrated LinearSVC, Model Selection, FastAPI `POST /api/nlp/classify` endpoint)
- **Phase 5 — Fee Service & Conversational Chat Integration**: Planned ⏳ (Contextual chat, Fee balance calculations from PostgreSQL, Gemini fallback)

---

## Architecture

```
Browser (React SPA - Port 5173)
        │
        │  HTTP/REST (Axios + Bearer JWT)
        ▼
FastAPI Backend (Docker - Port 8001:8000)
        │
        ├── NLP Classification Layer (POST /api/nlp/classify)
        │     ├── Text Preprocessor (ml/preprocessing.py)
        │     ├── Fitted TF-IDF Vectorizer (ml/models/tfidf_vectorizer.joblib)
        │     └── Champion Classifier: Logistic Regression (ml/models/best_model.joblib)
        │
        ├── PostgreSQL Database (Docker - Port 5433:5432)
        │     ├── Users (Students & Admins)
        │     ├── Fee Structures & Categories
        │     ├── Student Fees & Installments
        │     ├── Payment Records & Receipts
        │     └── Conversation Threads & Messages
        │
        └── Google Gemini API (Secondary Fallback for Low-Confidence Queries)
```

---

## Technology Stack

| Layer          | Technology                                                     |
|----------------|----------------------------------------------------------------|
| **Frontend**   | React 18, Vite, Tailwind CSS, React Router, Axios, Lucide Icons|
| **Backend**    | Python 3.11+, FastAPI, Uvicorn, Pydantic v2, Passlib, PyJWT   |
| **Database**   | PostgreSQL 16 (Docker container), SQLAlchemy 2.0, Alembic     |
| **NLP / ML**   | scikit-learn, NLTK, pandas, numpy, matplotlib, seaborn, joblib |
| **Notebooks**  | Jupyter, nbformat, nbconvert                                   |
| **AI Fallback**| Google Gemini API (`google-generativeai`)                      |
| **DevOps**     | Docker, Docker Compose                                         |

---

## ML Intent Classification & Model Selection

### 1. The 10 Fee-Specific Intents
1. `FEE_STRUCTURE`: Tuition fees, term fees, hostel & mess charges breakdown.
2. `PENDING_FEE`: Outstanding balance, remaining dues, pending payments.
3. `PAYMENT_STATUS`: Transaction confirmation, clearance verification.
4. `PAYMENT_HISTORY`: Past transaction logs, dates, payment methods.
5. `DUE_DATE`: Deadlines for fee submission and late fee penalties.
6. `INSTALLMENT`: Splitting fees into EMIs or semester installments.
7. `SCHOLARSHIP`: Government/merit concessions (EBC, TFWS, SC/ST, freeship).
8. `REFUND`: Excess fee clearance, admission cancellation refunds.
9. `RECEIPT`: Fee receipt downloads, acknowledgment slips, transaction IDs.
10. `OTHER_FEE_QUERY`: Counter timings, contact details, payment modes.

### 2. Empirical Benchmark Comparison
All three models were trained on 324 samples and evaluated on 81 held-out test samples (stratified 80/20 split, `random_state=42`):

| Model | Test Accuracy | Macro Precision | Macro Recall | Macro F1 | Weighted F1 | Selection |
|---|---|---|---|---|---|---|
| **Multinomial Naive Bayes** | 50.62% | 52.77% | 50.83% | 49.05% | 49.01% | Baseline |
| **Calibrated Linear SVM** | 55.56% | 56.64% | 55.42% | 53.60% | 53.87% | Runner-up |
| **Logistic Regression** | **58.02%** | **58.02%** | **58.06%** | **55.81%** | **55.94%** | **🏆 Champion Model** |

**Selection Rationale**: Logistic Regression achieved superior Macro F1 (55.81%) and Accuracy (58.02%) across all 10 fee intents while providing well-calibrated class probability distributions for confidence scoring.

### 3. Generated Evaluation Artifacts (`ml/models/`)
- `best_model.joblib`: Trained Logistic Regression champion model.
- `tfidf_vectorizer.joblib`: Fitted TF-IDF vectorizer (unigrams + bigrams, multilingual token pattern).
- `label_encoder.joblib`: Fitted label encoder for the 10 intent classes.
- `model_metadata.json`: Full benchmark evaluation results and per-class metrics.
- `model_comparison.png`: Comparison bar chart across the 3 models.
- `confusion_matrix_best.png`: Confusion matrix heatmap for the champion model.
- `per_intent_f1.png`: Per-intent F1 performance breakdown.

### 4. Running Training & Tests
```bash
# Train models, benchmark, and save artifacts
py ml/train.py

# Run standalone NLP prediction test suite (35 diverse test cases)
py ml/test_intent_classifier.py

# Test live FastAPI backend endpoint
py ml/test_api_endpoint.py
```

---

## FastAPI NLP Classification API

### Endpoint: `POST /api/nlp/classify`
Receives a student fee query in English, Hindi, or Marathi, runs it through the preprocessing and TF-IDF pipeline, and returns the recognized intent with a calibrated confidence score.

#### Example Request:
```bash
curl -X POST http://localhost:8001/api/nlp/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "How much fee do I have left?"}'
```

#### Example Response:
```json
{
  "intent": "PENDING_FEE",
  "confidence": 0.2504
}
```

#### Multilingual Examples:
- **Hindi**: `{"text": "मेरी फीस कितनी बाकी है?"}` ➔ `{"intent": "PENDING_FEE", "confidence": 0.5769}`
- **Marathi**: `{"text": "माझी किती फी बाकी आहे?"}` ➔ `{"intent": "PENDING_FEE", "confidence": 0.6463}`
- **Installment**: `{"text": "Can I pay in installments?"}` ➔ `{"intent": "INSTALLMENT", "confidence": 0.7484}`
- **Receipt**: `{"text": "Where can I download my fee receipt?"}` ➔ `{"intent": "RECEIPT", "confidence": 0.8347}`
- **Due Date**: `{"text": "When is the last date to pay fees?"}` ➔ `{"intent": "DUE_DATE", "confidence": 0.5269}`

---

## Getting Started

### Quick Start with Docker (Recommended)
All services (Frontend, Backend, PostgreSQL) run containerized:

```bash
# 1. Start all services
docker compose up -d

# 2. Verify running containers
docker compose ps
```

- **Frontend SPA**: http://localhost:5173
- **FastAPI Documentation**: http://localhost:8001/docs
- **Backend Health Check**: http://localhost:8001/health
- **PostgreSQL**: `localhost:5433` (mapped from container `5432`)

### Default Seed Credentials (Preloaded in Database)
- **Student Account**:
  - Email: `student@feeassist.edu`
  - Password: `Password@123`
- **Admin Account**:
  - Email: `admin@feeassist.edu`
  - Password: `Password@123`

---

## Roadmap

| Module                        | Description                                                   | Status      |
|-------------------------------|---------------------------------------------------------------|-------------|
| **UI & Layout**               | React + Tailwind CSS + Lucide Icons + Responsive Chat UI      | Complete ✅ |
| **PostgreSQL & Auth**         | Dockerized Postgres, SQLAlchemy 2.0, Alembic, JWT Auth        | Complete ✅ |
| **NLP Foundation**            | Multilingual Dataset (405 queries), Preprocessing, BoW, TFIDF | Complete ✅ |
| **ML Intent Classifier**      | MultinomialNB, SVM, Logistic Regression, FastAPI Endpoint     | Complete ✅ |
| **Fee Service & Chat Logic**  | Contextual student fee calculations, response generator      | Planned ⏳  |
| **Confidence & Fallback**     | Dynamic confidence scoring, Google Gemini API fallback        | Planned ⏳  |
| **Voice Assistant**           | Multilingual Speech-to-Text & Text-to-Speech (Web Speech API) | Planned ⏳  |

---

## License
This project is developed for academic purposes.
