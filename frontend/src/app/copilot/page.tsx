'use client'

import { FormEvent, useCallback, useEffect, useRef, useState } from 'react'
import {
  AlertTriangle, Bot, CheckCircle2, FileSearch, HelpCircle,
  List, Lightbulb, MessageSquare, RotateCcw, Send, Shield, Zap
} from 'lucide-react'
import { AppShell, EmptyState, Panel, StatTile } from '@/components/app-shell'
import { apiGet, apiPost } from '@/lib/api'

// ─── Types ────────────────────────────────────────────────────────────────────
interface ChatMessage { role: 'user' | 'assistant'; content: string }

interface CopilotHealth {
  ollama: boolean
  model: string
  model_ready: boolean
  available: boolean
  provider: string
  pull_hint?: string
  setup_hint?: string
}

// ─── Quick action definitions ─────────────────────────────────────────────────
const QUICK_ACTIONS = [
  { key: 'explain_risk',     label: 'Explain Risk',          icon: Shield },
  { key: 'investigate',      label: 'Investigate',           icon: FileSearch },
  { key: 'risk_factors',     label: 'Risk Factors',          icon: List },
  { key: 'triggered_rules',  label: 'Triggered Rules',       icon: Zap },
  { key: 'recommend',        label: 'Recommend Action',      icon: Lightbulb },
  { key: 'summarize',        label: 'Summarize Case',        icon: MessageSquare },
]

// ─── Sub-components ───────────────────────────────────────────────────────────
function OllamaOfflineBanner({ health }: { health: CopilotHealth }) {
  return (
    <section className="notice-band warning" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: 8 }}>
      <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
        <AlertTriangle size={18} />
        <strong>
          {!health.ollama
            ? 'Ollama is not running.'
            : `Model "${health.model}" is not installed.`}
        </strong>
      </div>
      <div style={{ fontSize: '0.88rem', color: '#5f6f86' }}>
        {health.setup_hint || health.pull_hint ||
          'The AI Risk Copilot requires Ollama and the Zephyr model to be available locally.'}
        <br />
        <strong>Setup commands (run once in a terminal):</strong>
        <code style={{
          display: 'block', marginTop: 8, padding: '10px 14px',
          background: '#1e293b', color: '#e2e8f0', borderRadius: 6,
          fontFamily: 'Consolas, monospace', fontSize: '0.85rem', lineHeight: 1.8
        }}>
          ollama serve<br />
          ollama pull {health.model || 'zephyr:7b-beta'}
        </code>
        <span style={{ display: 'block', marginTop: 6 }}>
          After Ollama starts, click <strong>Refresh Status</strong>.
          The rest of RiskShield continues working normally without it.
        </span>
      </div>
    </section>
  )
}

function MessageBubble({ msg }: { msg: ChatMessage }) {
  const isUser = msg.role === 'user'
  return (
    <div style={{
      display: 'flex', justifyContent: isUser ? 'flex-end' : 'flex-start',
      marginBottom: 12,
    }}>
      {!isUser && (
        <div style={{
          width: 32, height: 32, borderRadius: '50%', background: '#0f172a',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          marginRight: 10, flexShrink: 0
        }}>
          <Bot size={16} color="#fff" />
        </div>
      )}
      <div style={{
        maxWidth: '72%', padding: '10px 14px',
        background: isUser ? '#2563eb' : '#f1f5f9',
        color: isUser ? '#fff' : '#0f172a',
        borderRadius: isUser ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
        fontSize: '0.9rem', lineHeight: 1.6,
        whiteSpace: 'pre-wrap',
      }}>
        {msg.content}
      </div>
    </div>
  )
}

