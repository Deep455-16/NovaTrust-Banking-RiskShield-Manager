"""Anomaly Detection - Unsupervised anomaly detection component."""
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Optional, Any
import pickle
from pathlib import Path

ANOMALY_MODEL_PATH = Path("models/anomaly_model.pkl")


class AnomalyDetector:
    def __init__(self, contamination: float = 0.05):
        self.model = IsolationForest(n_estimators=100, contamination=contamination, random_state=42, n_jobs=-1)
        self.scaler = StandardScaler()
        self.fitted = False

    def fit(self, X: np.ndarray):
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        self.fitted = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        if not self.fitted:
            raise ValueError("Model not fitted")
        X_scaled = self.scaler.transform(X)
        scores = -self.model.decision_function(X_scaled)
        scores = (scores - scores.min()) / (scores.max() - scores.min() + 1e-8)
        return scores

    def save(self, path: Path = ANOMALY_MODEL_PATH):
        with open(path, "wb") as f:
            pickle.dump({"model": self.model, "scaler": self.scaler}, f)

    def load(self, path: Path = ANOMALY_MODEL_PATH):
        with open(path, "rb") as f:
            data = pickle.load(f)
        self.model = data["model"]
        self.scaler = data["scaler"]
        self.fitted = True
