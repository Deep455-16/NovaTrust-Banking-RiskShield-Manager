'use client'

import { useEffect, useState } from 'react'
import { AlertTriangle, RefreshCw } from 'lucide-react'
import { AppShell, EmptyState, Panel, StatTile } from '@/components/app-shell'
import { apiGet, DatasetInfo, num, pct } from '@/lib/api'

export default function DatasetsPage() {
  const [datasets, setDatasets] = useState<DatasetInfo[]>([])
  const [selected, setSelected] = useState('banksim')
  const [detail, setDetail] = useState<any>(null)
  const [preview, setPreview] = useState<any[]>([])
  const [error, setError] = useState('')

  async function load() {
    try {
      const data = await apiGet<{ datasets: DatasetInfo[] }>('/api/v1/datasets')
      setDatasets(data.datasets || [])
      setError('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load datasets')
    }
  }

  useEffect(() => {
    load()
  }, [])

  useEffect(() => {
    async function loadDetail() {
      try {
        const [datasetDetail, sample] = await Promise.all([
          apiGet<any>(`/api/v1/datasets/${selected}`),
          apiGet<{ preview: any[] }>(`/api/v1/datasets/${selected}/preview?rows=12`),
        ])
        setDetail(datasetDetail)
        setPreview(sample.preview || [])
        setError('')
      } catch (err) {
        setDetail(null)
        setPreview([])
        setError(err instanceof Error ? err.message : 'Unable to load dataset details')
      }
    }
    loadDetail()
  }, [selected])

  const active = datasets.find((item) => item.name === selected)
  const columns = preview.length ? Object.keys(preview[0]).slice(0, 8) : []

  return (
    <AppShell title="Datasets" description="Validate local banking datasets before they are used for fraud training, testing, simulation, and scoring.">
      {error ? <section className="notice-band danger"><AlertTriangle size={18} /><span>{error}</span></section> : null}

      <section className="toolbar">
        <label>
          Dataset
          <select value={selected} onChange={(event) => setSelected(event.target.value)}>
            {datasets.map((item) => (
              <option key={item.name} value={item.name}>{item.name}</option>
            ))}
          </select>
        </label>
        <button className="secondary-button" onClick={load}>
          <RefreshCw size={16} />
          Refresh
        </button>
      </section>

      <section className="stat-grid">
        <StatTile label="Rows" value={num(active?.row_count)} detail="Available examples" />
        <StatTile label="Columns" value={num(active?.column_count)} detail="Raw source fields" />
        <StatTile label="Fraud rate" value={pct(active?.fraud_rate)} detail={`${num(active?.fraud_count)} known fraud`} tone="warn" />
        <StatTile label="Status" value={active?.available ? 'Available' : 'Missing'} detail={active?.type || 'Dataset'} tone={active?.available ? 'good' : 'danger'} />
      </section>

      <section className="two-column">
        <Panel title="Dataset Profile">
          {detail ? (
            <div className="definition-list">
              <span>Name</span><strong>{selected}</strong>
              <span>Description</span><strong>{active?.description || 'No description'}</strong>
              <span>Validation</span><strong>{detail.validation?.valid ? 'Valid for use' : 'Review warnings'}</strong>
              <span>Fraud rows</span><strong>{num(detail.fraud_distribution?.fraud)}</strong>
              <span>Normal rows</span><strong>{num(detail.fraud_distribution?.normal)}</strong>
            </div>
          ) : (
            <EmptyState title="No profile loaded" body="Choose an available dataset to inspect its profile." />
          )}
        </Panel>

        <Panel title="Supported Features">
          <div className="tag-list">
            {(active?.compatible_tasks || []).map((task) => <span key={task}>{task.replaceAll('_', ' ')}</span>)}
          </div>
          <div className="column-list">
            {(active?.columns || []).slice(0, 24).map((column) => <code key={column}>{column}</code>)}
          </div>
        </Panel>
      </section>

      <Panel title="Sample Records">
        {preview.length ? (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>{columns.map((column) => <th key={column}>{column}</th>)}</tr>
              </thead>
              <tbody>
                {preview.map((row, index) => (
                  <tr key={index}>{columns.map((column) => <td key={column}>{String(row[column] ?? '')}</td>)}</tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState title="No preview available" body="The selected dataset did not return sample rows." />
        )}
      </Panel>
    </AppShell>
  )
}
