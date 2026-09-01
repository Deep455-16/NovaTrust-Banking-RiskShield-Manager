'use client'

import { useEffect, useRef, useState } from 'react'
import { AlertTriangle, Pause, Play, Square } from 'lucide-react'
import { AppShell, EmptyState, Panel, StatTile, StatusPill } from '@/components/app-shell'
import { RiskScoreTimeline } from '@/components/metric-charts'
import { apiGet, apiPost, buildStreamUrl, num, pct, Transaction } from '@/lib/api'
import { datasetOptions, scenarioOptions } from '@/lib/domain'

type SimulationStatus = {
  running: boolean
  paused: boolean
  current_index: number
  total_rows: number
  scenario: string
  dataset: string
}

export default function SimulationPage() {
  const [dataset, setDataset] = useState('banksim')
  const [scenario, setScenario] = useState('NORMAL')
  const [speed, setSpeed] = useState(5)
  const [status, setStatus] = useState<SimulationStatus | null>(null)
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [connected, setConnected] = useState(false)
  const [error, setError] = useState('')
  const wsRef = useRef<WebSocket | null>(null)

  async function loadStatus() {
    const data = await apiGet<SimulationStatus>('/api/v1/simulation/status')
    setStatus(data)
  }

  useEffect(() => {
    loadStatus().catch((err) => setError(err instanceof Error ? err.message : 'Unable to load simulation status'))
    const timer = window.setInterval(() => {
      loadStatus().catch(() => undefined)
    }, 5000)
    return () => {
      window.clearInterval(timer)
      wsRef.current?.close()
    }
  }, [])

  function connectStream() {
    wsRef.current?.close()
    const ws = new WebSocket(buildStreamUrl())
    wsRef.current = ws
    ws.onopen = () => setConnected(true)
    ws.onclose = () => setConnected(false)
    ws.onerror = () => setError('Transaction stream could not connect. Confirm the backend is running and you are signed in.')
    ws.onmessage = (event) => {
      const item = JSON.parse(event.data) as Transaction
      if (item.type !== 'heartbeat') setTransactions((current) => [item, ...current].slice(0, 80))
    }
  }

  async function control(action: 'start' | 'pause' | 'resume' | 'stop') {
    setError('')
    try {
      const result = await apiPost<any>('/api/v1/simulation/control', { action, dataset, speed, scenario })
      if (result.error) throw new Error(result.error)
      if (action === 'start' || action === 'resume') connectStream()
      if (action === 'stop') {
        wsRef.current?.close()
        setConnected(false)
      }
      await loadStatus()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Simulation action failed')
    }
  }

  const progress = status?.total_rows ? status.current_index / status.total_rows : 0
  const highRiskCount = transactions.filter((item) => ['HIGH', 'CRITICAL'].includes(String(item.risk_level))).length

  return (
    <AppShell title="Live Simulation" description="Replay local banking datasets through the fraud model, anomaly detector, policy engine, and live transaction stream.">
      {error ? <section className="notice-band danger"><AlertTriangle size={18} /><span>{error}</span></section> : null}

      <section className="toolbar">
        <label>Dataset<select value={dataset} onChange={(event) => setDataset(event.target.value)}>{datasetOptions.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}</select></label>
        <label>Scenario<select value={scenario} onChange={(event) => setScenario(event.target.value)}>{scenarioOptions.map((item) => <option key={item} value={item}>{item.replaceAll('_', ' ')}</option>)}</select></label>
        <label>Speed<select value={speed} onChange={(event) => setSpeed(Number(event.target.value))}>{[1, 5, 10, 25, 50].map((item) => <option key={item} value={item}>{item}x</option>)}</select></label>
        {!status?.running ? (
          <button onClick={() => control('start')}><Play size={16} />Start</button>
        ) : status.paused ? (
          <button onClick={() => control('resume')}><Play size={16} />Resume</button>
        ) : (
          <button className="secondary-button" onClick={() => control('pause')}><Pause size={16} />Pause</button>
        )}
        <button className="danger-button" onClick={() => control('stop')}><Square size={16} />Stop</button>
      </section>

      <section className="stat-grid">
        <StatTile label="Stream" value={connected ? 'Connected' : 'Offline'} detail="WebSocket transaction feed" tone={connected ? 'good' : 'warn'} />
        <StatTile label="Progress" value={pct(progress)} detail={`${num(status?.current_index)} of ${num(status?.total_rows)}`} />
        <StatTile label="High-risk seen" value={String(highRiskCount)} detail="Current screen buffer" tone="warn" />
        <StatTile label="Scenario" value={status?.scenario || scenario} detail={status?.dataset || dataset} />
      </section>

      <Panel title="Live Transaction Decisions">
        {transactions.length ? (
          <>
            <div style={{ marginBottom: 20 }}>
              <p style={{ margin: '0 0 10px', color: '#5f6f86', fontSize: '0.85rem' }}>Rolling Risk Score Timeline</p>
              <RiskScoreTimeline data={transactions.slice().reverse()} />
            </div>
            <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Transaction</th><th>Customer</th><th>Merchant</th><th>Amount</th><th>Fraud prob.</th><th>Anomaly</th><th>Risk</th><th>Decision</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((item, index) => (
                  <tr key={`${item.transaction_id || index}`}>
                    <td><code>{String(item.transaction_id || '').slice(-10) || 'streamed'}</code></td>
                    <td>{item.customer_id || 'Unknown'}</td>
                    <td>{item.merchant_id || 'Unknown'}</td>
                    <td>{typeof item.amount === 'number' ? `$${item.amount.toFixed(2)}` : 'N/A'}</td>
                    <td>{pct(item.fraud_probability)}</td>
                    <td>{typeof item.anomaly_score === 'number' ? item.anomaly_score.toFixed(3) : 'N/A'}</td>
                    <td><StatusPill value={item.risk_level} /></td>
                    <td>{item.decision || 'ALLOW'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          </>
        ) : (
          <EmptyState title="No stream records yet" body="Start the simulation to replay dataset transactions through the backend." />
        )}
      </Panel>
    </AppShell>
  )
}
