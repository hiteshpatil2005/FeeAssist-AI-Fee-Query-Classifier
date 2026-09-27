"""
FeeAssist AI — Voice API Router

Endpoints for:
1. Fetching supported voice languages and BCP-47 codes
2. Synthesizing Text-to-Speech into streaming MP3 audio
"""

import logging
from fastapi import APIRouter, HTTPException, Response, Query, status
from fastapi.responses import Response

from app.schemas.voice import TTSRequest, SupportedLanguagesResponse
from app.services.voice_service import VoiceService

logger = logging.getLogger("feeassist.voice.api")

router = APIRouter()


@router.get(
    "/languages",
    response_model=SupportedLanguagesResponse,
    summary="Get supported voice languages for STT and TTS",
)
def get_languages():
    """Returns languages explicitly verified and supported for voice (English, Hindi, Marathi)."""
    return SupportedLanguagesResponse(
        supported_languages=VoiceService.get_supported_languages()
    )


@router.post(
    "/tts",
    summary="Synthesize text into speech (MP3 stream)",
    responses={
        200: {
            "content": {"audio/mpeg": {}},
            "description": "MP3 audio stream",
        }
    },
)
def text_to_speech_post(payload: TTSRequest):
    """
    Synthesizes provided text into MP3 audio in the target language (en, hi, mr).
    Strips markdown and normalizes currency before synthesis.
    """
    try:
        audio_bytes = VoiceService.synthesize_speech(
            text=payload.text, lang=payload.language or "en"
        )
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=speech.mp3",
                "Cache-Control": "public, max-age=86400",
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"TTS synthesis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Speech synthesis service temporarily unavailable",
        )


@router.get(
    "/tts",
    summary="Synthesize text into speech via GET (for direct audio elements)",
    responses={
        200: {
            "content": {"audio/mpeg": {}},
            "description": "MP3 audio stream",
        }
    },
)
def text_to_speech_get(
    text: str = Query(..., min_length=1, max_length=5000, description="Text to speak"),
    language: str = Query("en", description="Target language ('en', 'hi', 'mr')"),
):
    """GET endpoint allowing direct usage in HTML5 <audio> sources."""
    try:
        audio_bytes = VoiceService.synthesize_speech(text=text, lang=language)
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=speech.mp3",
                "Cache-Control": "public, max-age=86400",
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"TTS synthesis GET error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Speech synthesis service temporarily unavailable",
        )
