"""
FeeAssist AI — Voice Service (Placeholder)

This module will implement voice input/output capabilities.

Planned features:
- Speech-to-text (STT) using Web Speech API or Google Cloud STT
- Text-to-speech (TTS) for assistant responses
- Multilingual voice support (English, Hindi, Marathi)
"""


def transcribe_audio(audio_data: bytes, language: str = "en") -> str:
    """
    Convert audio bytes to text.
    TODO: Implement using Google Cloud Speech-to-Text or Web Speech API.
    """
    raise NotImplementedError("Voice service not yet implemented")


def synthesize_speech(text: str, language: str = "en") -> bytes:
    """
    Convert text to audio bytes.
    TODO: Implement using Google Cloud Text-to-Speech.
    """
    raise NotImplementedError("Voice service not yet implemented")
