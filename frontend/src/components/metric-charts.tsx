'use client'

import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ComposedChart,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { ModelMetric } from '@/lib/api'

export function CurveChart({
  title,
  data,
  xKey,
  yKey,
  xLabel,
  yLabel,
  stroke,
}: {
  title: string
  data: Array<Record<string, number>>
  xKey: string
  yKey: string
  xLabel: string
  yLabel: string
  stroke: string
}) {
  return (
    <div className="chart-block">
      <div className="chart-title">
        <strong>{title}</strong>
        <span>{xLabel} vs {yLabel}</span>
      </div>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={data} margin={{ top: 10, right: 16, left: 0, bottom: 10 }}>
          <CartesianGrid stroke="#d8dee8" strokeDasharray="3 3" />
          <XAxis dataKey={xKey} tickFormatter={(value) => Number(value).toFixed(1)} />
          <YAxis domain={[0, 1]} tickFormatter={(value) => Number(value).toFixed(1)} />
          <Tooltip formatter={(value) => Number(value).toFixed(4)} />
          <Line type="monotone" dataKey={yKey} stroke={stroke} strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export function ModelComparisonChart({ rows }: { rows: Array<{ model: string; roc_auc: number; pr_auc: number }> }) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={rows} margin={{ top: 10, right: 16, left: 0, bottom: 20 }}>
        <CartesianGrid stroke="#d8dee8" strokeDasharray="3 3" />
        <XAxis dataKey="model" tick={{ fontSize: 11 }} />
        <YAxis domain={[0, 1]} tickFormatter={(value) => Number(value).toFixed(1)} />
        <Tooltip formatter={(value) => Number(value).toFixed(4)} />
        <Bar dataKey="roc_auc" fill="#2563eb" name="ROC AUC" radius={[4, 4, 0, 0]} />
        <Bar dataKey="pr_auc" fill="#16a34a" name="PR AUC" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}

export function RiskPie({ values }: { values: Array<{ name: string; value: number; color: string }> }) {
  return (
    <ResponsiveContainer width="100%" height={240}>
      <PieChart>
        <Pie data={values} dataKey="value" nameKey="name" innerRadius={62} outerRadius={88} paddingAngle={2}>
          {values.map((entry) => (
            <Cell key={entry.name} fill={entry.color} />
          ))}
        </Pie>
        <Tooltip formatter={(value) => `${value}%`} />
      </PieChart>
    </ResponsiveContainer>
  )
}

export function ConfusionMatrix({ matrix }: { matrix?: number[][] }) {
  const tn = matrix?.[0]?.[0] ?? 0
  const fp = matrix?.[0]?.[1] ?? 0
  const fn = matrix?.[1]?.[0] ?? 0
  const tp = matrix?.[1]?.[1] ?? 0
  return (
    <div className="matrix">
      <div><span>True normal</span><strong>{tn.toLocaleString()}</strong></div>
      <div><span>False alert</span><strong>{fp.toLocaleString()}</strong></div>
      <div><span>Missed fraud</span><strong>{fn.toLocaleString()}</strong></div>
      <div><span>Caught fraud</span><strong>{tp.toLocaleString()}</strong></div>
    </div>
  )
}

export function FeatureImportance({ metric, featureNames = [] }: { metric?: ModelMetric; featureNames?: string[] }) {
  const values = (metric?.feature_importance || [])
    .map((value, index) => ({ feature: featureNames[index] || `Feature ${index + 1}`, value }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 10)

  return (
    <ResponsiveContainer width="100%" height={280}>
      <ComposedChart data={values} layout="vertical" margin={{ top: 10, right: 20, left: 70, bottom: 10 }}>
        <CartesianGrid stroke="#d8dee8" strokeDasharray="3 3" />
        <XAxis type="number" />
        <YAxis dataKey="feature" type="category" width={110} tick={{ fontSize: 11 }} />
        <Tooltip formatter={(value) => Number(value).toFixed(4)} />
        <Area dataKey="value" fill="#bfdbfe" stroke="#2563eb" />
      </ComposedChart>
    </ResponsiveContainer>
  )
}

export function RiskScoreTimeline({ data }: { data: any[] }) {
  if (!data || data.length === 0) return null

  // Ensure data has the correct numeric value for the chart
  const chartData = data.map((d, i) => ({
    time: i,
    score: typeof d.risk_score === 'number' ? d.risk_score : 0,
    level: d.risk_level || 'LOW'
  }))

  return (
    <ResponsiveContainer width="100%" height={200}>
      <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
        <CartesianGrid stroke="#d8dee8" strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey="time" hide />
        <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: '#5f6f86' }} />
        <Tooltip 
          formatter={(value: number) => [`${value} / 100`, 'Risk Score']} 
          labelFormatter={() => ''}
        />
        <Area 
          type="monotone" 
          dataKey="score" 
          stroke="#0f172a" 
          fill="#cbd5e1" 
          fillOpacity={0.4} 
          strokeWidth={2}
          isAnimationActive={false}
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}
