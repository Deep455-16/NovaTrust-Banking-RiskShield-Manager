"""ML Models - Fraud detection model implementations."""
import os
import pickle
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    roc_auc_score, average_precision_score, precision_score, recall_score,
    f1_score, precision_recall_curve, roc_curve, confusion_matrix
)
import warnings
warnings.filterwarnings("ignore")

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

try:
    from imblearn.over_sampling import SMOTE
    from imblearn.under_sampling import RandomUnderSampler
    IMBLEARN_AVAILABLE = True
except ImportError:
    IMBLEARN_AVAILABLE = False

MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)


class ModelArtifact:
    def __init__(self, model, name: str, version: str = "1.0.0", metadata: Dict = None):
        self.model = model
        self.name = name
        self.version = version
        self.metadata = metadata or {}
        self.trained = False

    def save(self, path: Optional[Path] = None):
        path = path or MODELS_DIR / f"{self.name}_v{self.version}.pkl"
        artifact = {"model": self.model, "name": self.name, "version": self.version, "metadata": self.metadata}
        with open(path, "wb") as f:
            pickle.dump(artifact, f)
        return path

    @classmethod
    def load(cls, path: Path):
        with open(path, "rb") as f:
            artifact = pickle.load(f)
        m = cls(artifact["model"], artifact["name"], artifact["version"], artifact["metadata"])
        m.trained = True
        return m


class FraudDetectionModel:
    def __init__(self, name: str):
        self.name = name
        self.artifact: Optional[ModelArtifact] = None
        self.metrics: Dict[str, float] = {}

    def train(self, X_train: np.ndarray, y_train: np.ndarray, **kwargs) -> "FraudDetectionModel":
        raise NotImplementedError

    def predict(self, X: np.ndarray) -> np.ndarray:
        if self.artifact is None or not self.artifact.trained:
            raise ValueError("Model not trained")
        return self.artifact.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if self.artifact is None or not self.artifact.trained:
            raise ValueError("Model not trained")
        if hasattr(self.artifact.model, "predict_proba"):
            return self.artifact.model.predict_proba(X)[:, 1]
        return self.artifact.model.predict(X)

    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
        if self.artifact is None or not self.artifact.trained:
            return {"status": "Not evaluated yet"}
        y_pred = self.predict(X_test)
        y_prob = self.predict_proba(X_test)
        if len(np.unique(y_test)) < 2:
            return {"status": "Only one class in test set"}
        self.metrics = {
            "roc_auc": float(roc_auc_score(y_test, y_prob)),
            "pr_auc": float(average_precision_score(y_test, y_prob)),
            "precision": float(precision_score(y_test, y_pred, zero_division=0)),
            "recall": float(recall_score(y_test, y_pred, zero_division=0)),
            "f1": float(f1_score(y_test, y_pred, zero_division=0)),
        }
        k = max(1, int(len(y_test) * 0.01))
        top_k_idx = np.argsort(y_prob)[-k:]
        self.metrics["precision_at_k"] = float(y_test[top_k_idx].mean())
        fpr, tpr, thresholds = roc_curve(y_test, y_prob)
        fpr_01_idx = np.where(fpr <= 0.001)[0]
        if len(fpr_01_idx) > 0:
            self.metrics["recall_at_0.1_fpr"] = float(tpr[fpr_01_idx[-1]])
        else:
            self.metrics["recall_at_0.1_fpr"] = 0.0
        self.metrics["roc_curve"] = {"fpr": fpr.tolist(), "tpr": tpr.tolist()}
        precision_vals, recall_vals, _ = precision_recall_curve(y_test, y_prob)
        self.metrics["pr_curve"] = {"precision": precision_vals.tolist(), "recall": recall_vals.tolist()}
        cm = confusion_matrix(y_test, y_pred)
        self.metrics["confusion_matrix"] = cm.tolist()
        if hasattr(self.artifact.model, "feature_importances_"):
            self.metrics["feature_importance"] = self.artifact.model.feature_importances_.tolist()
        elif hasattr(self.artifact.model, "coef_"):
            self.metrics["feature_importance"] = np.abs(self.artifact.model.coef_[0]).tolist()
        return self.metrics

    def save(self):
        if self.artifact:
            self.artifact.metadata["metrics"] = self.metrics
            return self.artifact.save()

    def load(self, path: Path):
        self.artifact = ModelArtifact.load(path)
        self.metrics = self.artifact.metadata.get("metrics", {})


