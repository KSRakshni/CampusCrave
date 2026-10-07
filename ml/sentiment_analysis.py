"""Train and serve a compact TF-IDF feedback sentiment classifier."""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "feedback.csv"
MODEL_PATH = ROOT / "ml" / "models" / "sentiment_model.pkl"


def train_sentiment_model(data_path: str | Path = DATA_PATH, model_path: str | Path = MODEL_PATH):
    """Fit and persist a TF-IDF plus logistic-regression classifier."""
    source = Path(data_path)
    destination = Path(model_path)
    if not source.exists():
        raise FileNotFoundError(f"Sentiment training data not found: {source}")
    frame = pd.read_csv(source).dropna(subset=["text", "sentiment"])
    if frame.empty or frame["sentiment"].nunique() < 2:
        raise ValueError("Feedback data must contain labeled examples from at least two classes")
    model = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), lowercase=True)),
        ("classifier", LogisticRegression(max_iter=1000, random_state=42)),
    ])
    model.fit(frame["text"].astype(str), frame["sentiment"].astype(str))
    destination.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, destination)
    return model


def load_sentiment_model(model_path: str | Path = MODEL_PATH):
    """Load the classifier, fitting the bundled sample dataset on first use."""
    source = Path(model_path)
    if not source.exists():
        return train_sentiment_model(model_path=source)
    return joblib.load(source)


def analyze_sentiment(text: str) -> str:
    """Return Positive, Negative, or Neutral for a feedback string."""
    if not text or not text.strip():
        return "Neutral"
    return str(load_sentiment_model().predict([text.strip()])[0])