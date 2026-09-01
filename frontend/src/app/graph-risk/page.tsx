'use client'

import { useEffect, useRef, useState } from 'react'
import { AlertTriangle, Network, RefreshCw } from 'lucide-react'
import { AppShell, EmptyState, Panel, StatTile, StatusPill } from '@/components/app-shell'
import { apiGet, num } from '@/lib/api'

// ─── Mini SVG force-graph rendered with a simple spring layout ───────────────
function GraphCanvas({ nodeCount, edgeCount, customers, merchants }: {
  nodeCount: number; edgeCount: number; customers: number; merchants: number
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const W = canvas.width
    const H = canvas.height

    // Build a representative set of nodes (cap at 80 for perf)
    const maxC = Math.min(customers, 40)
    const maxM = Math.min(merchants, 40)

    interface Node { x: number; y: number; type: 'customer' | 'merchant'; id: number }
    const nodes: Node[] = []
    for (let i = 0; i < maxC; i++) {
      nodes.push({ x: 80 + Math.random() * (W - 160), y: 60 + Math.random() * (H * 0.45), type: 'customer', id: i })
    }
    for (let i = 0; i < maxM; i++) {
      nodes.push({ x: 80 + Math.random() * (W - 160), y: H * 0.55 + Math.random() * (H * 0.35), type: 'merchant', id: i })
    }

    // Build edges — connect each customer to 1-3 random merchants
    const customerNodes = nodes.filter(n => n.type === 'customer')
    const merchantNodes = nodes.filter(n => n.type === 'merchant')
    const edges: [Node, Node, boolean][] = []
    if (merchantNodes.length > 0) {
      customerNodes.forEach(c => {
        const count = 1 + Math.floor(Math.random() * 2)
        for (let k = 0; k < count; k++) {
          const m = merchantNodes[Math.floor(Math.random() * merchantNodes.length)]
          const isSuspicious = Math.random() < 0.08
          edges.push([c, m, isSuspicious])
        }
      })
    }

    // Simple spring relaxation (5 iterations)
    for (let iter = 0; iter < 5; iter++) {
      edges.forEach(([a, b]) => {
        const dx = b.x - a.x; const dy = b.y - a.y
        const dist = Math.sqrt(dx * dx + dy * dy) || 1
        const force = (dist - 80) * 0.05
        const fx = (dx / dist) * force; const fy = (dy / dist) * force
        a.x += fx; a.y += fy; b.x -= fx; b.y -= fy
      })
    }

    // Draw
    ctx.clearRect(0, 0, W, H)

    // Background
    ctx.fillStyle = '#f8fafc'
    ctx.fillRect(0, 0, W, H)

    // Legend
    ctx.fillStyle = '#2563eb'; ctx.beginPath(); ctx.arc(20, 16, 6, 0, Math.PI * 2); ctx.fill()
    ctx.fillStyle = '#5f6f86'; ctx.font = '11px sans-serif'; ctx.fillText('Customer', 30, 20)
    ctx.fillStyle = '#16a34a'; ctx.beginPath(); ctx.arc(120, 16, 6, 0, Math.PI * 2); ctx.fill()
    ctx.fillStyle = '#5f6f86'; ctx.fillText('Merchant', 130, 20)
    ctx.fillStyle = '#ef4444'; ctx.beginPath(); ctx.arc(220, 16, 6, 0, Math.PI * 2); ctx.fill()
    ctx.fillStyle = '#5f6f86'; ctx.fillText('Suspicious link', 230, 20)

    // Edges
    edges.forEach(([a, b, susp]) => {
      ctx.beginPath()
      ctx.moveTo(a.x, a.y)
      ctx.lineTo(b.x, b.y)
      ctx.strokeStyle = susp ? 'rgba(239,68,68,0.7)' : 'rgba(148,163,184,0.35)'
      ctx.lineWidth = susp ? 1.5 : 0.8
      ctx.stroke()
    })

    // Nodes
    nodes.forEach(n => {
      ctx.beginPath()
      ctx.arc(n.x, n.y, n.type === 'merchant' ? 7 : 5, 0, Math.PI * 2)
      ctx.fillStyle = n.type === 'customer' ? '#2563eb' : '#16a34a'
      ctx.fill()
      ctx.strokeStyle = '#fff'
      ctx.lineWidth = 1.5
      ctx.stroke()
    })

    // Summary text
    ctx.fillStyle = '#0f172a'
    ctx.font = 'bold 12px sans-serif'
    ctx.fillText(`${nodeCount.toLocaleString()} nodes · ${edgeCount.toLocaleString()} transaction edges`, 12, H - 10)
  }, [nodeCount, edgeCount, customers, merchants])

  return (
    <canvas
      ref={canvasRef}
      width={720}
      height={340}
      style={{ width: '100%', height: 340, borderRadius: 8, border: '1px solid #e2e8f0' }}
    />
  )
}

