'use client'

import { useEffect, useMemo, useState } from 'react'
import Link from 'next/link'
import { AlertTriangle, ArrowRight, CheckCircle2, ShieldAlert } from 'lucide-react'
import { AppShell, EmptyState, Panel, StatTile } from '@/components/app-shell'
import { ModelComparisonChart, RiskPie } from '@/components/metric-charts'
import { apiGet, DatasetInfo, ModelMetric, num, pct } from '@/lib/api'
import { riskColors } from '@/lib/domain'

type Health = {
  status: string
  models_loaded: string[]
  datasets_available: string[]
  simulation_running: boolean
}

export default function OverviewPage() {
  const [health, setHealth] = useState<Health | null>(null)
  const [datasets, setDatasets] = useState<DatasetInfo[]>([])
  const [metrics, setMetrics] = useState<Record<string, ModelMetric>>({})
  const [error, setError] = useState('')

  useEffect(() => {
    async function load() {
      try {
        const [healthData, datasetData, metricData] = await Promise.all([
          apiGet<Health>('/api/v1/health'),
          apiGet<{ datasets: DatasetInfo[] }>('/api/v1/datasets'),
          apiGet<Record<string, ModelMetric>>('/api/v1/models/metrics'),
        ])
        setHealth(healthData)
        setDatasets(datasetData.datasets || [])
        setMetrics(metricData || {})
        setError('')
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unable to load overview')
      }
    }

    load()
    const timer = window.setInterval(load, 10000)
    return () => window.clearInterval(timer)
  }, [])

  const comparison = useMemo(
    () =>
      Object.entries(metrics)
        .filter(([, metric]) => typeof metric.roc_auc === 'number')
        .map(([model, metric]) => ({
          model,
          roc_auc: metric.roc_auc || 0,
          pr_auc: metric.pr_auc || 0,
        })),
    [metrics],
  )

  const fraudRows = datasets.filter((item) => item.compatible_tasks?.includes('fraud_detection'))
  const rows = datasets.reduce((sum, item) => sum + (item.row_count || 0), 0)
  const fraud = datasets.reduce((sum, item) => sum + (item.fraud_count || 0), 0)
  const loadedModels = health?.models_loaded?.length || Object.keys(metrics).length

  return (
    <AppShell
      title="Risk Operations Overview"
      description="Monitor dataset-backed fraud detection, simulation health, model quality, and operational controls from one place."
    >
      {error ? (
        <section className="notice-band danger">
          <AlertTriangle size={18} />
          <span>{error}</span>
        </section>
      ) : null}

      <section className="notice-band">
        <CheckCircle2 size={18} />
        <strong>Simulation mode active.</strong>
        <span>Bank account linking is represented by local datasets until live-bank integrations are enabled.</span>
      </section>

      <section className="stat-grid">
        <StatTile label="Available datasets" value={String(health?.datasets_available?.length || datasets.length)} detail={`${fraudRows.length} fraud-ready`} />
        <StatTile label="Dataset rows" value={num(rows)} detail="Used for train/test evaluation" />
        <StatTile label="Known fraud rows" value={num(fraud)} detail={pct(rows ? fraud / rows : 0)} tone="warn" />
        <StatTile label="Models loaded" value={String(loadedModels)} detail={health?.simulation_running ? 'Simulation running' : 'Ready'} tone="good" />
      </section>

      <section className="feature-grid">
        {[
          ['Datasets', 'Inspect source columns, fraud distribution, validation, and sample records.', '/datasets'],
          ['Model Training', 'Train fraud models and review ROC, precision-recall, AUC, and confusion matrix.', '/training'],
          ['Live Simulation', 'Replay transaction datasets through the risk engine and WebSocket stream.', '/simulation'],
          ['Risk Scoring', 'Score an individual transaction and inspect the attack/fraud decision.', '/risk-scoring'],
          ['Investigations', 'Review generated cases and analyst workflow status.', '/investigations'],
          ['Qwen Copilot', 'Ask the local qwen2.5:3b model for analyst-grade risk explanations.', '/copilot'],
        ].map(([title, body, href]) => (
          <Link className="feature-link" href={href} key={href}>
            <div>
              <strong>{title}</strong>
              <span>{body}</span>
            </div>
            <ArrowRight size={18} />
          </Link>
        ))}
      </section>

      <section className="two-column">
        <Panel title="Model Quality">
          {comparison.length ? (
            <ModelComparisonChart rows={comparison} />
          ) : (
            <EmptyState title="No evaluated metrics yet" body="Open Model Training and run a dataset test to populate this chart." />
          )}
        </Panel>

        <Panel title="Risk Mix">
          <RiskPie
            values={[
              { name: 'Low', value: 57, color: riskColors.LOW },
              { name: 'Medium', value: 24, color: riskColors.MEDIUM },
              { name: 'High', value: 13, color: riskColors.HIGH },
              { name: 'Critical', value: 6, color: riskColors.CRITICAL },
            ]}
          />
          <div className="legend-list">
            {['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'].map((level) => (
              <span key={level}>
                <i style={{ backgroundColor: riskColors[level as keyof typeof riskColors] }} />
                {level}
              </span>
            ))}
          </div>
        </Panel>
      </section>

      <Panel title="Attack And Fraud Monitoring Scope">
        <div className="scope-grid">
          {[
            ['Account takeover', 'Velocity spikes, unfamiliar merchants, abnormal amount changes'],
            ['Card testing', 'Repeated low-value attempts, merchant bursts, fast retries'],
            ['Synthetic identity risk', 'Sparse customer history, unusual customer-merchant graph links'],
            ['Policy violations', 'Risk thresholds, fraud probability, review and block rules'],
          ].map(([title, body]) => (
            <div key={title} className="scope-item">
              <ShieldAlert size={18} />
              <strong>{title}</strong>
              <span>{body}</span>
            </div>
          ))}
        </div>
      </Panel>
    </AppShell>
  )
}
