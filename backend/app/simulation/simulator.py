"""Simulation - Real-time transaction simulator."""
import asyncio
import random
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, AsyncGenerator
from datetime import datetime, timezone, timedelta
import json
from pathlib import Path

try:
    from sdv.single_table import GaussianCopulaSynthesizer
    from sdv.metadata import Metadata
    SDV_AVAILABLE = True
except ImportError:
    SDV_AVAILABLE = False


class TransactionSimulator:
    ATTACK_SCENARIOS = {
        "NORMAL": {"fraud_boost": 0, "velocity_mult": 1.0, "amount_mult": 1.0},
        "HIGH_VELOCITY": {"fraud_boost": 0.1, "velocity_mult": 5.0, "amount_mult": 1.0},
        "UNUSUAL_AMOUNT": {"fraud_boost": 0.15, "velocity_mult": 1.0, "amount_mult": 5.0},
        "NEW_MERCHANT": {"fraud_boost": 0.1, "velocity_mult": 1.0, "amount_mult": 1.0},
        "NEW_CUSTOMER_MERCHANT_PAIR": {"fraud_boost": 0.12, "velocity_mult": 1.0, "amount_mult": 1.0},
        "ACCOUNT_TAKEOVER": {"fraud_boost": 0.3, "velocity_mult": 3.0, "amount_mult": 2.0},
        "CARD_TESTING": {"fraud_boost": 0.2, "velocity_mult": 10.0, "amount_mult": 0.1},
        "SUSPICIOUS_CHAIN": {"fraud_boost": 0.25, "velocity_mult": 2.0, "amount_mult": 1.5}
    }

    def __init__(self, dataset_name: str = "banksim", speed_multiplier: float = 1.0):
        self.dataset_name = dataset_name
        self.speed_multiplier = speed_multiplier
        self.running = False
        self.paused = False
        self.current_index = 0
        self.df: Optional[pd.DataFrame] = None
        self.scenario = "NORMAL"
        self._listeners: List[asyncio.Queue] = []

    def load_dataset(self, df: pd.DataFrame):
        self.df = df.copy()
        self.current_index = 0

    def set_scenario(self, scenario: str):
        if scenario in self.ATTACK_SCENARIOS:
            self.scenario = scenario

    def add_listener(self, queue: asyncio.Queue):
        self._listeners.append(queue)

    def remove_listener(self, queue: asyncio.Queue):
        if queue in self._listeners:
            self._listeners.remove(queue)

    async def _notify_listeners(self, transaction: Dict):
        for queue in self._listeners:
            try:
                await queue.put(transaction)
            except Exception:
                pass

    async def start(self):
        if self.df is None or self.df.empty:
            return
        self.running = True
        self.paused = False
        base_delay = 1.0 / self.speed_multiplier
        while self.running and self.current_index < len(self.df):
            if self.paused:
                await asyncio.sleep(0.1)
                continue
            row = self.df.iloc[self.current_index]
            transaction = self._process_row(row)
            await self._notify_listeners(transaction)
            self.current_index += 1
            await asyncio.sleep(base_delay)

    def _process_row(self, row: pd.Series) -> Dict:
        scenario_config = self.ATTACK_SCENARIOS.get(self.scenario, self.ATTACK_SCENARIOS["NORMAL"])
        amount = float(row.get("amount", 0))
        if self.scenario == "UNUSUAL_AMOUNT":
            amount *= scenario_config["amount_mult"]
        elif self.scenario == "CARD_TESTING":
            amount *= scenario_config["amount_mult"]
        is_fraud = int(row.get("fraud_label", row.get("fraud", 0)))
        if random.random() < scenario_config["fraud_boost"]:
            is_fraud = 1
        return {
            "transaction_id": str(row.get("transaction_id", f"SIM_{self.current_index}")),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "customer_id": str(row.get("customer_id", row.get("customer", "unknown"))),
            "merchant_id": str(row.get("merchant_id", row.get("merchant", "unknown"))),
            "amount": round(amount, 2),
            "currency": str(row.get("currency", "USD")),
            "category": str(row.get("category", "unknown")),
            "location": str(row.get("location", "unknown")),
            "device": str(row.get("device", "unknown")),
            "customer_age": str(row.get("customer_age", "unknown")),
            "customer_gender": str(row.get("customer_gender", "unknown")),
            "fraud_label": is_fraud,
            "scenario": self.scenario,
            "simulated": True
        }

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def stop(self):
        self.running = False

    def reset(self):
        self.current_index = 0
        self.running = False
        self.paused = False


class SyntheticDataGenerator:
    def __init__(self):
        self.synthesizer = None

    def fit(self, df: pd.DataFrame):
        if not SDV_AVAILABLE:
            return False
        train_df = df.copy()
        for col in train_df.columns:
            if train_df[col].dtype == "object":
                train_df[col] = train_df[col].astype(str)
        metadata = Metadata.detect_from_dataframe(data=train_df, table_name="transactions")
        self.synthesizer = GaussianCopulaSynthesizer(metadata)
        self.synthesizer.fit(train_df)
        return True

    def generate(self, n_samples: int = 1000) -> Optional[pd.DataFrame]:
        if self.synthesizer is None:
            return None
        synthetic = self.synthesizer.sample(num_rows=n_samples)
        synthetic["transaction_id"] = [f"SYN_{i:08d}" for i in range(len(synthetic))]
        synthetic["timestamp"] = pd.date_range(start=datetime.now(timezone.utc), periods=len(synthetic), freq="1min")
        synthetic["fraud_label"] = np.random.choice([0, 1], len(synthetic), p=[0.98, 0.02])
        return synthetic

    def save(self, path: str = "data/synthetic/synthetic_txns.csv"):
        if self.synthesizer is not None:
            synthetic = self.generate(5000)
            if synthetic is not None:
                Path(path).parent.mkdir(parents=True, exist_ok=True)
                synthetic.to_csv(path, index=False)
                return path
        return None
