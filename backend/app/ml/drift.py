"""Model Drift - Monitor training vs streaming distribution."""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from scipy import stats


@dataclass
class DriftReport:
    feature: str
    status: str
    p_value: float
    statistic: float
    training_mean: float
    streaming_mean: float


class DriftMonitor:
    def __init__(self, threshold: float = 0.05):
        self.threshold = threshold
        self.training_distributions: Dict[str, Dict] = {}
        self.drift_history: List[Dict] = []

    def fit(self, df: pd.DataFrame, features: List[str]):
        for feature in features:
            if feature in df.columns and pd.api.types.is_numeric_dtype(df[feature]):
                self.training_distributions[feature] = {
                    "mean": float(df[feature].mean()),
                    "std": float(df[feature].std()),
                    "median": float(df[feature].median()),
                    "q25": float(df[feature].quantile(0.25)),
                    "q75": float(df[feature].quantile(0.75))
                }

    def check_drift(self, df: pd.DataFrame, features: List[str]) -> List[DriftReport]:
        reports = []
        for feature in features:
            if feature not in self.training_distributions or feature not in df.columns:
                continue
            if not pd.api.types.is_numeric_dtype(df[feature]):
                continue
            train_mean = self.training_distributions[feature]["mean"]
            stream_mean = float(df[feature].mean())
            stream_std = float(df[feature].std())
            n = len(df)
            if n > 0 and stream_std > 0:
                z_score = abs(stream_mean - train_mean) / (stream_std / np.sqrt(n))
                p_value = 2 * (1 - stats.norm.cdf(z_score))
            else:
                p_value = 1.0
                z_score = 0.0
            if p_value < 0.01:
                status = "DRIFT DETECTED"
            elif p_value < self.threshold:
                status = "WARNING"
            else:
                status = "NORMAL"
            reports.append(DriftReport(
                feature=feature, status=status, p_value=round(p_value, 6),
                statistic=round(z_score, 4), training_mean=round(train_mean, 4),
                streaming_mean=round(stream_mean, 4)
            ))
        return reports

    def get_overall_status(self, reports: List[DriftReport]) -> str:
        if any(r.status == "DRIFT DETECTED" for r in reports):
            return "DRIFT DETECTED"
        elif any(r.status == "WARNING" for r in reports):
            return "WARNING"
        return "NORMAL"

    def get_fraud_rate_drift(self, training_rate: float, current_rate: float) -> Dict:
        diff = abs(current_rate - training_rate)
        if diff > 0.02:
            status = "DRIFT DETECTED"
        elif diff > 0.01:
            status = "WARNING"
        else:
            status = "NORMAL"
        return {
            "feature": "fraud_rate", "status": status,
            "training_rate": round(training_rate, 4),
            "current_rate": round(current_rate, 4),
            "difference": round(diff, 4)
        }
