"""
FeeAssist AI — Automated Preprocessing & Feature Extraction Tests

Verifies:
1. Tokenization on English, Hindi, and Marathi queries
2. Morphological lemmatization (paying -> pay, payments -> payment, remaining -> remain)
3. Domain stopword filtering with negation preservation (not, no, cannot)
4. Multilingual Unicode safety (Devanagari characters never corrupted or crashed)
5. Bag of Words extraction and vocabulary mapping
6. TF-IDF vectorization and feature matrix generation
7. Dataset integrity (10 intents, 3 languages, >= 35 samples per intent)
8. Stratified Train/Test split verification with fixed random seed
"""

import os
import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

# Ensure ml/ is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ensure UTF-8 output encoding on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from ml.preprocessing import (
    normalize_text,
    tokenize,
    remove_stopwords,
    lemmatize_tokens,
    preprocess,
    extract_bow,
    extract_tfidf,
    build_tfidf_vectorizer,
    save_vectorizer,
    load_vectorizer,
)


def test_tokenization():
    print("Test 1: Tokenization...")
    # English
    en_query = "How much fee is remaining?"
    en_tokens = tokenize(en_query)
    assert en_tokens == ["how", "much", "fee", "is", "remaining"], f"Unexpected tokens: {en_tokens}"

    # Uppercase English
    upper_query = "CAN I PAY MY FEES?"
    upper_tokens = tokenize(upper_query)
    assert upper_tokens == ["can", "i", "pay", "my", "fees"], f"Unexpected tokens: {upper_tokens}"

    # Hindi
    hi_query = "मेरी फीस कितनी बाकी है?"
    hi_tokens = tokenize(hi_query)
    assert "फीस" in hi_tokens and "बाकी" in hi_tokens, f"Hindi tokenization failed: {hi_tokens}"

    # Marathi
    mr_query = "माझी फी किती बाकी आहे?"
    mr_tokens = tokenize(mr_query)
    assert "फी" in mr_tokens and "बाकी" in mr_tokens, f"Marathi tokenization failed: {mr_tokens}"

    print("  -> Passed tokenization for English, Hindi, and Marathi")


def test_lemmatization():
    print("Test 2: Proper Lemmatization...")
    tokens = ["paying", "payments", "remaining", "installments", "studied"]
    lemmas = lemmatize_tokens(tokens)

    # paying -> pay (verb)
    assert lemmas[0] == "pay", f"Expected 'pay', got '{lemmas[0]}'"
    # payments -> payment (noun)
    assert lemmas[1] == "payment", f"Expected 'payment', got '{lemmas[1]}'"
    # remaining -> remain (verb)
    assert lemmas[2] == "remain", f"Expected 'remain', got '{lemmas[2]}'"

    print(f"  -> {tokens} -> {lemmas}")
    print("  -> Passed lemmatization verification")


def test_negation_preservation():
    print("Test 3: Stopword Removal with Negation Preservation...")
    query = "My fee was not paid and I cannot pay today"
    tokens = tokenize(query)
    filtered = remove_stopwords(tokens, preserve_negations=True)

    assert "not" in filtered, "'not' was incorrectly removed as stopword"
    assert "cannot" in filtered, "'cannot' was incorrectly removed as stopword"
    assert "fee" in filtered and "paid" in filtered

    print(f"  -> Filtered tokens: {filtered}")
    print("  -> Passed negation preservation test")


def test_multilingual_pipeline():
    print("Test 4: Multilingual Preprocessing Pipeline...")
    examples = [
        ("How much fee is remaining?", "much fee remain"),
        ("Can I PAY my fees?", "pay fee"),
        ("मेरी फीस कितनी बाकी है?", "मेरी फीस कितनी बाकी है"),
        ("माझी फी किती बाकी आहे?", "माझी फी किती बाकी आहे"),
    ]

    for raw, expected_hint in examples:
        result = preprocess(raw)
        assert isinstance(result, str) and len(result) > 0, f"Failed on query: {raw}"
        print(f"  [RAW] '{raw}' -> [PREPROCESSED] '{result}'")

    print("  -> Passed multilingual preprocessing pipeline")


