'use client'

import { useEffect, useMemo, useState } from 'react'
import { AlertTriangle, Brain, Play } from 'lucide-react'
import { AppShell, EmptyState, Panel, StatTile } from '@/components/app-shell'
import { ConfusionMatrix, CurveChart, FeatureImportance, ModelComparisonChart } from '@/components/metric-charts'
import { apiGet, apiPost, ModelMetric, pct } from '@/lib/api'
import { datasetOptions, modelOptions } from '@/lib/domain'

function rocData(metric?: ModelMetric) {
  const fpr = metric?.roc_curve?.fpr || []
  const tpr = metric?.roc_curve?.tpr || []
  return fpr.map((value, index) => ({ fpr: value, tpr: tpr[index] ?? 0 }))
}

function prData(metric?: ModelMetric) {
  const precision = metric?.pr_curve?.precision || []
  const recall = metric?.pr_curve?.recall || []
  return precision.map((value, index) => ({ precision: value, recall: recall[index] ?? 0 }))
}

export default function TrainingPage() {
  const [dataset, setDataset] = useState('banksim')
  const [model, setModel] = useState('weighted_lightgbm')
  const [metrics, setMetrics] = useState<Record<string, ModelMetric>>({})
  const [activeModel, setActiveModel] = useState('weighted_lightgbm')
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  async function refresh() {
    const data = await apiGet<Record<string, ModelMetric>>('/api/v1/models/metrics')
    setMetrics(data || {})
    if (!data[activeModel]) {
      const first = Object.keys(data)[0]
      if (first) setActiveModel(first)
    }
  }

  useEffect(() => {
    refresh().catch((err) => setError(err instanceof Error ? err.message : 'Unable to load metrics'))
  }, [])

  async function train() {
    setBusy(true)
    setError('')
    setMessage('')
    try {
      const result = await apiPost<any>(`/api/v1/models/train?model_name=${encodeURIComponent(model)}`, { dataset })
      if (result.error) throw new Error(result.error)
      setMessage(`Training finished for ${model} on ${dataset}. Metrics were evaluated on the test split.`)
      setActiveModel(model)
      await refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Training failed')
    } finally {
      setBusy(false)
    }
  }

  const activeMetric = metrics[activeModel]
  const comparison = useMemo(
    () =>
      Object.entries(metrics)
        .filter(([, metric]) => typeof metric.roc_auc === 'number')
        .map(([name, metric]) => ({ model: name, roc_auc: metric.roc_auc || 0, pr_auc: metric.pr_auc || 0 })),
    [metrics],
  )

  return (
    <AppShell
      title="Model Training"
      description="Train and test fraud-detection models against local datasets, then review ROC and precision-recall performance."
    >
      {error ? <section className="notice-band danger"><AlertTriangle size={18} /><span>{error}</span></section> : null}
      {message ? <section className="notice-band"><Brain size={18} /><span>{message}</span></section> : null}

      <section className="toolbar">
        <label>
          Dataset
          <select value={dataset} onChange={(event) => setDataset(event.target.value)}>
            {datasetOptions.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}
          </select>
        </label>
        <label>
          Model
          <select value={model} onChange={(event) => setModel(event.target.value)}>
            {modelOptions.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}
          </select>
        </label>
        <button onClick={train} disabled={busy}>
          <Play size={16} />
          {busy ? 'Training' : 'Train And Test'}
        </button>
      </section>

      <section className="tab-row" aria-label="Evaluated models">
        {Object.keys(metrics).map((name) => (
          <button key={name} className={activeModel === name ? 'active' : ''} onClick={() => setActiveModel(name)}>{name}</button>
        ))}
      </section>

      <section className="stat-grid">
        <StatTile label="ROC AUC" value={pct(activeMetric?.roc_auc, 2)} detail="Fraud ranking quality" tone="good" />
        <StatTile label="PR AUC" value={pct(activeMetric?.pr_auc, 2)} detail="Precision-recall area" tone="good" />
        <StatTile label="Precision" value={pct(activeMetric?.precision, 2)} detail="Alerts that are fraud" />
        <StatTile label="Recall" value={pct(activeMetric?.recall, 2)} detail="Fraud caught by model" tone="warn" />
      </section>

      <section className="two-column">
        <Panel title="ROC Curve">
          {rocData(activeMetric).length ? (
            <CurveChart title={activeModel} data={rocData(activeMetric)} xKey="fpr" yKey="tpr" xLabel="FPR" yLabel="TPR" stroke="#2563eb" />
          ) : (
            <EmptyState title="ROC curve unavailable" body="Run training on a fraud dataset to generate curve points." />
          )}
        </Panel>
        <Panel title="Precision-Recall Curve">
          {prData(activeMetric).length ? (
            <CurveChart title={activeModel} data={prData(activeMetric)} xKey="recall" yKey="precision" xLabel="Recall" yLabel="Precision" stroke="#16a34a" />
          ) : (
            <EmptyState title="Precision-recall unavailable" body="Run training to evaluate fraud probabilities on the test split." />
          )}
        </Panel>
      </section>

      <section className="two-column">
        <Panel title="Confusion Matrix">
          <ConfusionMatrix matrix={activeMetric?.confusion_matrix} />
        </Panel>
        <Panel title="Model Comparison">
          {comparison.length ? <ModelComparisonChart rows={comparison} /> : <EmptyState title="No comparison yet" body="Train at least one model to compare AUC scores." />}
        </Panel>
      </section>

      <Panel title="Feature Importance">
        <FeatureImportance metric={activeMetric} />
      </Panel>
    </AppShell>
  )
}
