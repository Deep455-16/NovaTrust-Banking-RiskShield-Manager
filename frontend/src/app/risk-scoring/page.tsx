'use client'

import { useState } from 'react'
import { AlertTriangle, Calculator, MessageSquare } from 'lucide-react'
import { AppShell, Panel, StatTile, StatusPill } from '@/components/app-shell'
import { apiPost, pct } from '@/lib/api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'

const starterTransaction = {
  transaction_id: 'manual-001',
  customer_id: 'C1024',
  merchant_id: 'M778',
  amount: 945.25,
  category: 'es_transportation',
  step: 0,
  location: 'UNKNOWN',
  device: 'mobile',
  customer_gender: 'UNKNOWN',
  transaction_velocity: 38,
  amount_deviation: 1850,
  is_first_time_pair: true,
  suspicious_patterns: ['new_merchant', 'amount_spike', 'high_velocity'],
}

function ComponentScoreChart({ scores }: { scores: Record<string, number> }) {
  const data = [
    { name: 'Fraud Prob', value: scores.fraud_probability ?? 0, color: '#dc2626' },
    { name: 'Anomaly', value: scores.anomaly_score ?? 0, color: '#ea580c' },
    { name: 'Velocity', value: scores.velocity_score ?? 0, color: '#ca8a04' },
    { name: 'Amt Dev', value: scores.amount_deviation_score ?? 0, color: '#7c3aed' },
    { name: 'First-time', value: scores.first_time_pair_score ?? 0, color: '#2563eb' },
  ]
  return (
    <div>
      <p style={{ margin: '0 0 10px', color: '#5f6f86', fontSize: '0.88rem' }}>
        Component score breakdown (0–100 per signal)
      </p>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={data} layout="vertical" margin={{ top: 4, right: 30, left: 70, bottom: 4 }}>
          <CartesianGrid stroke="#d8dee8" strokeDasharray="3 3" />
          <XAxis type="number" domain={[0, 100]} tickFormatter={(v) => `${v}`} />
          <YAxis dataKey="name" type="category" width={72} tick={{ fontSize: 11 }} />
          <Tooltip formatter={(v: number) => [`${v.toFixed(1)} / 100`, 'Score']} />
          <Bar dataKey="value" radius={[0, 4, 4, 0]}>
            {data.map((entry) => (
              <Cell key={entry.name} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

function RiskGauge({ score, level }: { score: number; level: string }) {
  const color =
    level === 'CRITICAL' ? '#dc2626' :
    level === 'HIGH' ? '#ea580c' :
    level === 'MEDIUM' ? '#ca8a04' : '#15803d'
  return (
    <div style={{ marginTop: 16 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6, fontSize: '0.85rem', color: '#5f6f86' }}>
        <span>Overall Risk Score</span>
        <strong style={{ color, fontSize: '1.1rem' }}>{score} / 100</strong>
      </div>
      <div style={{ height: 12, background: '#eef3f8', borderRadius: 8, overflow: 'hidden', border: '1px solid #d8dee8' }}>
        <div style={{ width: `${score}%`, height: '100%', background: color, borderRadius: 8, transition: 'width 0.6s ease' }} />
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: '#5f6f86', marginTop: 4 }}>
        <span>LOW</span><span>MEDIUM</span><span>HIGH</span><span>CRITICAL</span>
      </div>
    </div>
  )
}

export default function RiskScoringPage() {
  const [jsonText, setJsonText] = useState(JSON.stringify(starterTransaction, null, 2))
  const [result, setResult] = useState<any>(null)
  const [explanation, setExplanation] = useState<any>(null)
  const [error, setError] = useState('')

  async function score() {
    setError('')
    setExplanation(null)
    try {
      const transaction = JSON.parse(jsonText)
      const data = await apiPost<any>('/api/v1/risk/score', transaction)
      if (data.error) throw new Error(data.error)
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to score transaction')
    }
  }

  async function explain() {
    if (!result) return
    setError('')
    try {
      setExplanation(await apiPost<any>('/api/v1/copilot/explain', result))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to explain transaction')
    }
  }

  const riskTone = result?.risk_level === 'CRITICAL' || result?.risk_level === 'HIGH' ? 'danger' : 'warn'

  return (
    <AppShell title="Risk Scoring" description="Submit a transaction payload and inspect fraud probability, anomaly score, risk factors, and the policy decision.">
      {error ? <section className="notice-band danger"><AlertTriangle size={18} /><span>{error}</span></section> : null}

      <section className="two-column">
        <Panel title="Transaction Payload" action={<button onClick={score}><Calculator size={16} />Score</button>}>
          <p style={{ margin: '0 0 10px', color: '#5f6f86', fontSize: '0.85rem' }}>
            All fields are optional — safe defaults are injected automatically. Add <code>transaction_velocity</code>, <code>amount_deviation</code>, and <code>suspicious_patterns</code> to drive higher risk scores without a trained model.
          </p>
          <textarea className="json-editor" value={jsonText} onChange={(event) => setJsonText(event.target.value)} spellCheck={false} />
        </Panel>

        <Panel title="Decision Summary" action={<button className="secondary-button" onClick={explain} disabled={!result}><MessageSquare size={16} />Explain</button>}>
          {result ? (
            <>
              <section className="stat-grid compact">
                <StatTile label="Fraud probability" value={pct(result.fraud_probability)} tone="warn" />
                <StatTile label="Anomaly score" value={Number(result.anomaly_score || 0).toFixed(3)} />
                <StatTile label="Risk score" value={`${result.risk_score || 0}/100`} tone={riskTone} />
                <StatTile label="Decision" value={result.decision || 'ALLOW'} tone={result.decision === 'BLOCK' ? 'danger' : result.decision === 'REVIEW' ? 'warn' : 'good'} />
              </section>

              <div className="decision-line">
                <span>Risk level</span>
                <StatusPill value={result.risk_level} />
                <span style={{ color: '#5f6f86', fontSize: '0.82rem' }}>Policy: {result.policy_name || 'default'}</span>
              </div>

              {result.risk_score !== undefined && (
                <RiskGauge score={result.risk_score} level={result.risk_level} />
              )}

              {result.component_scores && (
                <div style={{ marginTop: 20 }}>
                  <ComponentScoreChart scores={result.component_scores} />
                </div>
              )}

              {(result.risk_factors || []).length > 0 && (
                <div style={{ marginTop: 14 }}>
                  <p style={{ margin: '0 0 8px', fontSize: '0.82rem', color: '#5f6f86', textTransform: 'uppercase', fontWeight: 800 }}>Risk Factors</p>
                  <div className="tag-list">
                    {(result.risk_factors || []).map((item: string) => <span key={item}>{item}</span>)}
                  </div>
                </div>
              )}
            </>
          ) : (
            <p className="muted-copy">Score the sample payload or paste your own normalized transaction. The starter payload has high velocity and amount deviation to demonstrate a non-trivial risk score even before model training.</p>
          )}
        </Panel>
      </section>

      {explanation ? (
        <Panel title="Analyst Explanation">
          <p className="large-copy">{explanation.explanation}</p>
          <pre className="summary-box">{explanation.investigation_summary}</pre>
          <div className="question-list">
            {(explanation.analyst_questions || []).map((item: string) => <span key={item}>{item}</span>)}
          </div>
        </Panel>
      ) : null}
    </AppShell>
  )
}
