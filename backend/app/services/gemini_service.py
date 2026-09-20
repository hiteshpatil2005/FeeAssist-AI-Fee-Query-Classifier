"""
FeeAssist AI — Gemini Service (Placeholder)

This module will integrate Google Gemini API as a secondary fallback
for complex or low-confidence queries that the NLP classifier cannot
handle with sufficient confidence.

Usage pattern:
- NLP classifier runs first on every query.
- If confidence < threshold, this service sends the query to Gemini.
- Gemini response is returned to the user with a disclaimer.
"""


def query_gemini(user_message: str, context: list = None) -> str:
    """
    Send a query to Google Gemini API.

    TODO: Implement using google-generativeai SDK.
    Requires GEMINI_API_KEY environment variable.

    Args:
        user_message: The user's natural language question.
        context: Optional list of prior conversation turns.

    Returns:
        str: Gemini-generated response text.
    """
    raise NotImplementedError("Gemini service not yet implemented")