class WeightedLightGBM(FraudDetectionModel):
    def __init__(self, params: Dict = None):
        super().__init__("weighted_lightgbm")
        self.params = params or {"objective": "binary", "metric": "auc", "boosting_type": "gbdt", "num_leaves": 31, "learning_rate": 0.05, "feature_fraction": 0.9, "bagging_fraction": 0.8, "bagging_freq": 5, "verbose": -1, "n_estimators": 100}

    def train(self, X_train: np.ndarray, y_train: np.ndarray, **kwargs) -> "WeightedLightGBM":
        if not LIGHTGBM_AVAILABLE:
            raise ImportError("LightGBM not available")
        neg_count = (y_train == 0).sum()
        pos_count = (y_train == 1).sum()
        scale_pos_weight = neg_count / max(pos_count, 1)
        params = self.params.copy()
        params["scale_pos_weight"] = scale_pos_weight
        model = lgb.LGBMClassifier(**params)
        model.fit(X_train, y_train)
        self.artifact = ModelArtifact(model, self.name, metadata={"scale_pos_weight": float(scale_pos_weight), "n_samples": len(y_train), "fraud_rate": float(y_train.mean())})
        self.artifact.trained = True
        return self


class EasyNegativeUndersamplingLGBM(FraudDetectionModel):
    def __init__(self, ratio: float = 0.05, n_models: int = 5):
        super().__init__(f"lgbm_eu_{ratio}")
        self.ratio = ratio
        self.n_models = n_models
        self.models: List[lgb.LGBMClassifier] = []
        self.params = {"objective": "binary", "metric": "auc", "boosting_type": "gbdt", "num_leaves": 31, "learning_rate": 0.05, "verbose": -1, "n_estimators": 100}

    def train(self, X_train: np.ndarray, y_train: np.ndarray, **kwargs) -> "EasyNegativeUndersamplingLGBM":
        if not LIGHTGBM_AVAILABLE or not IMBLEARN_AVAILABLE:
            raise ImportError("LightGBM or imbalanced-learn not available")
        pos_indices = np.where(y_train == 1)[0]
        neg_indices = np.where(y_train == 0)[0]
        n_pos = len(pos_indices)
        n_neg_target = int(n_pos / self.ratio)
        self.models = []
        for i in range(self.n_models):
            neg_sample = np.random.choice(neg_indices, size=min(n_neg_target, len(neg_indices)), replace=False)
            sample_indices = np.concatenate([pos_indices, neg_sample])
            np.random.shuffle(sample_indices)
            X_sample = X_train[sample_indices]
            y_sample = y_train[sample_indices]
            model = lgb.LGBMClassifier(**self.params)
            model.fit(X_sample, y_sample)
            self.models.append(model)
        self.artifact = ModelArtifact(self, self.name, metadata={"ratio": self.ratio, "n_models": self.n_models, "n_pos": n_pos, "n_neg_target": n_neg_target})
        self.artifact.trained = True
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if not self.models:
            raise ValueError("No models trained")
        probs = np.array([m.predict_proba(X)[:, 1] for m in self.models])
        return probs.mean(axis=0)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return (self.predict_proba(X) > 0.5).astype(int)


class SMOTELightGBM(FraudDetectionModel):
    def __init__(self, target_ratio: float = 0.1):
        super().__init__("smote_lightgbm")
        self.target_ratio = target_ratio
        self.params = {"objective": "binary", "metric": "auc", "boosting_type": "gbdt", "num_leaves": 31, "learning_rate": 0.05, "verbose": -1, "n_estimators": 100}

    def train(self, X_train: np.ndarray, y_train: np.ndarray, **kwargs) -> "SMOTELightGBM":
        if not LIGHTGBM_AVAILABLE or not IMBLEARN_AVAILABLE:
            raise ImportError("LightGBM or imbalanced-learn not available")
        smote = SMOTE(sampling_strategy=self.target_ratio, random_state=42)
        X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
        model = lgb.LGBMClassifier(**self.params)
        model.fit(X_resampled, y_resampled)
        self.artifact = ModelArtifact(model, self.name, metadata={"target_ratio": self.target_ratio, "original_shape": list(X_train.shape), "resampled_shape": list(X_resampled.shape)})
        self.artifact.trained = True
        return self


