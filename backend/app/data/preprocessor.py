"""Preprocessor - Handles data preprocessing and feature engineering."""
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
import warnings
warnings.filterwarnings("ignore")


class TransactionPreprocessor:
    def __init__(self):
        self.label_encoders: Dict[str, LabelEncoder] = {}
        self.scaler = StandardScaler()
        self.feature_columns: List[str] = []
        self.fitted = False

    def create_behavioral_features(self, df: pd.DataFrame) -> pd.DataFrame:
        if df is None or df.empty:
            return pd.DataFrame()
        df = df.copy()
        df = df.sort_values(["customer_id", "timestamp"]).reset_index(drop=True)
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
        df["step"] = pd.to_numeric(df["step"], errors="coerce").fillna(0)
        df["amount_zscore_24h"] = df.groupby("customer_id")["amount"].transform(
            lambda x: (x - x.shift(1).rolling(24, min_periods=1).mean()) / (x.shift(1).rolling(24, min_periods=1).std() + 1e-8)
        )
        df["txn_count_24h"] = df.groupby("customer_id")["amount"].transform(lambda x: x.shift(1).rolling(24, min_periods=1).count())
        df["mean_amount_24h"] = df.groupby("customer_id")["amount"].transform(lambda x: x.shift(1).rolling(24, min_periods=1).mean())
        df["step_delta"] = df.groupby("customer_id")["step"].diff().fillna(0)
        df["merchant_occurrences"] = df.groupby(["customer_id", "merchant_id"]).cumcount().fillna(0).astype(int)
        df["is_first_time_pair"] = (df["merchant_occurrences"] == 0).astype(int)
        df["unique_merchants_count"] = df.groupby("customer_id")["merchant_id"].transform(
            lambda x: x.shift(1).rolling(24, min_periods=1).apply(lambda y: len(set(y)), raw=False)
        ).fillna(0)
        df["is_night"] = ((df["step"] % 24 < 6) | (df["step"] % 24 > 22)).astype(int)
        df["transaction_velocity"] = np.where(df["step_delta"] > 0, df["amount"] / df["step_delta"], 0)
        customer_mean = df.groupby("customer_id")["amount"].transform(lambda x: x.shift(1).expanding().mean())
        df["amount_deviation"] = df["amount"] - customer_mean.fillna(df["amount"])
        merchant_counts = df["merchant_id"].value_counts().to_dict()
        df["merchant_frequency"] = df["merchant_id"].map(merchant_counts).fillna(0)
        customer_counts = df["customer_id"].value_counts().to_dict()
        df["customer_frequency"] = df["customer_id"].map(customer_counts).fillna(0)
        category_counts = df["category"].value_counts().to_dict()
        df["category_frequency"] = df["category"].map(category_counts).fillna(0)
        df["customer_merchant_interaction"] = df.groupby(["customer_id", "merchant_id"]).cumcount()
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].fillna(0)
        return df

    def prepare_features(self, df: pd.DataFrame, fit: bool = True) -> Tuple[pd.DataFrame, List[str]]:
        if df is None or df.empty:
            return pd.DataFrame(), []
        df = df.copy()
        df = self.create_behavioral_features(df)
        categorical_cols = ["category", "customer_gender", "location", "device"]
        for col in categorical_cols:
            if col in df.columns:
                if fit:
                    le = LabelEncoder()
                    df[col] = df[col].fillna("UNKNOWN").astype(str)
                    df[col + "_encoded"] = le.fit_transform(df[col])
                    self.label_encoders[col] = le
                else:
                    le = self.label_encoders.get(col)
                    if le:
                        df[col] = df[col].fillna("UNKNOWN").astype(str)
                        known_classes = set(le.classes_)
                        df[col] = df[col].apply(lambda x: x if x in known_classes else "UNKNOWN")
                        if "UNKNOWN" not in le.classes_:
                            df[col + "_encoded"] = 0
                        else:
                            df[col + "_encoded"] = le.transform(df[col])
                    else:
                        df[col + "_encoded"] = 0
        feature_cols = [
            "amount", "amount_zscore_24h", "txn_count_24h", "mean_amount_24h",
            "step_delta", "merchant_occurrences", "is_first_time_pair",
            "unique_merchants_count", "is_night", "transaction_velocity",
            "amount_deviation", "merchant_frequency", "customer_frequency",
            "category_frequency", "customer_merchant_interaction"
        ]
        for col in categorical_cols:
            enc_col = col + "_encoded"
            if enc_col in df.columns:
                feature_cols.append(enc_col)
        available_features = [c for c in feature_cols if c in df.columns]
        numeric_features = [c for c in available_features if pd.api.types.is_numeric_dtype(df[c])]
        if fit and numeric_features and len(df) > 0:
            df[numeric_features] = self.scaler.fit_transform(df[numeric_features])
            self.fitted = True
        elif numeric_features and len(df) > 0:
            df[numeric_features] = self.scaler.transform(df[numeric_features])
        self.feature_columns = available_features
        return df, available_features

    def get_feature_matrix(self, df: pd.DataFrame) -> np.ndarray:
        if df is None or df.empty:
            return np.array([])
        features = [c for c in self.feature_columns if c in df.columns]
        if not features:
            return np.array([])
        return df[features].values