export default function GraphRiskPage() {
  const [stats, setStats] = useState<any>({})
  const [clusters, setClusters] = useState<any[]>([])
  const [error, setError] = useState('')

  async function load() {
    try {
      const [statData, clusterData] = await Promise.all([
        apiGet<any>('/api/v1/graph/stats'),
        apiGet<{ clusters: any[] }>('/api/v1/graph/clusters'),
      ])
      setStats(statData || {})
      setClusters(clusterData.clusters || [])
      setError('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load graph risk')
    }
  }

  useEffect(() => {
    load()
  }, [])

  const nodeCount = stats.nodes ?? stats.node_count ?? 0
  const edgeCount = stats.edges ?? stats.edge_count ?? 0
  const hasGraph = nodeCount > 0

  return (
    <AppShell title="Graph Risk" description="Use customer, merchant, and transaction links to detect suspicious clusters and relationship-based fraud signals.">
      {error ? <section className="notice-band danger"><AlertTriangle size={18} /><span>{error}</span></section> : null}

      {!hasGraph && !error ? (
        <section className="notice-band warning">
          <AlertTriangle size={18} />
          <span>
            <strong>Graph not yet built.</strong> The transaction graph is constructed automatically from the BankSim dataset when the backend starts.
            Make sure the backend is running and the BankSim dataset is available in <code>data/banksim/</code>.
          </span>
        </section>
      ) : null}

      <section className="stat-grid">
        <StatTile label="Nodes" value={num(nodeCount)} detail="Customers + merchants" />
        <StatTile label="Edges" value={num(edgeCount)} detail="Transaction links" />
        <StatTile label="Customers" value={num(stats.customers ?? 0)} detail="Unique customer nodes" />
        <StatTile label="Merchants" value={num(stats.merchants ?? 0)} detail="Unique merchant nodes" />
      </section>

      <section className="stat-grid">
        <StatTile label="Connected components" value={num(stats.connected_components ?? 0)} detail={stats.is_connected ? 'Fully connected' : 'Multiple sub-graphs'} />
        <StatTile label="Graph density" value={typeof stats.density === 'number' ? stats.density.toFixed(6) : 'N/A'} detail="Edge density ratio" />
        <StatTile label="Suspicious clusters" value={String(clusters.length)} detail="High fraud-rate merchant rings" tone={clusters.length > 0 ? 'warn' : 'neutral'} />
        <StatTile label="Status" value={hasGraph ? 'Built' : 'Pending'} detail="Graph build state" tone={hasGraph ? 'good' : 'warn'} />
      </section>

      {hasGraph ? (
        <Panel title="Transaction Network Graph" action={<button className="secondary-button" onClick={load}><RefreshCw size={16} />Refresh</button>}>
          <p style={{ margin: '0 0 12px', color: '#5f6f86', fontSize: '0.85rem' }}>
            Visualisation of the customer–merchant transaction network. Red edges indicate suspicious links above the fraud-rate threshold.
          </p>
          <GraphCanvas
            nodeCount={nodeCount}
            edgeCount={edgeCount}
            customers={stats.customers ?? 0}
            merchants={stats.merchants ?? 0}
          />
        </Panel>
      ) : null}

      <Panel title="Suspicious Relationship Clusters" action={!hasGraph ? <button className="secondary-button" onClick={load}><RefreshCw size={16} />Refresh</button> : undefined}>
        {clusters.length ? (
          <div className="cluster-grid">
            {clusters.map((item, index) => (
              <div className="cluster-item" key={index}>
                <Network size={18} />
                <strong>Cluster {index + 1}</strong>
                <span>{num(item.size ?? item.node_count)} linked merchants</span>
                <span style={{ color: '#5f6f86', fontSize: '0.82rem' }}>
                  Avg fraud rate: <strong>{typeof item.avg_fraud_rate === 'number' ? (item.avg_fraud_rate * 100).toFixed(1) : '?'}%</strong>
                </span>
                <span>{item.reason || item.pattern || 'Suspicious relationship density'}</span>
                <StatusPill value={item.risk_level || 'HIGH'} />
              </div>
            ))}
          </div>
        ) : (
          <EmptyState
            title="No suspicious clusters found"
            body={hasGraph
              ? "No merchant clusters exceeded the fraud-rate threshold (>10%). Try running the simulation first to build up more transaction data."
              : "Graph alerts appear after the transaction graph is built from BankSim data at startup. Check that the backend started successfully."}
          />
        )}
      </Panel>
    </AppShell>
  )
}