class WeightedXGBoost(FraudDetectionModel):
    def __init__(self, params: Dict = None):
        super().__init__("weighted_xgboost")
        self.params = params or {"objective": "binary:logistic", "eval_metric": "auc", "max_depth": 6, "learning_rate": 0.1, "n_estimators": 100, "subsample": 0.8, "colsample_bytree": 0.8}

    def train(self, X_train: np.ndarray, y_train: np.ndarray, **kwargs) -> "WeightedXGBoost":
        if not XGBOOST_AVAILABLE:
            raise ImportError("XGBoost not available")
        neg_count = (y_train == 0).sum()
        pos_count = (y_train == 1).sum()
        scale_pos_weight = neg_count / max(pos_count, 1)
        params = self.params.copy()
        params["scale_pos_weight"] = scale_pos_weight
        model = xgb.XGBClassifier(**params, use_label_encoder=False)
        model.fit(X_train, y_train)
        self.artifact = ModelArtifact(model, self.name, metadata={"scale_pos_weight": float(scale_pos_weight)})
        self.artifact.trained = True
        return self


class LogisticRegressionBaseline(FraudDetectionModel):
    def __init__(self):
        super().__init__("logistic_regression")

    def train(self, X_train: np.ndarray, y_train: np.ndarray, **kwargs) -> "LogisticRegressionBaseline":
        model = LogisticRegression(max_iter=1000, class_weight="balanced")
        model.fit(X_train, y_train)
        self.artifact = ModelArtifact(model, self.name)
        self.artifact.trained = True
        return self


class RandomForestBaseline(FraudDetectionModel):
    def __init__(self):
        super().__init__("random_forest")

    def train(self, X_train: np.ndarray, y_train: np.ndarray, **kwargs) -> "RandomForestBaseline":
        model = RandomForestClassifier(n_estimators=100, class_weight="balanced", random_state=42, n_jobs=-1)
        model.fit(X_train, y_train)
        self.artifact = ModelArtifact(model, self.name)
        self.artifact.trained = True
        return self


class ModelManager:
    def __init__(self):
        self.models: Dict[str, FraudDetectionModel] = {}
        self.model_classes = {
            "weighted_lightgbm": WeightedLightGBM,
            "lgbm_eu_0.02": lambda: EasyNegativeUndersamplingLGBM(ratio=0.02),
            "lgbm_eu_0.05": lambda: EasyNegativeUndersamplingLGBM(ratio=0.05),
            "lgbm_eu_0.10": lambda: EasyNegativeUndersamplingLGBM(ratio=0.10),
            "smote_lightgbm": SMOTELightGBM,
            "weighted_xgboost": WeightedXGBoost,
            "logistic_regression": LogisticRegressionBaseline,
            "random_forest": RandomForestBaseline
        }

    def train_model(self, name: str, X_train: np.ndarray, y_train: np.ndarray, **kwargs) -> Dict:
        if name not in self.model_classes:
            return {"error": f"Unknown model: {name}"}
        try:
            model = self.model_classes[name]()
            model.train(X_train, y_train, **kwargs)
            self.models[name] = model
            return {"status": "success", "model": name}
        except Exception as e:
            return {"error": str(e), "model": name}

    def evaluate_model(self, name: str, X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        if name not in self.models:
            return {"status": "Not evaluated yet", "model": name}
        try:
            metrics = self.models[name].evaluate(X_test, y_test)
            metrics["model"] = name
            return metrics
        except Exception as e:
            return {"error": str(e), "model": name}

    def predict(self, name: str, X: np.ndarray) -> np.ndarray:
        if name not in self.models:
            raise ValueError(f"Model {name} not trained")
        return self.models[name].predict_proba(X)

    def get_all_metrics(self) -> Dict[str, Dict]:
        return {name: model.metrics for name, model in self.models.items()}

    def save_all(self):
        paths = {}
        for name, model in self.models.items():
            path = model.save()
            paths[name] = str(path)
        return paths

    def load_all(self):
        for path in MODELS_DIR.glob("*.pkl"):
            try:
                artifact = ModelArtifact.load(path)
                name = artifact.name
                if name in self.model_classes:
                    model = self.model_classes[name]()
                    model.artifact = artifact
                    model.metrics = artifact.metadata.get("metrics", {})
                    self.models[name] = model
            except Exception as e:
                print(f"Error loading {path}: {e}")
