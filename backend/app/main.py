"""
FeeAssist AI — FastAPI Application Entry Point
Phase 2: Real PostgreSQL authentication + fee/payment APIs.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, chat, nlp
from app.api import fees, payments

app = FastAPI(
    title="FeeAssist AI API",
    description="Multilingual and Voice-Enabled Personal Fees Query Assistant",
    version="0.3.0",
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────────────────────
app.include_router(auth.router,     prefix="/api/auth",     tags=["Authentication"])
app.include_router(fees.router,     prefix="/api/fees",     tags=["Fees"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])
app.include_router(chat.router,     prefix="/api/chat",     tags=["Chat"])
app.include_router(nlp.router,      prefix="/api/nlp",      tags=["NLP"])


# ── Root & Health ─────────────────────────────────────────────────────────────
@app.get("/", tags=["Root"])
async def root():
    return {"message": "FeeAssist AI API is running"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}
