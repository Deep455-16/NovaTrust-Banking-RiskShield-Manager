"""Data Validation - Validates dataset integrity and schema compliance."""
from typing import Dict, List, Any
import pandas as pd
import numpy as np


class DataValidator:
    @staticmethod
    def validate_dataset(df: pd.DataFrame, dataset_name: str) -> Dict[str, Any]:
        if df is None:
            return {"valid": False, "issues": ["Dataset is None"], "warnings": [], "row_count": 0, "column_count": 0, "null_percentage": 0}
        issues = []
        warnings = []
        if df.empty:
            issues.append("Dataset is empty")
            return {"valid": False, "issues": issues, "warnings": warnings, "row_count": 0, "column_count": 0, "null_percentage": 0}
        if dataset_name == "banksim":
            required = ["step", "customer", "amount", "fraud"]
            for col in required:
                if col not in df.columns:
                    issues.append(f"Missing required column: {col}")
        null_counts = df.isnull().sum()
        high_null_cols = null_counts[null_counts > len(df) * 0.5].index.tolist()
        if high_null_cols:
            warnings.append(f"Columns with >50% nulls: {high_null_cols}")
        dup_count = df.duplicated().sum()
        if dup_count > 0:
            warnings.append(f"Found {dup_count} duplicate rows")
        if "fraud" in df.columns:
            fraud_rate = df["fraud"].mean()
            if fraud_rate == 0:
                warnings.append("No fraud cases found in dataset")
            elif fraud_rate > 0.5:
                warnings.append(f"Unusually high fraud rate: {fraud_rate:.2%}")
        if "amount" in df.columns:
            amounts = pd.to_numeric(df["amount"], errors="coerce")
            if amounts.min() < 0:
                issues.append("Negative amounts found")
            if amounts.max() > 1000000:
                warnings.append(f"Very high amounts detected: max={amounts.max()}")
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "row_count": len(df),
            "column_count": len(df.columns),
            "null_percentage": float(df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100)
        }

    @staticmethod
    def get_profile(df: pd.DataFrame) -> Dict[str, Any]:
        if df is None or df.empty:
            return {"row_count": 0, "column_count": 0, "memory_usage_mb": 0, "columns": {}}
        profile = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "memory_usage_mb": float(df.memory_usage(deep=True).sum() / 1024 / 1024),
            "columns": {}
        }
        for col in df.columns:
            col_profile = {
                "dtype": str(df[col].dtype),
                "null_count": int(df[col].isnull().sum()),
                "null_pct": float(df[col].isnull().mean() * 100),
                "unique_count": int(df[col].nunique())
            }
            if pd.api.types.is_numeric_dtype(df[col]):
                col_profile.update({
                    "min": float(df[col].min()) if not pd.isna(df[col].min()) else None,
                    "max": float(df[col].max()) if not pd.isna(df[col].max()) else None,
                    "mean": float(df[col].mean()) if not pd.isna(df[col].mean()) else None,
                    "std": float(df[col].std()) if not pd.isna(df[col].std()) else None,
                    "median": float(df[col].median()) if not pd.isna(df[col].median()) else None,
                })
            else:
                top_vals = df[col].value_counts().head(5).to_dict()
                col_profile["top_values"] = {str(k): int(v) for k, v in top_vals.items()}
            profile["columns"][col] = col_profile
        return profile
