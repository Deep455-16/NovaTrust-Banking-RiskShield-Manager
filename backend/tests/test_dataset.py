import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.data.dataset_loader import DatasetLoader
from app.data.data_validator import DataValidator
from app.data.preprocessor import TransactionPreprocessor


def test_dataset_loading():
    loader = DatasetLoader()
    df = loader.load_dataset("banksim", normalize=False)
    assert df is not None, "BankSim dataset should be available"
    assert len(df) > 0
    assert "fraud" in df.columns


def test_schema_normalization():
    loader = DatasetLoader()
    df = loader.load_dataset("banksim", normalize=True)
    assert df is not None
    assert "transaction_id" in df.columns
    assert "customer_id" in df.columns
    assert "fraud_label" in df.columns


def test_data_validation():
    loader = DatasetLoader()
    df = loader.load_dataset("banksim", normalize=False)
    validator = DataValidator()
    result = validator.validate_dataset(df, "banksim")
    assert result["valid"] is True


def test_feature_engineering():
    loader = DatasetLoader()
    df = loader.load_dataset("banksim", normalize=True)
    assert df is not None
    preprocessor = TransactionPreprocessor()
    processed, features = preprocessor.prepare_features(df, fit=True)
    assert len(features) > 0
    assert "amount_zscore_24h" in processed.columns


def test_temporal_leakage_prevention():
    loader = DatasetLoader()
    df = loader.load_dataset("banksim", normalize=True)
    assert df is not None
    preprocessor = TransactionPreprocessor()
    processed, _ = preprocessor.prepare_features(df, fit=True)
    first_txns = processed.groupby("customer_id").first()
    assert (first_txns["is_first_time_pair"] == 1).all()
    assert (first_txns["merchant_occurrences"] == 0).all()
