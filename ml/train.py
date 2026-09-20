"""
FeeAssist AI — Intent Classifier Training & Model Selection

Trains and rigorously benchmarks three ML classifiers on the multilingual
fees query dataset (405 queries across 10 intents in English, Hindi, and Marathi):
1. Multinomial Naive Bayes (MultinomialNB)
2. Logistic Regression (LogisticRegression)
3. Support Vector Machine (LinearSVC with Platt Scaling / CalibratedClassifierCV)

Evaluation metrics:
- Accuracy, Precision (Macro/Weighted), Recall (Macro/Weighted), F1-Score (Macro/Weighted)
- Per-class precision, recall, and F1
- Confusion Matrix

Generates visual evaluation artifacts and saves the champion model to ml/models/.
"""

import os
import sys
import json
from datetime import datetime

# Windows UTF-8 stdout configuration
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import LinearSVC

# Ensure ml/ is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ml.preprocessing import build_tfidf_vectorizer, preprocess


def train_and_evaluate():
    print("=" * 70)
    print("FeeAssist AI — Model Training & Benchmark Pipeline")
    print("=" * 70)

    # 1. Load Dataset
    dataset_path = os.path.join(BASE_DIR, "ml", "dataset", "fees_queries.csv")
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found at: {dataset_path}")

    df = pd.read_csv(dataset_path)
    print(f"Loaded dataset: {len(df)} samples across {df['intent'].nunique()} intents")

    # 2. Label Encoding
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(df["intent"])
    classes = list(label_encoder.classes_)
    print(f"Target classes ({len(classes)}): {classes}")

    # 3. Stratified Train/Test Split (80/20)
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        df["text"],
        y_encoded,
        test_size=0.20,
        random_state=42,
        stratify=y_encoded,
    )
    print(f"Partitioned: {len(X_train_raw)} train samples, {len(X_test_raw)} test samples")

    # 4. TF-IDF Feature Extraction
    print("\nFitting TF-IDF Vectorizer (unigrams + bigrams, sublinear TF, multilingual tokens)...")
    vectorizer = build_tfidf_vectorizer(
        max_features=2000,
        ngram_range=(1, 2),
        min_df=1,
        sublinear_tf=True,
    )
    X_train = vectorizer.fit_transform(X_train_raw)
    X_test = vectorizer.transform(X_test_raw)
    print(f"Feature matrix shape: Train={X_train.shape}, Test={X_test.shape}")

    # 5. Model Definitions
    models = {
        "Multinomial Naive Bayes": MultinomialNB(alpha=0.1),
        "Logistic Regression": LogisticRegression(
            C=3.0,
            max_iter=1000,
            random_state=42,
        ),
        "Support Vector Machine (Calibrated)": CalibratedClassifierCV(
            estimator=LinearSVC(C=2.0, random_state=42),
            cv=3,
        ),
    }

    results = {}
    best_model_name = None
    best_macro_f1 = -1.0
    best_model_obj = None

    print("\n" + "=" * 70)
    print("Evaluating Candidate Models on Test Set (81 samples)")
    print("=" * 70)

    for name, model in models.items():
        print(f"\nTraining: {name}...")
        model.fit(X_train, y_train)

        # Predictions
        y_pred = model.predict(X_test)

        # Metrics
        acc = float(accuracy_score(y_test, y_pred))
        macro_prec = float(precision_score(y_test, y_pred, average="macro", zero_division=0))
        macro_rec = float(recall_score(y_test, y_pred, average="macro", zero_division=0))
        macro_f1 = float(f1_score(y_test, y_pred, average="macro", zero_division=0))
        weighted_f1 = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))
        cm = confusion_matrix(y_test, y_pred).tolist()
        report = classification_report(
            y_test,
            y_pred,
            target_names=classes,
            output_dict=True,
            zero_division=0,
        )

        results[name] = {
            "accuracy": acc,
            "macro_precision": macro_prec,
            "macro_recall": macro_rec,
            "macro_f1": macro_f1,
            "weighted_f1": weighted_f1,
            "confusion_matrix": cm,
            "per_class": {
                c: {
                    "precision": float(report[c]["precision"]),
                    "recall": float(report[c]["recall"]),
                    "f1_score": float(report[c]["f1-score"]),
                    "support": int(report[c]["support"]),
                }
                for c in classes
            },
        }

        print(f"  -> Accuracy:     {acc * 100:.2f}%")
        print(f"  -> Macro F1:     {macro_f1 * 100:.2f}%")
        print(f"  -> Weighted F1:  {weighted_f1 * 100:.2f}%")
        print(f"  -> Macro Prec:   {macro_prec * 100:.2f}%")
        print(f"  -> Macro Recall: {macro_rec * 100:.2f}%")

        if macro_f1 > best_macro_f1:
            best_macro_f1 = macro_f1
            best_model_name = name
            best_model_obj = model

    print("\n" + "=" * 70)
    print(f"🏆 Champion Model: {best_model_name} (Macro F1 = {best_macro_f1 * 100:.2f}%)")
    print("=" * 70)

    # 7. Persist Models & Artifacts
    models_dir = os.path.join(BASE_DIR, "ml", "models")
    os.makedirs(models_dir, exist_ok=True)

    # Save best model, vectorizer, and label encoder
    model_path = os.path.join(models_dir, "best_model.joblib")
    vectorizer_path = os.path.join(models_dir, "tfidf_vectorizer.joblib")
    encoder_path = os.path.join(models_dir, "label_encoder.joblib")

    joblib.dump(best_model_obj, model_path)
    joblib.dump(vectorizer, vectorizer_path)
    joblib.dump(label_encoder, encoder_path)

    print(f"Saved best model to:      {model_path}")
    print(f"Saved TF-IDF vectorizer:  {vectorizer_path}")
    print(f"Saved label encoder:      {encoder_path}")

    # Save metadata
    metadata = {
        "timestamp": datetime.now().isoformat(),
        "dataset_total_samples": len(df),
        "train_samples": len(X_train_raw),
        "test_samples": len(X_test_raw),
        "classes": classes,
        "champion_model": best_model_name,
        "selection_metric": "macro_f1",
        "champion_metrics": {
            "accuracy": results[best_model_name]["accuracy"],
            "macro_f1": results[best_model_name]["macro_f1"],
            "weighted_f1": results[best_model_name]["weighted_f1"],
            "macro_precision": results[best_model_name]["macro_precision"],
            "macro_recall": results[best_model_name]["macro_recall"],
        },
        "all_benchmarks": results,
    }

    metadata_path = os.path.join(models_dir, "model_metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"Saved model metadata to:  {metadata_path}")

    # 8. Generate & Save Visualizations
    print("\nGenerating evaluation charts...")
    _generate_visualizations(models_dir, results, classes, best_model_name)

    print("\nTraining & evaluation completed successfully!")
    return results, best_model_name


def _generate_visualizations(output_dir: str, results: dict, classes: list, best_model_name: str):
    """Generate and save publication-quality evaluation plots."""
    sns.set_theme(style="whitegrid", palette="deep")
    plt.rcParams["font.sans-serif"] = "DejaVu Sans"

    # 1. Model Comparison Bar Chart
    fig, ax = plt.subplots(figsize=(10, 5), dpi=120)
    model_names = list(results.keys())
    accuracies = [results[m]["accuracy"] * 100 for m in model_names]
    macro_f1s = [results[m]["macro_f1"] * 100 for m in model_names]
    weighted_f1s = [results[m]["weighted_f1"] * 100 for m in model_names]

    x = np.arange(len(model_names))
    width = 0.25

    rects1 = ax.bar(x - width, accuracies, width, label="Accuracy (%)", color="#6366f1")
    rects2 = ax.bar(x, macro_f1s, width, label="Macro F1 (%)", color="#10b981")
    rects3 = ax.bar(x + width, weighted_f1s, width, label="Weighted F1 (%)", color="#f59e0b")

    ax.set_ylabel("Score (%)", fontsize=11, fontweight="bold")
    ax.set_title("FeeAssist AI — Classifier Benchmark Comparison", fontsize=13, fontweight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(model_names, fontsize=10)
    ax.set_ylim(0, 110)
    ax.legend(loc="upper left")

    # Annotate bar values
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(
                f"{height:.1f}%",
                xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8,
                fontweight="semibold",
            )

    autolabel(rects1)
    autolabel(rects2)
    autolabel(rects3)

    plt.tight_layout()
    comp_path = os.path.join(output_dir, "model_comparison.png")
    plt.savefig(comp_path)
    plt.close()
    print(f"  -> Saved {comp_path}")

    # 2. Confusion Matrix Heatmap (Best Model)
    fig, ax = plt.subplots(figsize=(10, 8), dpi=120)
    best_cm = np.array(results[best_model_name]["confusion_matrix"])
    sns.heatmap(
        best_cm,
        annot=True,
        fmt="d",
        cmap="Purples",
        xticklabels=classes,
        yticklabels=classes,
        ax=ax,
        cbar=True,
    )
    ax.set_title(f"Confusion Matrix — {best_model_name}", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Predicted Intent", fontsize=11, fontweight="bold")
    ax.set_ylabel("True Intent", fontsize=11, fontweight="bold")
    plt.xticks(rotation=45, ha="right", fontsize=9)
    plt.yticks(rotation=0, fontsize=9)
    plt.tight_layout()
    cm_path = os.path.join(output_dir, "confusion_matrix_best.png")
    plt.savefig(cm_path)
    plt.close()
    print(f"  -> Saved {cm_path}")

    # 3. Per-Intent F1 Score Bar Chart (Best Model)
    fig, ax = plt.subplots(figsize=(11, 5), dpi=120)
    per_class_f1 = [results[best_model_name]["per_class"][c]["f1_score"] * 100 for c in classes]

    y_pos = np.arange(len(classes))
    bars = ax.barh(y_pos, per_class_f1, color="#8b5cf6", edgecolor="#6d28d9")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(classes, fontsize=9, fontweight="medium")
    ax.invert_yaxis()  # Labels read top-to-bottom
    ax.set_xlabel("F1-Score (%)", fontsize=11, fontweight="bold")
    ax.set_title(f"Per-Intent F1-Scores — {best_model_name}", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlim(0, 115)

    for bar in bars:
        width = bar.get_width()
        ax.text(
            width + 1.5,
            bar.get_y() + bar.get_height() / 2,
            f"{width:.1f}%",
            ha="left",
            va="center",
            fontsize=9,
            fontweight="semibold",
        )

    plt.tight_layout()
    f1_path = os.path.join(output_dir, "per_intent_f1.png")
    plt.savefig(f1_path)
    plt.close()
    print(f"  -> Saved {f1_path}")


if __name__ == "__main__":
    train_and_evaluate()
