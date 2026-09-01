'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { FormEvent, ReactNode, useEffect, useState } from 'react'
import {
  Activity,
  Bot,
  Database,
  GitBranch,
  LayoutDashboard,
  ListChecks,
  LogOut,
  Network,
  Landmark,
  PlayCircle,
  Scale,
  Shield,
  SlidersHorizontal,
  UserRound,
} from 'lucide-react'
import { ApiUser, clearSession, getStoredToken, getStoredUser, login } from '@/lib/api'

const navigation = [
  { href: '/overview', label: 'Overview', icon: LayoutDashboard },
  { href: '/datasets', label: 'Datasets', icon: Database },
  { href: '/training', label: 'Model Training', icon: Activity },
  { href: '/simulation', label: 'Live Simulation', icon: PlayCircle },
  { href: '/risk-scoring', label: 'Risk Scoring', icon: Shield },
  { href: '/investigations', label: 'Investigations', icon: ListChecks },
  { href: '/policies', label: 'Policies', icon: SlidersHorizontal },
  { href: '/graph-risk', label: 'Graph Risk', icon: Network },
  { href: '/drift', label: 'Drift Monitor', icon: GitBranch },
  { href: '/copilot', label: 'AI Copilot', icon: Bot },
  { href: '/bank-account', label: 'Bank Account', icon: Landmark },
]

export function AppShell({
  title,
  description,
  children,
}: {
  title: string
  description: string
  children: ReactNode
}) {
  const pathname = usePathname()
  const [mounted, setMounted] = useState(false)
  const [user, setUser] = useState<ApiUser | null>(null)
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('admin123')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    setMounted(true)
    setUser(getStoredUser())
    const timer = window.setInterval(() => setUser(getStoredUser()), 1200)
    return () => window.clearInterval(timer)
  }, [])

  async function submit(event: FormEvent) {
    event.preventDefault()
    setBusy(true)
    setError('')
    try {
      setUser(await login(username, password))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to sign in')
    } finally {
      setBusy(false)
    }
  }

  function signOut() {
    clearSession()
    setUser(null)
  }


  return (
    <div className="app-frame">
      <aside className="sidebar">
        <Link href="/" className="brand" aria-label="RiskShield AI Manager home">
          <span className="brand-mark">
            <Shield size={22} />
          </span>
          <span>
            <strong>RiskShield</strong>
            <small>AI Manager</small>
          </span>
        </Link>

        <nav className="nav-list" aria-label="Primary">
          {navigation.map((item) => {
            const Icon = item.icon
            const active = pathname === item.href
            return (
              <Link key={item.href} href={item.href} className={active ? 'nav-item active' : 'nav-item'}>
                <Icon size={18} />
                <span>{item.label}</span>
              </Link>
            )
          })}
        </nav>

        <div className="sidebar-note">
          <Scale size={16} />
          <span>Dataset replay mode. No real bank connection is opened.</span>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <p className="eyebrow">Financial risk operations</p>
            <h1>{title}</h1>
            <p>{description}</p>
          </div>
          <div className="account-box">
            {user ? (
              <>
                <div className="account-user">
                  <UserRound size={18} />
                  <span>{user.username}</span>
                  <strong>{user.role}</strong>
                </div>
                <button className="icon-button" onClick={signOut} aria-label="Sign out" title="Sign out">
                  <LogOut size={18} />
                </button>
              </>
            ) : (
              <form className="login-form" onSubmit={submit}>
                <input value={username} onChange={(event) => setUsername(event.target.value)} aria-label="Username" />
                <input
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  aria-label="Password"
                />
                <button type="submit" disabled={busy}>
                  {busy ? 'Signing in' : 'Sign in'}
                </button>
              </form>
            )}
          </div>
        </header>

        {mounted && !user && !getStoredToken() ? (
          <section className="notice-band warning">
            <strong>Sign in to run protected actions.</strong>
            <span>Default demo credentials are pre-filled for local testing.</span>
            {error && <em>{error}</em>}
          </section>
        ) : null}

        {children}
      </main>
    </div>
  )
}

export function StatTile({
  label,
  value,
  detail,
  tone = 'neutral',
}: {
  label: string
  value: string
  detail?: string
  tone?: 'neutral' | 'good' | 'warn' | 'danger'
}) {
  return (
    <div className={`stat-tile ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
      {detail ? <small>{detail}</small> : null}
    </div>
  )
}

export function Panel({
  title,
  action,
  children,
}: {
  title: string
  action?: ReactNode
  children: ReactNode
}) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <h2>{title}</h2>
        {action}
      </div>
      {children}
    </section>
  )
}

export function StatusPill({ value }: { value?: string }) {
  const normalized = (value || 'UNKNOWN').toLowerCase()
  return <span className={`status-pill ${normalized}`}>{value || 'UNKNOWN'}</span>
}

export function EmptyState({ title, body }: { title: string; body: string }) {
  return (
    <div className="empty-state">
      <strong>{title}</strong>
      <span>{body}</span>
    </div>
  )
}
