'use client'

import { useEffect, useState } from 'react'
import { AlertTriangle, RefreshCw } from 'lucide-react'
import { AppShell, EmptyState, Panel, StatTile, StatusPill } from '@/components/app-shell'
import { apiGet, num } from '@/lib/api'

export default function InvestigationsPage() {
  const [cases, setCases] = useState<any[]>([])
  const [stats, setStats] = useState<any>({})
  const [status, setStatus] = useState('')
  const [error, setError] = useState('')

  async function load() {
    try {
      const suffix = status ? `?status=${encodeURIComponent(status)}` : ''
      const [caseData, statData] = await Promise.all([
        apiGet<{ cases: any[] }>(`/api/v1/investigations${suffix}`),
        apiGet<any>('/api/v1/investigations/stats'),
      ])
      setCases(caseData.cases || [])
      setStats(statData || {})
      setError('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load investigations')
    }
  }

  useEffect(() => {
    load()
  }, [status])

  return (
    <AppShell title="Investigations" description="Track risk cases that need analyst review and understand how much fraud work is currently open.">
      {error ? <section className="notice-band danger"><AlertTriangle size={18} /><span>{error}</span></section> : null}
      <section className="toolbar">
        <label>Status<select value={status} onChange={(event) => setStatus(event.target.value)}><option value="">All</option><option value="OPEN">Open</option><option value="IN_PROGRESS">In progress</option><option value="CLOSED">Closed</option></select></label>
        <button className="secondary-button" onClick={load}><RefreshCw size={16} />Refresh</button>
      </section>
      <section className="stat-grid">
        <StatTile label="Total cases" value={num(stats.total_cases ?? cases.length)} />
        <StatTile label="Open" value={num(stats.open_cases ?? 0)} tone="warn" />
        <StatTile label="Escalated" value={num(stats.escalated_cases ?? 0)} tone="danger" />
        <StatTile label="Resolved" value={num(stats.resolved_cases ?? 0)} tone="good" />
      </section>
      <Panel title="Case Queue">
        {cases.length ? (
          <div className="table-wrap">
            <table>
              <thead><tr><th>Case</th><th>Transaction</th><th>Status</th><th>Risk</th><th>Score</th><th>Assigned</th><th>Created</th></tr></thead>
              <tbody>
                {cases.map((item) => (
                  <tr key={item.id}>
                    <td><code>{item.id}</code></td>
                    <td>{item.transaction_id}</td>
                    <td>{item.status}</td>
                    <td><StatusPill value={item.risk_level} /></td>
                    <td>{item.risk_score}</td>
                    <td>{item.assigned_to || 'Unassigned'}</td>
                    <td>{item.created_at ? new Date(item.created_at).toLocaleString() : 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState title="No cases found" body="Cases appear here when transactions are escalated for review." />
        )}
      </Panel>
    </AppShell>
  )
}
