'use client'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'
const TOKEN_KEY = 'riskshield_token'
const USER_KEY = 'riskshield_user'

export type ApiUser = {
  username: string
  role: string
}

export type DatasetInfo = {
  name?: string
  description?: string
  type?: string
  available?: boolean
  row_count?: number
  column_count?: number
  fraud_count?: number
  fraud_rate?: number
  compatible_tasks?: string[]
  columns?: string[]
  files?: string[]
}

export type ModelMetric = {
  model?: string
  roc_auc?: number
  pr_auc?: number
  precision?: number
  recall?: number
  f1?: number
  precision_at_k?: number
  'recall_at_0.1_fpr'?: number
  roc_curve?: { fpr: number[]; tpr: number[] }
  pr_curve?: { precision: number[]; recall: number[] }
  confusion_matrix?: number[][]
  feature_importance?: number[]
  status?: string
  error?: string
}

export type Transaction = {
  transaction_id?: string
  customer_id?: string
  merchant_id?: string
  amount?: number
  fraud_probability?: number
  anomaly_score?: number
  risk_score?: number
  risk_level?: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' | string
  decision?: string
  type?: string
  error?: string
  [key: string]: unknown
}

export function getStoredToken() {
  if (typeof window === 'undefined') return ''
  return localStorage.getItem(TOKEN_KEY) || ''
}

export function getStoredUser(): ApiUser | null {
  if (typeof window === 'undefined') return null
  const value = localStorage.getItem(USER_KEY)
  return value ? JSON.parse(value) : null
}

export function clearSession() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

export async function login(username: string, password: string) {
  const form = new URLSearchParams()
  form.set('username', username)
  form.set('password', password)
  const tokenResponse = await fetch(`${API_BASE}/api/v1/auth/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: form.toString(),
  })

  if (!tokenResponse.ok) {
    throw new Error('Invalid username or password')
  }

  const token = await tokenResponse.json()
  localStorage.setItem(TOKEN_KEY, token.access_token)
  const user = await apiGet<ApiUser>('/api/v1/auth/me')
  localStorage.setItem(USER_KEY, JSON.stringify(user))
  return user
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers)
  const token = getStoredToken()
  if (token) headers.set('Authorization', `Bearer ${token}`)
  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  let response = await fetch(`${API_BASE}${path}`, { ...options, headers })
  if (response.status === 401 && path !== '/api/v1/auth/me') {
    const refreshed = await loginWithDemoAccount()
    if (refreshed) {
      headers.set('Authorization', `Bearer ${getStoredToken()}`)
      response = await fetch(`${API_BASE}${path}`, { ...options, headers })
    }
  }
  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    const detail = typeof data.detail === 'string' ? data.detail : 'Request failed'
    throw new Error(detail)
  }

  return data as T
}

async function loginWithDemoAccount() {
  try {
    const form = new URLSearchParams()
    form.set('username', 'admin')
    form.set('password', 'admin123')
    const response = await fetch(`${API_BASE}/api/v1/auth/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: form.toString(),
    })
    if (!response.ok) return false
    const token = await response.json()
    localStorage.setItem(TOKEN_KEY, token.access_token)
    localStorage.setItem(USER_KEY, JSON.stringify({ username: 'admin', role: 'admin' }))
    return true
  } catch {
    return false
  }
}

export function apiGet<T>(path: string) {
  return request<T>(path)
}

export function apiPost<T>(path: string, body?: unknown) {
  return request<T>(path, {
    method: 'POST',
    body: body === undefined ? undefined : JSON.stringify(body),
  })
}

export function buildStreamUrl() {
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
  const host = window.location.hostname || '127.0.0.1'
  return `${protocol}://${host}:8000/api/v1/transactions/stream?token=${encodeURIComponent(getStoredToken())}`
}

export function pct(value?: number, digits = 1) {
  if (typeof value !== 'number' || Number.isNaN(value)) return 'N/A'
  return `${(value * 100).toFixed(digits)}%`
}

export function num(value?: number, digits = 0) {
  if (typeof value !== 'number' || Number.isNaN(value)) return 'N/A'
  return value.toLocaleString(undefined, { maximumFractionDigits: digits })
}
