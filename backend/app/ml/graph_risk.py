"""Graph Risk - Lightweight transaction graph analysis."""
import networkx as nx
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any
from collections import defaultdict


class TransactionGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.customer_nodes: set = set()
        self.merchant_nodes: set = set()

    def build_from_transactions(self, transactions: List[Dict]):
        """Build graph from list of dicts. Handles raw BankSim and normalised column names."""
        self.graph.clear()
        self.customer_nodes.clear()
        self.merchant_nodes.clear()
        for txn in transactions:
            cust_raw = txn.get("customer_id") or txn.get("customer") or txn.get("from_account") or "unknown"
            merch_raw = txn.get("merchant_id") or txn.get("merchant") or txn.get("to_account") or "unknown"
            customer = f"C:{cust_raw}"
            merchant = f"M:{merch_raw}"
            fraud_flag = txn.get("fraud_label") or txn.get("fraud") or txn.get("is_fraud") or 0
            self.customer_nodes.add(customer)
            self.merchant_nodes.add(merchant)
            self.graph.add_node(customer, type="customer")
            self.graph.add_node(merchant, type="merchant")
            self.graph.add_edge(customer, merchant,
                                amount=float(txn.get("amount", 0)),
                                fraud=int(fraud_flag),
                                timestamp=str(txn.get("timestamp", "")))

    def get_customer_risk_signals(self, customer_id: str) -> Dict[str, Any]:
        node = f"C:{customer_id}"
        if node not in self.graph:
            return {}
        edges = list(self.graph.out_edges(node, data=True))
        merchants = set(e[1] for e in edges)
        total_amount = sum(e[2].get("amount", 0) for e in edges)
        fraud_count = sum(1 for e in edges if e[2].get("fraud", 0) == 1)
        merchant_counts = defaultdict(int)
        for e in edges:
            merchant_counts[e[1]] += 1
        high_freq_merchants = [m for m, c in merchant_counts.items() if c > 5]
        return {
            "degree": self.graph.out_degree(node),
            "unique_merchants": len(merchants),
            "total_amount": round(total_amount, 2),
            "fraud_count": fraud_count,
            "fraud_rate": round(fraud_count / max(len(edges), 1), 4),
            "high_frequency_relationships": len(high_freq_merchants),
            "avg_transaction_amount": round(total_amount / max(len(edges), 1), 2)
        }

    def get_merchant_risk_signals(self, merchant_id: str) -> Dict[str, Any]:
        node = f"M:{merchant_id}"
        if node not in self.graph:
            return {}
        edges = list(self.graph.in_edges(node, data=True))
        customers = set(e[0] for e in edges)
        total_amount = sum(e[2].get("amount", 0) for e in edges)
        fraud_count = sum(1 for e in edges if e[2].get("fraud", 0) == 1)
        return {
            "degree": self.graph.in_degree(node),
            "unique_customers": len(customers),
            "total_amount": round(total_amount, 2),
            "fraud_count": fraud_count,
            "fraud_rate": round(fraud_count / max(len(edges), 1), 4),
            "avg_transaction_amount": round(total_amount / max(len(edges), 1), 2)
        }

    def find_suspicious_clusters(self) -> List[Dict[str, Any]]:
        if len(self.graph) == 0:
            return []
        merchant_fraud_rates = {}
        for node in self.merchant_nodes:
            edges = list(self.graph.in_edges(node, data=True))
            if edges:
                fraud_rate = sum(1 for e in edges if e[2].get("fraud", 0) == 1) / len(edges)
                if fraud_rate > 0.1:
                    merchant_fraud_rates[node] = fraud_rate
        clusters = []
        processed = set()
        for merchant in sorted(merchant_fraud_rates.keys(), key=lambda x: merchant_fraud_rates[x], reverse=True):
            if merchant in processed:
                continue
            customers = set(e[0] for e in self.graph.in_edges(merchant, data=True))
            cluster_merchants = {merchant}
            for other in merchant_fraud_rates:
                if other != merchant and other not in processed:
                    other_customers = set(e[0] for e in self.graph.in_edges(other, data=True))
                    if len(customers & other_customers) > 0:
                        cluster_merchants.add(other)
            if len(cluster_merchants) > 1:
                clusters.append({
                    "merchants": list(cluster_merchants),
                    "avg_fraud_rate": round(np.mean([merchant_fraud_rates[m] for m in cluster_merchants]), 4),
                    "size": len(cluster_merchants)
                })
                processed.update(cluster_merchants)
        return clusters

    def get_graph_stats(self) -> Dict[str, Any]:
        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "customers": len(self.customer_nodes),
            "merchants": len(self.merchant_nodes),
            "density": round(nx.density(self.graph), 6) if self.graph.number_of_nodes() > 1 else 0,
            "is_connected": nx.is_weakly_connected(self.graph) if self.graph.number_of_nodes() > 0 else False
        }
