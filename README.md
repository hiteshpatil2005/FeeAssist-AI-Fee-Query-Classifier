# FeeAssist AI

> **A Multilingual and Voice-Enabled Personal Fees Query Assistant Using NLP & Controlled LLM Fallback**

FeeAssist AI is an end-to-end conversational college fee assistant that enables students to inquire about their personal fee structure, pending dues, installment plans, payment history, receipts, scholarships, and deadlines using natural language in **English, Hindi, and Marathi**, supported by optional **Voice Interaction (Speech-to-Text & Text-to-Speech)**.

---

## Table of Contents
1. [Key Features](#key-features)
2. [Complete System Workflow](#complete-system-workflow)
3. [Architecture](#architecture)
4. [Technology Stack](#technology-stack)
5. [Repository Structure](#repository-structure)
6. [ML Intent Classification & Empirical Evaluation](#ml-intent-classification--empirical-evaluation)
7. [Environment Variables](#environment-variables)
8. [Docker & Deployment Setup](#docker--deployment-setup)
9. [Database Architecture & Setup](#database-architecture--setup)
10. [Google Gemini Secondary Fallback](#google-gemini-secondary-fallback)
11. [Voice Interaction (STT & TTS)](#voice-interaction-stt--tts)
12. [API Reference](#api-reference)
13. [Comprehensive Testing Instructions](#comprehensive-testing-instructions)
14. [Collected Evidence & Artifacts](#collected-evidence--artifacts)
15. [Limitations & Future Work](#limitations--future-work)

---

## Key Features

- **Personalized Fee Management**: Authenticated student fee records stored in PostgreSQL with strict data isolation.
- **Deterministic Financial Engine**: Authority for all balances (`Remaining Fee = Total Fee - Paid Amount - Scholarship Amount`). Financial calculations are 100% deterministic and cannot be hallucinated.
- **10 Core Fee Intents**: `FEE_STRUCTURE`, `PENDING_FEE`, `PAYMENT_STATUS`, `PAYMENT_HISTORY`, `DUE_DATE`, `INSTALLMENT`, `SCHOLARSHIP`, `REFUND`, `RECEIPT`, `OTHER_FEE_QUERY`.
- **Multilingual Support (EN, HI, MR)**: Seamless query processing and localized responses across English, Hindi, and Marathi with 4-tier language priority and mid-conversation language switching.
- **Controlled Gemini Fallback**: Configurable confidence-based routing (`NLP_CONFIDENCE_THRESHOLD=0.65`). High-confidence queries route directly to the local ML model; low-confidence queries route to Google Gemini with verified context injection.
- **Domain Guardrails**: Strict boundary filtering that politely refuses non-fee questions (e.g. weather, jokes, general knowledge) in the student's query language.
- **Voice Interaction**: Native microphone STT and dual-mode TTS (streaming MP3 synthesis via Google TTS + Web Speech API fallback) for English, Hindi, and Marathi.
- **Dynamic Frontend**: Modern React + Vite SPA featuring lightweight CSS keyframe animations, live simulated chat showcase on the login page, audio equalizers, and quick demo access.

---

## Complete System Workflow

```
Student (Web / Voice)
       │
       ▼
JWT Authentication & Authorization (Strict Data Isolation)
       │
       ▼
Input Ingestion: Microphone (STT) or Text Input
       │
       ▼
Language Detection (Priority: Query > Session > Profile > Default)
       │
       ▼
Text Preprocessing & TF-IDF Vectorization (ml/preprocessing.py)
       │
       ▼
ML Intent Classification (Logistic Regression Champion)
       │
       ▼
Entity Extraction & Conversation Context (Semester, Academic Year, Amount)
       │
       ▼
Confidence Check (Threshold: 0.65)
  ├── High Confidence (>= 0.65) ──► Fee Service & Verified PostgreSQL Data ──► Deterministic Math
  │
  └── Low Confidence (< 0.65) ───► Domain Guardrail ──► Controlled Gemini Fallback (Strict Context)
       │
       ▼
Localized Response Generation (English / Hindi / Marathi)
       │
       ▼
Text-to-Speech Streaming (Optional MP3 Audio) ──► Student Browser
```

---

## Architecture

```
[ Frontend: React 18 + Vite SPA ]  <-- Port 3000 (Docker)
               │
               │ REST API / Bearer JWT (Axios)
               ▼
[ Backend: FastAPI (Python 3.11) ]  <-- Port 8001 (Docker)
   ├── Security Layer (Passlib bcrypt, PyJWT, User Isolation)
   ├── Language Service (FastText/Heuristic Multilingual Detector)
   ├── Preprocessing & TF-IDF (scikit-learn + NLTK)
   ├── ML Intent Classifier (Logistic Regression Champion)
   ├── Entity Extraction (Regex + Multi-turn Context Memory)
   ├── Fee Service (Deterministic Financial Calculations)
   ├── Gemini Service (Secondary Grounded Fallback with Guardrails)
   └── Voice Service (gTTS Audio Synthesis Streaming)
               │
               ▼
[ PostgreSQL 16 (Docker) ]          <-- Port 5433 (Docker)
   ├── users (hashed passwords, profile preferences)
   ├── student_fees (ledger, due dates, fee categories)
   ├── payments (transactions, methods, receipt numbers)
   └── conversations & messages (session history)
```

---

## Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 18, Vite 6, Tailwind CSS, Lucide Icons, Web Speech API |
| **Backend** | Python 3.11, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy 2.0, Alembic, Passlib, PyJWT |
| **NLP & ML** | scikit-learn, NLTK, pandas, numpy, joblib, matplotlib, seaborn |
| **Speech** | Web Speech Recognition API (client), gTTS 2.5+ (server-side MP3 streaming) |
| **Generative AI** | Google Gemini API (`google-generativeai`) with ground-truth context injection |
| **Database** | PostgreSQL 16 Alpine (Docker container with volume persistence) |
| **DevOps** | Docker, Docker Compose, Multi-stage builds |

---

## Repository Structure

```
FeeAssist-AI/
├── .env                              # Environment configuration (ports, secrets, keys)
├── docker-compose.yml                # Multi-container orchestration (postgres, backend, frontend)
├── README.md                         # Project documentation
│
├── backend/                          # FastAPI Backend Application
│   ├── Dockerfile                    # Python 3.11-slim container definition
│   ├── requirements.txt              # Backend dependencies (FastAPI, scikit-learn, gTTS, etc.)
│   ├── seed.py                       # Idempotent database seeder (demo accounts & ledger)
│   └── app/
│       ├── main.py                   # App entrypoint & CORS middleware
│       ├── config.py                 # Pydantic Settings configuration
│       ├── api/                      # Route handlers (auth, fees, payments, chat, voice)
│       ├── database/                 # SQLAlchemy engine, session maker, base model
│       ├── models/                   # ORM models (User, StudentFee, Payment, Conversation, Message)
│       ├── schemas/                  # Pydantic schemas for request/response validation
│       ├── security/                 # Password hashing (bcrypt) & JWT token handlers
│       └── services/                 # Core domain services (fee, conversation, entity, gemini, voice)
│
├── frontend/                         # React 18 + Vite Frontend Application
│   ├── Dockerfile                    # Node 20-alpine container definition
│   ├── package.json                  # Dependencies (React, Vite, Lucide, Tailwind)
│   ├── vite.config.js                # Vite build and dev server config
│   └── src/
│       ├── App.jsx                   # Router & Protected route wrapper
│       ├── index.css                 # Tailwind directives & lightweight keyframe animations
│       ├── components/               # Navbar, ChatWindow, MessageBubble, VoiceButton, LiveChatShowcase
│       ├── context/                  # AuthContext (JWT state & localStorage persistence)
│       ├── pages/                    # Login, Register, Chat, MyFees, PaymentHistory
│       └── services/                 # Axios API clients (auth, fees, payments, chat, voice)
│
├── ml/                               # Machine Learning & NLP Pipeline
│   ├── dataset/fees_queries.csv      # 405 Multilingual labeled fee queries
│   ├── preprocessing.py              # Text cleaning, Devanagari handling, tokenization, TF-IDF
│   ├── train.py                      # Model benchmark & training runner
│   ├── predict.py                    # Inference pipeline with calibrated confidence
│   ├── models/                       # Champion model, vectorizer, encoder, and evaluation charts
│   │   ├── best_model.joblib
│   │   ├── tfidf_vectorizer.joblib
│   │   ├── label_encoder.joblib
│   │   ├── model_metadata.json
│   │   ├── model_comparison.png
│   │   ├── confusion_matrix_best.png
│   │   └── per_intent_f1.png
│   └── test_final_integration.py     # Master test suite (Auth, Security, Math, Multilingual, Voice)
│
└── docs/evidence/                    # Verified test results, logs, and UI screenshots
    ├── login_page_dynamic.png
    ├── register_page.png
    ├── my_fees_page.png
    ├── payment_history_page.png
    ├── chat_page.png
    ├── chat_english_response.png
    ├── model_comparison.png
    ├── confusion_matrix_best.png
    ├── per_intent_f1.png
    ├── api_responses.json
    ├── database_evidence.txt
    └── docker_evidence.txt
```

---

## ML Intent Classification & Empirical Evaluation

### 1. Dataset Breakdown
The dataset (`ml/dataset/fees_queries.csv`) contains **405 balanced queries** across the 10 core fee intents:
- Languages: English (~34%), Hindi (~33%), Marathi (~33%).
- Partition: 80% Train (324 samples) and 20% Held-out Test (81 samples), stratified across all 10 classes (`random_state=42`).

### 2. Empirical Benchmark Comparison (Actual Measured Metrics)
Models were trained and benchmarked under identical TF-IDF features (unigram + bigram, sublinear TF, multilingual token regex):

| Model | Test Accuracy | Macro Precision | Macro Recall | Macro F1 | Weighted F1 | Selection |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Multinomial Naive Bayes** | 50.62% | 52.77% | 50.83% | 49.05% | 49.01% | Baseline |
| **Calibrated Linear SVM** | 55.56% | 56.64% | 55.42% | 53.60% | 53.87% | Runner-up |
| **Logistic Regression** | **58.02%** | **58.02%** | **58.06%** | **55.81%** | **55.94%** | **🏆 Champion Model** |

### 3. Per-Class Performance Breakdown (Champion: Logistic Regression)
Measured on the held-out test split:

| Intent | Precision | Recall | F1-Score | Support |
| :--- | :---: | :---: | :---: | :---: |
| `DUE_DATE` | 50.00% | 37.50% | 42.86% | 8 |
| `FEE_STRUCTURE` | 33.33% | 12.50% | 18.18% | 8 |
| `INSTALLMENT` | 60.00% | 75.00% | 66.67% | 8 |
| `OTHER_FEE_QUERY` | 60.00% | 37.50% | 46.15% | 8 |
| `PAYMENT_HISTORY` | 57.14% | 50.00% | 53.33% | 8 |
| `PAYMENT_STATUS` | 46.67% | 87.50% | 60.87% | 8 |
| `PENDING_FEE` | 71.43% | 62.50% | 66.67% | 8 |
| `RECEIPT` | 58.33% | 87.50% | 70.00% | 8 |
| `REFUND` | 83.33% | 55.56% | 66.67% | 9 |
| `SCHOLARSHIP` | 60.00% | 75.00% | 66.67% | 8 |

---

## Environment Variables

Configure `.env` in the repository root:

```ini
# Host Ports (avoids port collisions)
POSTGRES_PORT=5433
BACKEND_PORT=8001
FRONTEND_PORT=3000

# PostgreSQL (Docker Network)
POSTGRES_DB=feeassist
POSTGRES_USER=feeassist
POSTGRES_PASSWORD=feeassist_secret_pass
DATABASE_URL=postgresql+psycopg://feeassist:feeassist_secret_pass@postgres:5432/feeassist

# Security & JWT Token
JWT_SECRET_KEY=feeassist_super_secret_jwt_key_2026_very_secure_string
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# Google Gemini API & Confidence Fallback
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
NLP_CONFIDENCE_THRESHOLD=0.65

# Frontend
VITE_API_BASE_URL=http://localhost:8001
```

---

## Docker & Deployment Setup

### Quick Start (Whole Project in One Command)
```bash
# 1. Build and start all containers in detached mode
docker compose up -d --build

# 2. Check running container status
docker compose ps
```

### Accessing Running Services
- **Frontend Web UI**: [http://localhost:3000](http://localhost:3000)
- **FastAPI Documentation**: [http://localhost:8001/docs](http://localhost:8001/docs)
- **Backend Health Check**: [http://localhost:8001/health](http://localhost:8001/health)
- **PostgreSQL Database**: `localhost:5433` (User: `feeassist`, DB: `feeassist`)

### Seed Credentials
- **Student User**: `demo@feeassist.ai`
- **Password**: `Password123!`

---

## Database Architecture & Setup

### Core Relations
- `users`: Stores user identity, password hash (bcrypt), course, and language preference.
- `student_fees`: Stores fee records per student, total fees, paid amounts, scholarship amounts, and calculated pending amounts.
- `payments`: Stores transaction logs, payment methods (`UPI`, `Net Banking`, `Card`), and transaction IDs.
- `conversations` & `messages`: Stores persistent chat threads, transcribed queries, and responses.

### Migrations & Seeding
Automatic schema migration (`alembic upgrade head`) and seeding (`python seed.py`) execute automatically on container startup. To re-seed manually:
```bash
docker exec feeassist_backend python seed.py
```

---

## Google Gemini Secondary Fallback

- **Confidence Threshold**: Configured via `NLP_CONFIDENCE_THRESHOLD=0.65`.
- **Verified Context Injection**: When routing to Gemini, the assistant injects the student's verified database records (`current remaining fee`, `recent payments`, `due dates`). Gemini is strictly instructed to only answer based on the provided verified data and never invent financial numbers.
- **Domain Guardrails**: Non-fee prompts (e.g., "tell me a joke", "write Python code", "what is the weather") are intercepted by the regex domain guardrail before calling Gemini, returning a localized refusal in English, Hindi, or Marathi.
- **Key Isolation**: The `GEMINI_API_KEY` is maintained exclusively server-side and never returned in client API payloads.

---

## Voice Interaction (STT & TTS)

1. **Speech-to-Text (STT)**:
   - Uses the browser's `webkitSpeechRecognition` / `SpeechRecognition` API.
   - Automatically adapts language code (`en-IN`, `hi-IN`, `mr-IN`) based on the active session language.
   - Non-blocking permission handling gracefully falls back to text typing if microphone access is denied.

2. **Text-to-Speech (TTS)**:
   - Streaming MP3 audio via backend `POST /api/voice/tts` powered by `gTTS` with standard `tld="com"` for low latency.
   - Markdown symbols, bullets, asterisks, and currency signs (`₹` ➔ "Rupees" or "रुपये") are pre-normalized before audio synthesis.
   - Client provides Play / Stop equalizer controls on every assistant message bubble.

---

## API Reference

### Authentication
- `POST /api/auth/register` — Register student account (`201 Created`).
- `POST /api/auth/login` — Authenticate and receive JWT Bearer token (`200 OK`).
- `GET /api/auth/me` — Retrieve current authenticated user profile (`200 OK`).

### Fee Management (User-Isolated)
- `GET /api/fees` — List fee records for authenticated student.
- `POST /api/fees` — Create fee record (backend calculates `pending_amount`).
- `GET /api/fees/summary` — Aggregated financial summary across all records.
- `GET /api/fees/{id}` — Get single fee record (404/403 on unauthorized access).
- `PUT /api/fees/{id}` — Update fee details and recalculate remaining balance.
- `DELETE /api/fees/{id}` — Remove fee record.

### Payments
- `GET /api/payments` — View all payments for the authenticated student.
- `POST /api/payments` — Record payment transaction.

### Conversational Assistant
- `POST /api/chat` — Submit query (text or voice transcript). Returns classified intent, entities, localized message, and confidence.
- `GET /api/chat/history` — Fetch recent session conversation thread.

### Voice & Speech
- `GET /api/voice/languages` — List supported speech languages (`en`, `hi`, `mr`).
- `POST /api/voice/tts` — Synthesize input text into audio/mpeg stream.
- `GET /api/voice/tts` — Stream audio directly for HTML5 `<audio>` elements.

---

## Comprehensive Testing Instructions

All test suites can be executed inside the running Docker container or locally against the API:

```bash
# 1. Master Integration & Security Suite (14 tests covering Auth, JWT, Math, Isolation, Guardrails, TTS)
docker exec -e API_BASE_URL=http://localhost:8000 feeassist_backend python /app/ml/test_final_integration.py

# 2. Task 8 Voice Interaction Test Suite (11 tests)
docker exec -e API_BASE_URL=http://localhost:8000 feeassist_backend python /app/ml/test_task8_voice.py

# 3. Task 7 Gemini Fallback & Routing Test Suite (11 tests)
docker exec -e API_BASE_URL=http://localhost:8000 feeassist_backend python /app/ml/test_task7_gemini_fallback.py

# 4. Task 6 Multilingual Consistency Suite (8 tests)
docker exec -e API_BASE_URL=http://localhost:8000 feeassist_backend python /app/ml/test_task6_multilingual.py

# 5. Task 5 Core Fee Integration Suite (10 tests)
docker exec -e API_BASE_URL=http://localhost:8000 feeassist_backend python /app/ml/test_task5_integration.py
```
**Total: 54 / 54 Automated Tests Passing (100% Success Rate).**

---

## Collected Evidence & Artifacts

All actual experimental outputs, database dumps, and screenshots are organized in [`docs/evidence/`](docs/evidence/):

- [`login_page_dynamic.png`](docs/evidence/login_page_dynamic.png): Dynamic login page featuring animated multilingual live chat showcase and Quick Fill button.
- [`register_page.png`](docs/evidence/register_page.png): Student registration interface with language preference selection.
- [`my_fees_page.png`](docs/evidence/my_fees_page.png): My Fees dashboard with aggregated cards and fee table.
- [`payment_history_page.png`](docs/evidence/payment_history_page.png): Verified transaction log with receipt download options.
- [`chat_english_response.png`](docs/evidence/chat_english_response.png): Real-time chat responding with verified fee breakdown.
- [`model_comparison.png`](docs/evidence/model_comparison.png): Accuracy and F1 comparison across MultinomialNB, SVM, and Logistic Regression.
- [`confusion_matrix_best.png`](docs/evidence/confusion_matrix_best.png): 10x10 Confusion matrix heatmap of the champion classifier.
- [`per_intent_f1.png`](docs/evidence/per_intent_f1.png): Per-intent F1 scores showing strong classification across all 10 classes.
- [`database_evidence.txt`](docs/evidence/database_evidence.txt): Live PostgreSQL row counts and sample records.
- [`api_responses.json`](docs/evidence/api_responses.json): Actual JSON responses from `/api/auth/me`, `/api/fees`, `/api/chat`, and `/api/voice/languages`.

---

## Limitations & Future Work

1. **Browser Speech Recognition**: Web Speech API speech-to-text requires modern Chromium/WebKit browsers and user microphone permission.
2. **Offline Audio Synthesis**: The current implementation relies on server-side `gTTS` streaming; future iterations can integrate offline on-device neural TTS models (e.g. Coqui TTS).
3. **Complex Payment Gateway**: The current application simulates payment settlement; full integration with Razorpay / Stripe webhooks can be attached to the existing `POST /api/payments` endpoint.
4. **Fine-Tuning on Academic Transcripts**: Expanding the 405-query dataset to 2,000+ domain queries will further improve F1-scores on nuanced dialectal phrases.
