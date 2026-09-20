"""
FeeAssist AI — NLP Preprocessing and Feature Extraction Pipeline

This module implements modular, reusable text preprocessing and feature extraction
for college fee queries across English, Hindi, and Marathi.

Pipeline Stages:
    Raw Text
       ↓
    Lowercase (Latin script normalization)
       ↓
    Unicode & Punctuation Cleaning (safe for Devanagari \u0900-\u097F & currency ₹)
       ↓
    Whitespace Normalization
       ↓
    Tokenization
       ↓
    Stopword Removal (domain-aware: preserves critical negations like 'not', 'no', 'cannot')
       ↓
    Lemmatization (NLTK WordNetLemmatizer with POS-mapping for English; pass-through for Devanagari)
       ↓
    Clean Preprocessed Text / Tokens
       ↓
    Feature Extraction:
      ├── Bag of Words (CountVectorizer)
      └── TF-IDF Representation (TfidfVectorizer)

Multilingual Considerations:
    - English: Full normalization, tokenization, stopword filtering, and morphological lemmatization.
    - Hindi / Marathi: Devanagari characters, matras, and conjuncts are preserved.
      English-trained lemmatizers gracefully pass non-ASCII / Devanagari tokens through unmodified
      to prevent character corruption.
"""

import os
import re
import unicodedata
from typing import List, Tuple, Union

import joblib
import nltk
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

# ── Ensure Required NLTK Corpora Are Available ────────────────────────────────
_NLTK_RESOURCES = [
    ("corpora/stopwords", "stopwords"),
    ("corpora/wordnet", "wordnet"),
    ("corpora/omw-1.4", "omw-1.4"),
    ("taggers/averaged_perceptron_tagger_eng", "averaged_perceptron_tagger_eng"),
]

for resource_path, resource_name in _NLTK_RESOURCES:
    try:
        nltk.data.find(resource_path)
    except (LookupError, OSError):
        nltk.download(resource_name, quiet=True)

_lemmatizer = WordNetLemmatizer()

# Domain-aware negation words to preserve:
# Stripping words like "not" or "no" can completely invert query intent
# (e.g. "fee not paid" vs "fee paid").
PRESERVED_WORDS = {
    "not", "no", "never", "none", "neither", "nor", "cannot", "cant",
    "without", "against", "due", "after", "before", "once"
}

# Standard English stopwords excluding critical meaning-bearing words
_english_stopwords = set(stopwords.words("english")) - PRESERVED_WORDS

# Basic Hindi / Marathi common functional markers
_devanagari_stopwords = {
    "का", "के", "की", "को", "में", "से", "पर", "ने", "है", "हैं", "था", "थी", "थे",
    "चा", "ची", "चे", "च्या", "ला", "ना", "आहे", "होता", "होती", "होते"
}


# ── 1. Text Normalization ─────────────────────────────────────────────────────
def normalize_text(text: str) -> str:
    """
    Normalize raw text:
    - Case-fold for Latin characters (Devanagari characters are case-invariant).
    - Normalize Unicode compatibility characters (NFKC).
    - Remove punctuation while retaining alphanumeric tokens, Devanagari characters,
      and monetary symbols (₹, $).
    - Collapse redundant whitespace.

    Args:
        text: Input string.

    Returns:
        Cleaned, normalized string.
    """
    if not isinstance(text, str):
        return ""

    # Normalize Unicode composition
    text = unicodedata.normalize("NFKC", text)

    # Lowercase Latin text
    text = text.lower()

    # Remove unwanted punctuation while preserving:
    # - Standard alphanumeric: a-z, 0-9
    # - Devanagari Unicode block: \u0900-\u097F
    # - Currency symbol: ₹
    # - Whitespace
    text = re.sub(r"[^\w\s\u0900-\u097F₹]", " ", text)

    # Collapse consecutive whitespaces into a single space
    text = re.sub(r"\s+", " ", text).strip()

    return text