// ─── Main page ────────────────────────────────────────────────────────────────
export default function CopilotPage() {
  const [health, setHealth] = useState<CopilotHealth | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [prompt, setPrompt] = useState('')
  const [transactionId, setTransactionId] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const chatEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = useCallback(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  // Fetch copilot health status
  async function fetchHealth() {
    try {
      const data = await apiGet<CopilotHealth>('/api/v1/copilot/health')
      setHealth(data)
    } catch {
      // If health endpoint fails, report Ollama as down but keep UI functional
      setHealth({
        ollama: false, model: 'zephyr:7b-beta', model_ready: false,
        available: false, provider: 'ollama',
        setup_hint: 'Could not reach the backend health endpoint.'
      })
    }
  }

  useEffect(() => { fetchHealth() }, [])
  useEffect(() => { scrollToBottom() }, [messages, scrollToBottom])

  async function sendMessage(userText: string) {
    if (!userText.trim()) return
    setBusy(true)
    setError('')

    const newMessages: ChatMessage[] = [...messages, { role: 'user', content: userText }]
    setMessages(newMessages)
    setPrompt('')

    try {
      // Build history array for context window
      const historyPayload = newMessages.slice(-12).map(m => ({
        role: m.role, content: m.content
      }))

      const result = await apiPost<any>('/api/v1/copilot/message', {
        message: userText,
        transaction_id: transactionId || undefined,
        history: historyPayload.slice(0, -1), // exclude the message we just added
        history_window: 6,
      })

      const answer = result.available
        ? result.response
        : (result.fallback || 'RiskShield Copilot is currently unavailable because the local AI service is not configured.')

      setMessages(prev => [...prev, { role: 'assistant', content: answer }])
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'RiskShield Copilot is currently unavailable because the local AI service is not configured.'
      }])
      setError(err instanceof Error ? err.message : 'Request failed')
    } finally {
      setBusy(false)
    }
  }

  async function runQuickAction(actionKey: string) {
    setBusy(true)
    setError('')
    const label = QUICK_ACTIONS.find(a => a.key === actionKey)?.label || actionKey
    setMessages(prev => [...prev, { role: 'user', content: `[Quick Action] ${label}` }])
    try {
      const result = await apiPost<any>('/api/v1/copilot/quick_action', {
        action: actionKey,
        transaction_id: transactionId || undefined,
      })
      const answer = result.available
        ? result.response
        : (result.fallback || 'RiskShield Copilot is currently unavailable because the local AI service is not configured.')
      setMessages(prev => [...prev, { role: 'assistant', content: answer }])
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'RiskShield Copilot is currently unavailable because the local AI service is not configured.'
      }])
    } finally {
      setBusy(false)
    }
  }

  async function runInvestigate() {
    if (!transactionId.trim()) {
      setError('Enter a Transaction ID to investigate.')
      return
    }
    setBusy(true)
    setError('')
    setMessages(prev => [...prev, { role: 'user', content: `Investigate transaction: ${transactionId}` }])
    try {
      const result = await apiPost<any>('/api/v1/copilot/investigate', {
        transaction_id: transactionId,
      })
      const answer = result.available
        ? result.response
        : (result.fallback || 'RiskShield Copilot is currently unavailable because the local AI service is not configured.')
      setMessages(prev => [...prev, { role: 'assistant', content: answer }])
    } catch {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'RiskShield Copilot is currently unavailable because the local AI service is not configured.'
      }])
    } finally {
      setBusy(false)
    }
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    sendMessage(prompt)
  }

  const isAvailable = health?.available === true

  return (
    <AppShell
      title="AI Risk Copilot"
      description="Zephyr-7B-beta powered investigation assistant. Explains risk scores, investigates transactions, and helps analysts make better decisions."
    >
      {error ? (
        <section className="notice-band danger">
          <AlertTriangle size={18} /><span>{error}</span>
        </section>
      ) : null}

      {/* ── Status tiles ─────────────────────────────────────────── */}
      <section className="stat-grid">
        <StatTile
          label="Model"
          value={health?.model || 'zephyr:7b-beta'}
          detail="Local Ollama inference"
        />
        <StatTile
          label="Ollama"
          value={health?.ollama ? 'Running' : 'Offline'}
          tone={health?.ollama ? 'good' : 'warn'}
          detail={health?.ollama ? 'Service reachable' : 'Not detected'}
        />
        <StatTile
          label="Model Ready"
          value={health?.model_ready ? 'Yes' : 'No'}
          tone={health?.model_ready ? 'good' : 'warn'}
          detail={health?.model_ready ? 'Zephyr loaded' : 'Pull required'}
        />
        <StatTile
          label="Copilot"
          value={isAvailable ? 'Available' : 'Unavailable'}
          tone={isAvailable ? 'good' : 'warn'}
          detail="Independent of risk engine"
        />
      </section>

      {/* ── Offline banner ─────────────────────────────────────────── */}
      {health && !health.available ? (
        <OllamaOfflineBanner health={health} />
      ) : null}

      {/* ── Main two-column layout ──────────────────────────────────── */}
      <section className="two-column" style={{ gridTemplateColumns: '1fr 2fr' }}>

        {/* Left: Controls */}
        <Panel title="Session Controls">
          <div style={{ display: 'grid', gap: 12 }}>
            <label style={{ display: 'grid', gap: 4, fontWeight: 700, color: '#5f6f86', fontSize: '0.85rem' }}>
              Transaction ID (optional)
              <input
                value={transactionId}
                onChange={e => setTransactionId(e.target.value)}
                placeholder="e.g. TXN-BNK-001234"
              />
            </label>

            <button onClick={runInvestigate} disabled={busy || !transactionId.trim()}>
              <FileSearch size={15} />
              Investigate Transaction
            </button>

            <hr style={{ border: 'none', borderTop: '1px solid #e2e8f0', margin: '4px 0' }} />
            <p style={{ fontSize: '0.82rem', color: '#5f6f86', margin: 0 }}>Quick Actions</p>

            {QUICK_ACTIONS.map(({ key, label, icon: Icon }) => (
              <button
                key={key}
                className="secondary-button"
                disabled={busy}
                onClick={() => runQuickAction(key)}
                style={{ justifyContent: 'flex-start', gap: 8 }}
              >
                <Icon size={14} />{label}
              </button>
            ))}

            <hr style={{ border: 'none', borderTop: '1px solid #e2e8f0', margin: '4px 0' }} />
            <button
              className="secondary-button"
              onClick={() => setMessages([])}
              disabled={busy}
            >
              <RotateCcw size={14} /> Clear History
            </button>
            <button className="secondary-button" onClick={fetchHealth} disabled={busy}>
              <HelpCircle size={14} /> Refresh Status
            </button>
          </div>
        </Panel>

        {/* Right: Chat window */}
        <Panel title="🛡 RiskShield Copilot — Zephyr 7B">
          {/* Chat history */}
          <div style={{
            minHeight: 340, maxHeight: 460, overflowY: 'auto',
            padding: '8px 0', marginBottom: 16,
            borderBottom: '1px solid #e2e8f0',
          }}>
            {messages.length === 0 ? (
              <EmptyState
                title="Start a conversation"
                body={isAvailable
                  ? 'Ask a risk analysis question or use a Quick Action on the left. Optionally enter a Transaction ID for context-aware answers.'
                  : 'Copilot is offline. Start Ollama and pull zephyr:7b-beta to enable AI-assisted investigation. The rest of RiskShield continues working normally.'}
              />
            ) : (
              <>
                {messages.map((msg, i) => <MessageBubble key={i} msg={msg} />)}
                {busy && (
                  <div style={{ display: 'flex', gap: 8, alignItems: 'center', padding: '8px 0' }}>
                    <div style={{
                      width: 32, height: 32, borderRadius: '50%', background: '#0f172a',
                      display: 'flex', alignItems: 'center', justifyContent: 'center'
                    }}>
                      <Bot size={16} color="#fff" />
                    </div>
                    <span style={{ color: '#5f6f86', fontSize: '0.88rem' }}>Zephyr is thinking…</span>
                  </div>
                )}
                <div ref={chatEndRef} />
              </>
            )}
          </div>

          {/* Input area */}
          <form onSubmit={handleSubmit} style={{ display: 'flex', gap: 10, alignItems: 'flex-end' }}>
            <textarea
              value={prompt}
              onChange={e => setPrompt(e.target.value)}
              placeholder={isAvailable
                ? 'Ask a risk analysis question…'
                : 'Copilot unavailable — start Ollama to enable'}
              rows={2}
              style={{ flex: 1, resize: 'vertical', minHeight: 44 }}
              onKeyDown={e => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  sendMessage(prompt)
                }
              }}
            />
            <button type="submit" disabled={busy || !prompt.trim()} style={{ alignSelf: 'stretch' }}>
              <Send size={16} />
              {busy ? 'Thinking…' : 'Send'}
            </button>
          </form>
          <p style={{ fontSize: '0.78rem', color: '#94a3b8', margin: '8px 0 0' }}>
            Zephyr does NOT determine risk scores. The RiskShield risk engine remains authoritative.
            Shift+Enter for newline.
          </p>
        </Panel>
      </section>
    </AppShell>
  )
}
