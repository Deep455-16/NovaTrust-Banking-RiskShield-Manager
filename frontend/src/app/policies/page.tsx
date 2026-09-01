'use client'

import { useEffect, useState } from 'react'
import { AlertTriangle, RefreshCw } from 'lucide-react'
import { AppShell, EmptyState, Panel, StatusPill } from '@/components/app-shell'
import { apiGet } from '@/lib/api'

export default function PoliciesPage() {
  const [policies, setPolicies] = useState<any[]>([])
  const [error, setError] = useState('')

  async function load() {
    try {
      const data = await apiGet<{ policies: any[] }>('/api/v1/policies')
      setPolicies(data.policies || [])
      setError('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load policies')
    }
  }

  useEffect(() => {
    load()
  }, [])

  return (
    <AppShell title="Policies" description="Review decision rules that convert model risk into allow, review, block, or escalation actions.">
      {error ? <section className="notice-band danger"><AlertTriangle size={18} /><span>{error}</span></section> : null}
      <Panel title="Policy Rules" action={<button className="secondary-button" onClick={load}><RefreshCw size={16} />Refresh</button>}>
        {policies.length ? (
          <div className="table-wrap">
            <table>
              <thead><tr><th>Name</th><th>Condition</th><th>Action</th><th>Priority</th><th>Status</th></tr></thead>
              <tbody>
                {policies.map((item) => (
                  <tr key={item.name}>
                    <td><strong>{item.name}</strong></td>
                    <td><code>{item.condition}</code></td>
                    <td>{item.action}</td>
                    <td>{item.priority}</td>
                    <td><StatusPill value={item.enabled ? 'ENABLED' : 'DISABLED'} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState title="No policies returned" body="The policy engine did not return configured rules." />
        )}
      </Panel>
    </AppShell>
  )
}
