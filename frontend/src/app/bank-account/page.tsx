'use client'

import { FormEvent, useState } from 'react'
import { AlertTriangle, Building, CreditCard, Landmark, CheckCircle2 } from 'lucide-react'
import { AppShell, EmptyState, Panel, StatTile, StatusPill } from '@/components/app-shell'
import { apiPost, apiGet, pct, num, Transaction } from '@/lib/api'

export default function BankAccountPage() {
  const [accountName, setAccountName] = useState('')
  const [accountNumber, setAccountNumber] = useState('')
  const [ifsc, setIfsc] = useState('')
  const [pnr, setPnr] = useState('')
  const [bankName, setBankName] = useState('HDFC Bank')
  const [accountType, setAccountType] = useState('Savings')
  
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [linkedAccount, setLinkedAccount] = useState<any>(null)
  const [transactions, setTransactions] = useState<Transaction[]>([])

  async function linkAccount(event: FormEvent) {
    event.preventDefault()
    if (!accountName || !accountNumber || !ifsc) {
      setError('Please fill in all required fields.')
      return
    }
    
    // Basic IFSC validation (4 letters, 0, 6 alphanumeric)
    const ifscRegex = /^[A-Z]{4}0[A-Z0-9]{6}$/i
    if (!ifscRegex.test(ifsc)) {
      setError('Invalid IFSC Code format.')
      return
    }

    setBusy(true)
    setError('')
    try {
      const result = await apiPost<any>('/api/v1/bank-account/link', {
        account_name: accountName,
        account_number: accountNumber,
        ifsc_code: ifsc,
        pnr_number: pnr,
        bank_name: bankName,
        account_type: accountType
      })
      
      if (result.error) throw new Error(result.error)
      setLinkedAccount(result.account)
      
      // Load simulated transactions
      const txns = await apiGet<{ transactions: Transaction[] }>(`/api/v1/bank-account/transactions?account_number=${encodeURIComponent(accountNumber)}`)
      setTransactions(txns.transactions || [])
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to link account')
    } finally {
      setBusy(false)
    }
  }

  function unlink() {
    setLinkedAccount(null)
    setTransactions([])
    setAccountNumber('')
  }

  return (
    <AppShell title="Bank Account Linking" description="Connect financial accounts via IFSC/PNR to evaluate linked transaction histories against risk models.">
      {error ? <section className="notice-band danger"><AlertTriangle size={18} /><span>{error}</span></section> : null}

      <section className="notice-band warning">
        <Landmark size={18} />
        <div>
          <strong>Simulated link only.</strong> No real bank connection is made. Transaction history is sourced from the loaded datasets to demonstrate risk analysis capabilities.
        </div>
      </section>

      {!linkedAccount ? (
        <section className="two-column">
          <Panel title="Link New Account">
            <form onSubmit={linkAccount} style={{ display: 'grid', gap: '16px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <label style={{ display: 'grid', gap: '6px', fontWeight: 700, color: '#5f6f86' }}>
                  Account Holder Name *
                  <input value={accountName} onChange={e => setAccountName(e.target.value)} placeholder="e.g. John Doe" />
                </label>
                <label style={{ display: 'grid', gap: '6px', fontWeight: 700, color: '#5f6f86' }}>
                  Account Number *
                  <input value={accountNumber} onChange={e => setAccountNumber(e.target.value)} placeholder="e.g. 100023456789" type="password" />
                </label>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <label style={{ display: 'grid', gap: '6px', fontWeight: 700, color: '#5f6f86' }}>
                  IFSC Code *
                  <input value={ifsc} onChange={e => setIfsc(e.target.value)} placeholder="e.g. HDFC0001234" style={{ textTransform: 'uppercase' }} maxLength={11} />
                </label>
                <label style={{ display: 'grid', gap: '6px', fontWeight: 700, color: '#5f6f86' }}>
                  PNR / Reference Number
                  <input value={pnr} onChange={e => setPnr(e.target.value)} placeholder="Optional" />
                </label>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <label style={{ display: 'grid', gap: '6px', fontWeight: 700, color: '#5f6f86' }}>
                  Bank Name
                  <select value={bankName} onChange={e => setBankName(e.target.value)}>
                    <option value="HDFC Bank">HDFC Bank</option>
                    <option value="State Bank of India">State Bank of India</option>
                    <option value="ICICI Bank">ICICI Bank</option>
                    <option value="Axis Bank">Axis Bank</option>
                    <option value="Kotak Mahindra Bank">Kotak Mahindra Bank</option>
                  </select>
                </label>
                <label style={{ display: 'grid', gap: '6px', fontWeight: 700, color: '#5f6f86' }}>
                  Account Type
                  <select value={accountType} onChange={e => setAccountType(e.target.value)}>
                    <option value="Savings">Savings</option>
                    <option value="Current">Current</option>
                    <option value="Credit">Credit</option>
                  </select>
                </label>
              </div>

              <button type="submit" disabled={busy} style={{ justifySelf: 'start', marginTop: '8px' }}>
                <CreditCard size={16} />
                {busy ? 'Linking...' : 'Link Account'}
              </button>
            </form>
          </Panel>
          <Panel title="Supported Institutions">
            <div className="tag-list" style={{ marginBottom: 16 }}>
              <span>HDFC Bank</span>
              <span>State Bank of India</span>
              <span>ICICI Bank</span>
              <span>Axis Bank</span>
              <span>Kotak Mahindra Bank</span>
            </div>
            <p className="muted-copy">Account linking enables the risk engine to analyze historical behavior, detect anomalies based on past patterns, and establish trusted counterparty graphs.</p>
          </Panel>
        </section>
      ) : (
        <>
          <section className="stat-grid">
            <StatTile label="Account Name" value={linkedAccount.account_name} detail={linkedAccount.bank_name} />
            <StatTile label="Account Number" value={linkedAccount.account_number_masked} detail={accountType} />
            <StatTile label="Simulated Balance" value={`$${num(linkedAccount.balance, 2)}`} tone="good" />
            <StatTile label="Connection Status" value="Active" detail="Simulated dataset link" tone="good" />
          </section>

          <Panel title="Account History & Risk Posture" action={<button className="secondary-button" onClick={unlink}>Unlink Account</button>}>
            {transactions.length ? (
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Transaction ID</th>
                      <th>Timestamp</th>
                      <th>Merchant / Counterparty</th>
                      <th>Category</th>
                      <th>Amount</th>
                      <th>Fraud Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {transactions.map((item, i) => (
                      <tr key={i}>
                        <td><code>{String(item.transaction_id || `sim-${i}`).slice(-10)}</code></td>
                        <td>{item.timestamp ? new Date(String(item.timestamp)).toLocaleString() : 'N/A'}</td>
                        <td>{item.merchant_id || 'Unknown'}</td>
                        <td>{item.category ? String(item.category) : 'N/A'}</td>
                        <td>${typeof item.amount === 'number' ? item.amount.toFixed(2) : '0.00'}</td>
                        <td>
                          {item.fraud_label === 1 ? <StatusPill value="CRITICAL" /> : <StatusPill value="LOW" />}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <EmptyState title="No transactions found" body="This simulated account has no historical transactions in the dataset." />
            )}
          </Panel>
        </>
      )}
    </AppShell>
  )
}
