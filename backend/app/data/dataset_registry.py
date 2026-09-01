"""Dataset Registry - Central registry for all datasets."""
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd


def get_project_root() -> Path:
    """Find project root by looking for data/ directory."""
    current = Path.cwd()
    for path in [current] + list(current.parents):
        if (path / "data" / "banksim").exists():
            return path
    env_dir = os.environ.get("RISKSHIELD_DATA_DIR")
    if env_dir:
        return Path(env_dir)
    return current.parent if (current / "backend").exists() else current


PROJECT_ROOT = get_project_root()
DATA_DIR = PROJECT_ROOT / "data"

DATASETS: Dict[str, Dict[str, Any]] = {
    "banksim": {
        "path": DATA_DIR / "banksim",
        "type": "fraud_detection",
        "label_column": "fraud",
        "temporal_column": "step",
        "description": "BankSim synthetic banking transaction dataset",
        "compatible_tasks": ["fraud_detection", "risk_scoring", "anomaly_detection", "graph_analysis"]
    },
    "sfindset": {
        "path": DATA_DIR / "sfindset",
        "type": "financial_crime",
        "label_column": "is_fraud",
        "temporal_column": "timestamp",
        "description": "SFinDSet financial crime detection dataset",
        "compatible_tasks": ["fraud_detection", "risk_scoring", "anomaly_detection"]
    },
    "bank_marketing": {
        "path": DATA_DIR / "bank_marketing",
        "type": "banking",
        "label_column": "y",
        "temporal_column": None,
        "description": "Bank Marketing campaign dataset",
        "compatible_tasks": ["marketing", "customer_segmentation"]
    },
    "global_bank": {
        "path": DATA_DIR / "global_bank",
        "type": "banking",
        "label_column": "is_fraud",
        "temporal_column": "date",
        "description": "Global Banking transaction dataset",
        "compatible_tasks": ["fraud_detection", "risk_scoring", "anomaly_detection"]
    },
    "synthetic": {
        "path": DATA_DIR / "synthetic",
        "type": "synthetic",
        "label_column": "fraud_label",
        "temporal_column": "timestamp",
        "description": "SDV-generated synthetic transactions",
        "compatible_tasks": ["fraud_detection", "risk_scoring", "anomaly_detection", "simulation"]
    }
}


def discover_files(dataset_path: Path) -> List[Path]:
    if not dataset_path.exists():
        return []
    files = []
    for ext in ["*.csv", "*.json", "*.parquet", "*.jsonl"]:
        files.extend(dataset_path.glob(ext))
    return sorted(files)


def get_dataset_info(dataset_name: str) -> Optional[Dict[str, Any]]:
    if dataset_name not in DATASETS:
        return None
    info = DATASETS[dataset_name].copy()
    info["name"] = dataset_name
    info["files"] = [str(f.name) for f in discover_files(info["path"])]
    info["available"] = len(info["files"]) > 0
    info["row_count"] = 0
    info["column_count"] = 0
    if info["available"]:
        try:
            full_files = discover_files(info["path"])
            csv_files = [f for f in full_files if f.suffix == ".csv"]
            first_file = csv_files[0] if csv_files else full_files[0]
            df = pd.read_csv(first_file)
            info["row_count"] = len(df)
            info["column_count"] = len(df.columns)
            info["columns"] = list(df.columns)
            if info.get("label_column") and info["label_column"] in df.columns:
                col = df[info["label_column"]]
                if col.dtype in ['int64', 'int32', 'float64', 'float32', 'bool', 'int8', 'uint8']:
                    fraud_series = col.fillna(0).astype(float)
                    info["fraud_count"] = int(fraud_series.sum())
                    info["fraud_rate"] = float(fraud_series.mean())
                elif col.dtype == object:
                    # Handle yes/no or 1/0 as strings (e.g. bank_marketing 'y' column)
                    fraud_series = col.astype(str).str.strip().str.lower().isin(["yes", "1", "true", "fraud"]).astype(int)
                    info["fraud_count"] = int(fraud_series.sum())
                    info["fraud_rate"] = float(fraud_series.mean())
                else:
                    info["fraud_count"] = 0
                    info["fraud_rate"] = 0.0
        except Exception as e:
            info["error"] = str(e)
    return info


def list_datasets(task_type: Optional[str] = None) -> List[Dict[str, Any]]:
    results = []
    for name, config in DATASETS.items():
        if task_type and task_type not in config.get("compatible_tasks", []):
            continue
        info = get_dataset_info(name)
        if info:
            results.append(info)
    return results


def get_compatible_datasets(task_type: str) -> List[str]:
    return [
        name for name, config in DATASETS.items()
        if task_type in config.get("compatible_tasks", [])
    ]
