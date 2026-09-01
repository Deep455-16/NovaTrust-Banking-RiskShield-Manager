"""Dataset Loader - Loads and manages datasets."""
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np

from .dataset_registry import DATASETS, discover_files, get_dataset_info, get_project_root
from .schema_mapper import normalize_dataset, get_schema_info
from .data_validator import DataValidator


class DatasetLoader:
    def __init__(self, data_dir: str = None):
        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            self.data_dir = get_project_root() / "data"
        self._cache: Dict[str, pd.DataFrame] = {}
        self._normalized_cache: Dict[str, pd.DataFrame] = {}
        self.validator = DataValidator()

    def load_dataset(self, dataset_name: str, normalize: bool = True) -> Optional[pd.DataFrame]:
        if dataset_name in self._cache:
            df = self._cache[dataset_name]
            if normalize and dataset_name in self._normalized_cache:
                return self._normalized_cache[dataset_name]
            elif normalize:
                norm_df = normalize_dataset(df, dataset_name)
                self._normalized_cache[dataset_name] = norm_df
                return norm_df
            return df
        if dataset_name not in DATASETS:
            print(f"Dataset '{dataset_name}' not found in registry")
            return None
        config = DATASETS[dataset_name]
        files = discover_files(config["path"])
        if not files:
            print(f"Dataset '{dataset_name}' not available - no files found in {config['path']}")
            return None
        csv_files = [f for f in files if f.suffix == ".csv"]
        if not csv_files:
            print(f"Dataset '{dataset_name}' - no CSV files found")
            return None
        try:
            df = pd.read_csv(csv_files[0])
            self._cache[dataset_name] = df
            if normalize:
                norm_df = normalize_dataset(df, dataset_name)
                self._normalized_cache[dataset_name] = norm_df
                return norm_df
            return df
        except Exception as e:
            print(f"Error loading dataset '{dataset_name}': {e}")
            return None

    def get_dataset_profile(self, dataset_name: str) -> Optional[Dict[str, Any]]:
        df = self.load_dataset(dataset_name, normalize=False)
        if df is None:
            return None
        return self.validator.get_profile(df)

    def validate_dataset(self, dataset_name: str) -> Dict[str, Any]:
        df = self.load_dataset(dataset_name, normalize=False)
        if df is None:
            return {"valid": False, "issues": ["Dataset not available"], "warnings": []}
        return self.validator.validate_dataset(df, dataset_name)

    def get_fraud_distribution(self, dataset_name: str) -> Optional[Dict[str, Any]]:
        df = self.load_dataset(dataset_name, normalize=False)
        if df is None:
            return None
        config = DATASETS.get(dataset_name, {})
        label_col = config.get("label_column")
        if label_col and label_col in df.columns:
            if df[label_col].dtype == object:
                if set(df[label_col].unique()).issubset({"no", "yes", "0", "1", 0, 1}):
                    fraud_count = int((df[label_col].isin(["yes", "1", 1])).sum())
                    return {"fraud": fraud_count, "normal": len(df) - fraud_count, "fraud_rate": fraud_count / len(df)}
            else:
                fraud_count = int(df[label_col].sum())
                return {"fraud": fraud_count, "normal": len(df) - fraud_count, "fraud_rate": fraud_count / len(df)}
        return None

    def list_available_datasets(self) -> List[str]:
        available = []
        for name, config in DATASETS.items():
            files = discover_files(config["path"])
            if files:
                available.append(name)
        return available

    def clear_cache(self):
        self._cache.clear()
        self._normalized_cache.clear()


dataset_loader = DatasetLoader()
