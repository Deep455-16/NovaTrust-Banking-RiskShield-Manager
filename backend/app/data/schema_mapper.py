"""Schema Normalization - Maps diverse dataset schemas to normalized RiskShield schema."""
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np

NORMALIZED_SCHEMA = {
    "transaction_id": "string",
    "timestamp": "datetime",
    "customer_id": "string",
    "merchant_id": "string",
    "amount": "float",
    "currency": "string",
    "category": "string",
    "location": "string",
    "device": "string",
    "customer_age": "string",
    "customer_gender": "string",
    "fraud_label": "int",
    "step": "int",
    "zipcode_ori": "string",
    "zipcode_merchant": "string"
}

DATASET_MAPPINGS = {
    "banksim": {
        "transaction_id": None, "timestamp": None, "customer_id": "customer",
        "merchant_id": "merchant", "amount": "amount", "currency": None,
        "category": "category", "location": None, "device": None,
        "customer_age": "age", "customer_gender": "gender", "fraud_label": "fraud",
        "step": "step", "zipcode_ori": "zipcodeOri", "zipcode_merchant": "zipMerchant"
    },
    "sfindset": {
        "transaction_id": "transaction_id", "timestamp": "timestamp",
        "customer_id": "from_account", "merchant_id": "to_account",
        "amount": "amount", "currency": None, "category": "transaction_type",
        "location": None, "device": None, "customer_age": None,
        "customer_gender": None, "fraud_label": "is_fraud",
        "step": None, "zipcode_ori": None, "zipcode_merchant": None
    },
    "global_bank": {
        "transaction_id": "transaction_id", "timestamp": None,
        "customer_id": "customer_id", "merchant_id": "merchant_id",
        "amount": "amount", "currency": "currency", "category": "transaction_type",
        "location": "location", "device": "device_type",
        "customer_age": None, "customer_gender": None, "fraud_label": "is_fraud",
        "step": None, "zipcode_ori": None, "zipcode_merchant": None
    },
    "bank_marketing": {
        "transaction_id": None, "timestamp": None, "customer_id": None,
        "merchant_id": None, "amount": "balance", "currency": None,
        "category": "job", "location": None, "device": None,
        "customer_age": "age", "customer_gender": None, "fraud_label": None,
        "step": None, "zipcode_ori": None, "zipcode_merchant": None
    },
    "synthetic": {
        "transaction_id": "transaction_id", "timestamp": "timestamp",
        "customer_id": "customer_id", "merchant_id": "merchant_id",
        "amount": "amount", "currency": "currency", "category": "category",
        "location": "location", "device": "device",
        "customer_age": "customer_age", "customer_gender": "customer_gender",
        "fraud_label": "fraud_label", "step": "step",
        "zipcode_ori": "zipcode_ori", "zipcode_merchant": "zipcode_merchant"
    }
}


def normalize_dataset(df: pd.DataFrame, dataset_name: str) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=list(NORMALIZED_SCHEMA.keys()))
    mapping = DATASET_MAPPINGS.get(dataset_name, {})
    result = {}
    for norm_col, dtype in NORMALIZED_SCHEMA.items():
        src_col = mapping.get(norm_col)
        if src_col and src_col in df.columns:
            result[norm_col] = df[src_col].copy()
        elif norm_col in df.columns:
            result[norm_col] = df[norm_col].copy()
        else:
            if norm_col == "transaction_id" and dataset_name == "banksim":
                result[norm_col] = [f"BS_{i:08d}" for i in range(len(df))]
            elif norm_col == "timestamp" and dataset_name == "banksim":
                base_time = pd.Timestamp("2023-01-01")
                result[norm_col] = pd.to_datetime(df["step"].astype(int) * 3600, unit="s", origin="2023-01-01")
            elif norm_col == "timestamp" and dataset_name == "global_bank":
                if "date" in df.columns and "time" in df.columns:
                    result[norm_col] = pd.to_datetime(df["date"].astype(str) + " " + df["time"].astype(str))
                else:
                    result[norm_col] = pd.NaT
            elif norm_col == "currency":
                result[norm_col] = "USD"
            elif norm_col == "fraud_label":
                result[norm_col] = 0
            elif norm_col == "location":
                result[norm_col] = "UNKNOWN"
            elif norm_col == "device":
                result[norm_col] = "UNKNOWN"
            elif norm_col == "customer_age":
                result[norm_col] = "UNKNOWN"
            elif norm_col == "customer_gender":
                result[norm_col] = "UNKNOWN"
            elif norm_col == "step":
                result[norm_col] = 0
            elif norm_col == "zipcode_ori":
                result[norm_col] = "UNKNOWN"
            elif norm_col == "zipcode_merchant":
                result[norm_col] = "UNKNOWN"
            else:
                result[norm_col] = None
    normalized_df = pd.DataFrame(result)
    if "amount" in normalized_df.columns:
        normalized_df["amount"] = pd.to_numeric(normalized_df["amount"], errors="coerce").fillna(0)
    if "fraud_label" in normalized_df.columns:
        normalized_df["fraud_label"] = pd.to_numeric(normalized_df["fraud_label"], errors="coerce").fillna(0).astype(int)
    if "step" in normalized_df.columns:
        normalized_df["step"] = pd.to_numeric(normalized_df["step"], errors="coerce").fillna(0).astype(int)
    return normalized_df


def get_schema_info(df: pd.DataFrame) -> Dict[str, Any]:
    if df is None or df.empty:
        return {"columns": [], "dtypes": {}, "missing": {}, "missing_pct": {}, "numeric_columns": [], "categorical_columns": []}
    return {
        "columns": list(df.columns),
        "dtypes": {col: str(df[col].dtype) for col in df.columns},
        "missing": {col: int(df[col].isna().sum()) for col in df.columns},
        "missing_pct": {col: float(df[col].isna().mean() * 100) for col in df.columns},
        "numeric_columns": list(df.select_dtypes(include=[np.number]).columns),
        "categorical_columns": list(df.select_dtypes(include=["object", "category"]).columns),
    }