# ── 2. Tokenization ───────────────────────────────────────────────────────────
def tokenize(text: str) -> List[str]:
    """
    Tokenize normalized text into discrete word tokens.
    Supports both English words and Devanagari word units without breaking matras.

    Example:
        "How much fee is remaining?" -> ["how", "much", "fee", "is", "remaining"]
        "मेरी फीस कितनी बाकी है?"    -> ["मेरी", "फीस", "कितनी", "बाकी", "है"]

    Args:
        text: Normalized or raw string.

    Returns:
        List of string tokens.
    """
    cleaned = normalize_text(text)
    if not cleaned:
        return []

    # Regex token matching alphanumeric or Devanagari sequence
    tokens = re.findall(r"[\u0900-\u097F\w₹]+", cleaned)
    return tokens


# ── 3. Stopword Removal ───────────────────────────────────────────────────────
def remove_stopwords(
    tokens: List[str],
    preserve_negations: bool = True,
) -> List[str]:
    """
    Remove non-informative grammatical stopwords while preserving domain-critical
    words (e.g. 'not', 'no', 'cannot') that alter the intent of the sentence.

    Rationale:
        Blindly dropping all standard stopwords harms intent classification.
        For example:
          - "Why is my payment not approved?" without "not" becomes "payment approved",
            conflating PENDING_FEE / ISSUE with PAYMENT_STATUS.

    Args:
        tokens: List of input word tokens.
        preserve_negations: When True, preserves negation and constraint words.

    Returns:
        Filtered list of informative tokens.
    """
    stop_set = _english_stopwords if preserve_negations else set(stopwords.words("english"))

    filtered = []
    for token in tokens:
        # Check English stopwords
        if token in stop_set:
            continue
        filtered.append(token)

    return filtered


# ── 4. Lemmatization ──────────────────────────────────────────────────────────
def _get_wordnet_pos(treebank_tag: str) -> str:
    """Map POS tag to first character used by WordNetLemmatizer."""
    if treebank_tag.startswith("J"):
        return wordnet.ADJ
    elif treebank_tag.startswith("V"):
        return wordnet.VERB
    elif treebank_tag.startswith("N"):
        return wordnet.NOUN
    elif treebank_tag.startswith("R"):
        return wordnet.ADV
    else:
        return wordnet.NOUN


def lemmatize_tokens(tokens: List[str]) -> List[str]:
    """
    Lemmatize tokens to their dictionary root form using WordNet with POS tagging.

    Examples:
        - "paying"    -> "pay"
        - "payments"  -> "payment"
        - "remaining" -> "remain"

    Note on Multilingual Tokens:
        Devanagari (Hindi/Marathi) words do not exist in English WordNet and are
        safely returned untouched, avoiding token corruption.

    Args:
        tokens: List of string tokens.

    Returns:
        List of lemmatized tokens.
    """
    if not tokens:
        return []

    # Tag parts of speech for accurate morphological transformation
    tagged_tokens = nltk.pos_tag(tokens)

    lemmatized = []
    for word, tag in tagged_tokens:
        # Check if token is Latin script (English)
        if re.match(r"^[a-zA-Z]+$", word):
            pos = _get_wordnet_pos(tag)
            lemma = _lemmatizer.lemmatize(word, pos=pos)
            lemmatized.append(lemma)
        else:
            # Pass Devanagari and numeral/currency tokens through unchanged
            lemmatized.append(word)

    return lemmatized


# ── 5. End-to-End Modular Preprocessing Pipeline ──────────────────────────────
def preprocess(
    text: str,
    language: str = "en",
    return_tokens: bool = False,
) -> Union[str, List[str]]:
    """
    Full text preprocessing pipeline for FeeAssist AI.

    Steps:
        1. normalize_text (case-folding, unicode cleanup, punctuation removal)
        2. tokenize (language-safe word extraction)
        3. remove_stopwords (filtering non-informative words, preserving negations)
        4. lemmatize_tokens (POS-aware morphological reduction to root words)

    Args:
        text: Raw input query from user or dataset.
        language: Language hint ('en', 'hi', 'mr', 'English', etc.).
        return_tokens: If True, returns List[str]; otherwise returns joined string.

    Returns:
        Processed string (e.g. "much fee remain") or list of tokens.
    """
    normalized = normalize_text(text)
    tokens = tokenize(normalized)
    filtered = remove_stopwords(tokens, preserve_negations=True)
    lemmatized = lemmatize_tokens(filtered)

    if return_tokens:
        return lemmatized

    return " ".join(lemmatized)


