export interface Transaction {
  transaction_id: string
  timestamp: string
  customer_id: string
  merchant_id: string
  amount: number
  currency: string
  category: string
  fraud_probability?: number
  anomaly_score?: number
  risk_score?: number
  risk_level?: string
  decision?: string
}

export interface RiskScore {
  risk_score: number
  risk_level: string
  risk_factors: string[]
  component_scores: Record<string, number>
}

export interface ModelMetrics {
  model: string
  roc_auc: number
  pr_auc: number
  precision: number
  recall: number
  f1: number
}