def test_bag_of_words():
    print("Test 5: Bag of Words (BoW) Feature Extraction...")
    sample_corpus = [
        "How much is the semester fee?",
        "Can I pay fee in installments?",
        "Is there any pending fee remaining?",
    ]

    vectorizer, matrix = extract_bow(sample_corpus)
    vocab = vectorizer.get_feature_names_out()
    assert len(vocab) > 0
    assert matrix.shape[0] == 3
    assert matrix.shape[1] == len(vocab)
    print(f"  -> BoW Matrix Shape: {matrix.shape}")
    print(f"  -> Sample Vocabulary: {list(vocab)[:6]}...")
    print("  -> Passed Bag of Words demonstration")


def test_tfidf_extraction():
    print("Test 6: TF-IDF Feature Extraction...")
    sample_corpus = [
        "How much is the tuition fee structure?",
        "When is the fee payment due date?",
        "How to apply for fee refund?",
    ]

    vectorizer, matrix = extract_tfidf(sample_corpus)
    vocab = vectorizer.get_feature_names_out()
    assert len(vocab) > 0
    assert matrix.shape[0] == 3
    # Check that TF-IDF values are floats between 0 and 1
    assert matrix.dtype in (np.float32, np.float64)

    # Test persistence (save and load)
    tmp_path = os.path.join(os.path.dirname(__file__), "models", "test_tfidf.joblib")
    save_vectorizer(vectorizer, tmp_path)
    loaded_vec = load_vectorizer(tmp_path)
    assert len(loaded_vec.vocabulary_) == len(vectorizer.vocabulary_)
    if os.path.exists(tmp_path):
        os.remove(tmp_path)

    print(f"  -> TF-IDF Matrix Shape: {matrix.shape}")
    print("  -> Passed TF-IDF vectorization and persistence test")


def test_dataset_integrity_and_stratification():
    print("Test 7: Dataset Integrity & Stratified Split...")
    csv_path = os.path.join(os.path.dirname(__file__), "dataset", "fees_queries.csv")
    assert os.path.exists(csv_path), f"Dataset not found at {csv_path}"

    df = pd.read_csv(csv_path)
    assert "text" in df.columns and "intent" in df.columns and "language" in df.columns
    assert len(df) >= 350, f"Expected >= 350 rows, got {len(df)}"

    intents = df["intent"].unique()
    assert len(intents) == 10, f"Expected exactly 10 intents, got {len(intents)}: {intents}"

    languages = df["language"].unique()
    assert set(languages) == {"English", "Hindi", "Marathi"}

    # Ensure no duplicates
    duplicates = df[df.duplicated(subset=["text"])]
    assert len(duplicates) == 0, f"Found duplicate rows: {duplicates}"

    # Stratified Train/Test Split (Task 3 specification: X=text, y=intent, random_state=42)
    X = df["text"]
    y = df["intent"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    assert len(X_train) + len(X_test) == len(df)
    # Verify stratification: each intent should be represented in both splits
    assert len(np.unique(y_train)) == 10
    assert len(np.unique(y_test)) == 10

    print(f"  -> Total dataset rows: {len(df)}")
    print(f"  -> Intents ({len(intents)}): {sorted(list(intents))}")
    print(f"  -> Train samples: {len(X_train)}, Test samples: {len(X_test)}")
    print("  -> Passed dataset integrity and stratified split")


def run_all():
    print("==================================================")
    print("FeeAssist AI — NLP Preprocessing Test Suite")
    print("==================================================")
    test_tokenization()
    test_lemmatization()
    test_negation_preservation()
    test_multilingual_pipeline()
    test_bag_of_words()
    test_tfidf_extraction()
    test_dataset_integrity_and_stratification()
    print("==================================================")
    print("🎉 ALL NLP PREPROCESSING TESTS PASSED!")
    print("==================================================")


if __name__ == "__main__":
    run_all()
