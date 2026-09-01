'use client'

import { useEffect, useState } from 'react'
import { AlertTriangle, RefreshCw } from 'lucide-react'
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { AppShell, EmptyState, Panel, StatTile, StatusPill } from '@/components/app-shell'
import { apiGet, pct } from '@/lib/api'

export default function DriftPage() {
  const [report, setReport] = useState<any>(null)
  const [error, setError] = useState('')

  async function load() {
    try {
      const data = await apiGet<any>('/api/v1/drift/status')
      if (data.error) throw new Error(data.error)
      setReport(data)
      setError('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load drift status')
    }
  }

  useEffect(() => {
    load()
  }, [])

  const features = (report?.feature_reports || []).slice(0, 12).map((item: any) => ({
    feature: item.feature,
    training: item.training_mean,
    streaming: item.streaming_mean,
  }))

  return (
    <AppShell title="Drift Monitor" description="Compare current dataset behavior with the training baseline so model quality issues are visible early.">
      {error ? <section className="notice-band danger"><AlertTriangle size={18} /><span>{error}</span></section> : null}
      <section className="toolbar">
        <button className="secondary-button" onClick={load}><RefreshCw size={16} />Refresh Drift</button>
      </section>
      <section className="stat-grid">
        <StatTile label="Overall status" value={report?.overall_status || 'Unknown'} tone={report?.overall_status === 'STABLE' ? 'good' : 'warn'} />
        <StatTile label="Fraud rate change" value={pct(report?.fraud_rate_drift?.absolute_change)} detail="Current vs training" />
        <StatTile label="Training fraud" value={pct(report?.fraud_rate_drift?.training_rate)} />
        <StatTile label="Current fraud" value={pct(report?.fraud_rate_drift?.current_rate)} tone="warn" />
      </section>
      <Panel title="Feature Drift Means">
        {features.length ? (
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={features} margin={{ top: 10, right: 18, left: 0, bottom: 50 }}>
              <CartesianGrid stroke="#d8dee8" strokeDasharray="3 3" />
              <XAxis dataKey="feature" angle={-30} textAnchor="end" interval={0} tick={{ fontSize: 11 }} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="training" fill="#2563eb" name="Training mean" radius={[4, 4, 0, 0]} />
              <Bar dataKey="streaming" fill="#f97316" name="Current mean" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <EmptyState title="No drift report yet" body="Train a model first so the drift monitor has a baseline." />
        )}
      </Panel>
      <Panel title="Feature Status">
        {(report?.feature_reports || []).length ? (
          <div className="table-wrap">
            <table>
              <thead><tr><th>Feature</th><th>Status</th><th>P value</th><th>Training mean</th><th>Current mean</th></tr></thead>
              <tbody>
                {report.feature_reports.slice(0, 30).map((item: any) => (
                  <tr key={item.feature}>
                    <td><code>{item.feature}</code></td>
                    <td><StatusPill value={item.status} /></td>
                    <td>{Number(item.p_value || 0).toFixed(4)}</td>
                    <td>{Number(item.training_mean || 0).toFixed(4)}</td>
                    <td>{Number(item.streaming_mean || 0).toFixed(4)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
      </Panel>
    </AppShell>
  )
}