# ── 6. Bag of Words (BoW) Feature Extraction ──────────────────────────────────
def extract_bow(
    corpus: List[str],
    max_features: int = 500,
    ngram_range: Tuple[int, int] = (1, 1),
) -> Tuple[CountVectorizer, any]:
    """
    Generate a Bag of Words representation for a collection of documents.

    Pipeline:
        Clean Text -> Vocabulary Construction -> Word Frequency Matrix

    Args:
        corpus: List of raw or preprocessed strings.
        max_features: Maximum vocabulary size.
        ngram_range: Lower and upper boundary of n-values for n-grams.

    Returns:
        Tuple of (fitted CountVectorizer, count_matrix).
    """
    # Use our preprocess function as the preprocessor
    vectorizer = CountVectorizer(
        preprocessor=preprocess,
        max_features=max_features,
        ngram_range=ngram_range,
    )
    matrix = vectorizer.fit_transform(corpus)
    return vectorizer, matrix


# ── 7. TF-IDF Feature Extraction ──────────────────────────────────────────────
def build_tfidf_vectorizer(
    max_features: int = 1500,
    ngram_range: Tuple[int, int] = (1, 2),
    min_df: int = 1,
    sublinear_tf: bool = True,
) -> TfidfVectorizer:
    """
    Construct a scikit-learn TfidfVectorizer pre-configured with the FeeAssist AI pipeline.

    Args:
        max_features: Maximum number of features in vocabulary.
        ngram_range: Tuple (min_n, max_n). Default is (1, 2) to capture unigrams and bigrams.
        min_df: Minimum document frequency threshold.
        sublinear_tf: Apply sublinear scaling (1 + log(tf)) to dampen high-frequency terms.

    Returns:
        Configured TfidfVectorizer instance.
    """
    return TfidfVectorizer(
        preprocessor=preprocess,
        token_pattern=r"[\u0900-\u097F\w₹]+",
        max_features=max_features,
        ngram_range=ngram_range,
        min_df=min_df,
        sublinear_tf=sublinear_tf,
    )


def extract_tfidf(
    corpus: List[str],
    vectorizer: TfidfVectorizer = None,
    fit: bool = True,
) -> Tuple[TfidfVectorizer, any]:
    """
    Extract TF-IDF feature matrix from a text corpus.

    Pipeline:
        Clean Text -> TF-IDF Vectorizer -> Numerical Feature Matrix

    Args:
        corpus: List of text queries.
        vectorizer: Existing TfidfVectorizer instance, or None to build a new one.
        fit: When True, fits the vectorizer on corpus; otherwise transforms only.

    Returns:
        Tuple of (TfidfVectorizer, tfidf_matrix).
    """
    if vectorizer is None:
        vectorizer = build_tfidf_vectorizer()

    if fit:
        matrix = vectorizer.fit_transform(corpus)
    else:
        matrix = vectorizer.transform(corpus)

    return vectorizer, matrix


# ── 8. Model Persistence Helpers ──────────────────────────────────────────────
def save_vectorizer(vectorizer: Union[CountVectorizer, TfidfVectorizer], filepath: str) -> str:
    """Save fitted vectorizer to disk for reuse during inference."""
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    joblib.dump(vectorizer, filepath)
    return filepath


def load_vectorizer(filepath: str) -> Union[CountVectorizer, TfidfVectorizer]:
    """Load pre-fitted vectorizer from disk."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Vectorizer file not found at: {filepath}")
    return joblib.load(filepath)
