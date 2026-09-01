"""SHAP Explanations - Transaction-level SHAP explanations."""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any
import warnings
warnings.filterwarnings("ignore")

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False


class SHAPExplainer:
    def __init__(self, model, feature_names: List[str]):
        self.model = model
        self.feature_names = feature_names
        self.explainer = None
        self.background_data = None

    def fit(self, X_background: np.ndarray):
        if not SHAP_AVAILABLE:
            return self
        try:
            if hasattr(self.model, "predict_proba"):
                self.explainer = shap.TreeExplainer(self.model)
            else:
                self.explainer = shap.KernelExplainer(self.model.predict, X_background[:100])
            self.background_data = X_background[:100]
        except Exception as e:
            print(f"SHAP explainer initialization failed: {e}")
        return self

    def explain(self, X: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        if not SHAP_AVAILABLE or self.explainer is None:
            return []
        try:
            shap_values = self.explainer.shap_values(X)
            if isinstance(shap_values, list):
                shap_values = shap_values[1]
            if X.ndim == 1:
                X = X.reshape(1, -1)
                shap_values = shap_values.reshape(1, -1) if hasattr(shap_values, "reshape") else np.array([shap_values])
            explanations = []
            for i in range(len(X)):
                sv = shap_values[i] if hasattr(shap_values, "__len__") and len(shap_values.shape) > 1 else shap_values
                feature_importance = [
                    {"feature": name, "value": float(X[i, j]), "shap_value": float(sv[j])}
                    for j, name in enumerate(self.feature_names)
                    if j < len(sv) and j < X.shape[1]
                ]
                feature_importance.sort(key=lambda x: abs(x["shap_value"]), reverse=True)
                explanations.append(feature_importance[:top_k])
            return explanations[0] if len(explanations) == 1 else explanations
        except Exception as e:
            print(f"SHAP explanation failed: {e}")
            return []

    def explain_transaction(self, transaction_features: pd.Series, feature_names: List[str]) -> List[Dict[str, Any]]:
        X = transaction_features[feature_names].values.reshape(1, -1)
        return self.explain(X, top_k=5)
