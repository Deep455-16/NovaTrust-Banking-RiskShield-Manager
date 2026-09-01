'use client'

import Link from 'next/link'
import { ArrowRight, ShieldCheck, CreditCard, Building2, Smartphone, Lock, Globe2 } from 'lucide-react'
import '@/app/globals.css'

export default function BankingLandingPage() {
  return (
    <div className="landing-container">
      {/* ── Navbar ── */}
      <nav className="landing-nav">
        <div className="landing-nav-brand">
          <Building2 size={24} color="#2563eb" />
          <span>NovaTrust Bank</span>
        </div>
        <div className="landing-nav-links">
          <Link href="#">Personal</Link>
          <Link href="#">Business</Link>
          <Link href="#">Corporate</Link>
          <Link href="#">Wealth</Link>
        </div>
        <div className="landing-nav-actions">
          <Link href="/overview" className="btn-primary">
            <Lock size={16} /> Enter Operations Portal
          </Link>
        </div>
      </nav>

      {/* ── Hero Section ── */}
      <header className="landing-hero">
        <div className="landing-hero-content">
          <div className="badge">New Security Features Available</div>
          <h1>Banking without boundaries. Secured by AI.</h1>
          <p>
            Experience the next generation of digital banking with NovaTrust.
            Our platform is protected by the advanced RiskShield AI Engine, securing
            every transaction in real-time.
          </p>
          <div className="hero-buttons">
            <button className="btn-secondary">Open an Account</button>
            <Link href="/overview" className="btn-primary">
              RiskShield Dashboard <ArrowRight size={18} />
            </Link>
          </div>
        </div>
        <div className="landing-hero-image">
          {/* Abstract secure banking illustration using CSS */}
          <div className="glass-card">
            <div className="card-chip"></div>
            <div className="card-number">**** **** **** 4092</div>
            <div className="card-footer">
              <span>NovaTrust Premier</span>
              <ShieldCheck size={28} color="#22c55e" />
            </div>
          </div>
        </div>
      </header>

      {/* ── Features Grid ── */}
      <section className="landing-features">
        <div className="feature-card">
          <Globe2 size={32} color="#3b82f6" />
          <h3>Global Access</h3>
          <p>Access your accounts anywhere in the world with multi-currency support and real-time exchange rates.</p>
        </div>
        <div className="feature-card">
          <Smartphone size={32} color="#3b82f6" />
          <div className="feature-badge">Powered by RiskShield</div>
          <h3>AI Fraud Protection</h3>
          <p>Our machine learning models detect account takeovers and anomalous transactions within milliseconds.</p>
        </div>
        <div className="feature-card">
          <CreditCard size={32} color="#3b82f6" />
          <h3>Virtual Cards</h3>
          <p>Instantly generate virtual cards for secure online shopping with customizable spending limits.</p>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="landing-footer">
        <div className="footer-content">
          <div className="footer-col">
            <strong>NovaTrust Bank</strong>
            <p>123 Financial District, NY 10004</p>
          </div>
          <div className="footer-col">
            <strong>Internal Links</strong>
            <Link href="/overview">Risk Operations Dashboard</Link>
            <Link href="/bank-account">Link Bank Account (Demo)</Link>
          </div>
          <div className="footer-col">
            <strong>Legal</strong>
            <Link href="#">Privacy Policy</Link>
            <Link href="#">Terms of Service</Link>
            <Link href="#">Security Center</Link>
          </div>
        </div>
        <div className="footer-bottom">
          &copy; {new Date().getFullYear()} NovaTrust Bank. This is a demonstration environment for RiskShield AI.
        </div>
      </footer>

      {/* ── Minimal CSS to make it look authentic without touching globals if possible, but injected safely ── */}
      <style jsx>{`
        .landing-container {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
          background: #f8fafc;
          min-height: 100vh;
          display: flex;
          flex-direction: column;
        }

        .landing-nav {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0 40px;
          height: 80px;
          background: white;
          border-bottom: 1px solid #e2e8f0;
          position: sticky;
          top: 0;
          z-index: 100;
        }
        
        .landing-nav-brand {
          display: flex;
          align-items: center;
          gap: 12px;
          font-weight: 700;
          font-size: 1.25rem;
          color: #0f172a;
        }

        .landing-nav-links {
          display: flex;
          gap: 32px;
        }

        .landing-nav-links a {
          text-decoration: none;
          color: #64748b;
          font-weight: 500;
          font-size: 0.95rem;
          transition: color 0.2s;
        }
        
        .landing-nav-links a:hover {
          color: #2563eb;
        }

        .landing-nav-actions {
          display: flex;
          gap: 16px;
          align-items: center;
        }

        .btn-primary {
          background: #2563eb;
          color: white;
          padding: 10px 20px;
          border-radius: 8px;
          text-decoration: none;
          font-weight: 500;
          display: flex;
          align-items: center;
          gap: 8px;
          transition: background 0.2s;
          border: none;
          cursor: pointer;
        }

        .btn-primary:hover {
          background: #1d4ed8;
        }

        .btn-secondary {
          background: white;
          color: #0f172a;
          padding: 10px 20px;
          border-radius: 8px;
          text-decoration: none;
          font-weight: 500;
          border: 1px solid #e2e8f0;
          cursor: pointer;
        }

        .landing-hero {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 60px;
          padding: 80px 40px;
          max-width: 1200px;
          margin: 0 auto;
          align-items: center;
        }

        .badge {
          display: inline-block;
          background: #eff6ff;
          color: #2563eb;
          padding: 6px 12px;
          border-radius: 20px;
          font-size: 0.85rem;
          font-weight: 600;
          margin-bottom: 24px;
        }

        .landing-hero h1 {
          font-size: 3.5rem;
          line-height: 1.1;
          color: #0f172a;
          margin: 0 0 24px 0;
          letter-spacing: -0.02em;
        }

        .landing-hero p {
          font-size: 1.15rem;
          color: #64748b;
          line-height: 1.6;
          margin: 0 0 40px 0;
        }

        .hero-buttons {
          display: flex;
          gap: 16px;
        }

        .glass-card {
          background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
          border-radius: 20px;
          padding: 32px;
          height: 220px;
          width: 360px;
          box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          position: relative;
          overflow: hidden;
          color: white;
          transform: perspective(1000px) rotateY(-15deg) rotateX(10deg);
          transition: transform 0.3s;
        }
        
        .glass-card:hover {
          transform: perspective(1000px) rotateY(-5deg) rotateX(5deg);
        }

        .glass-card::before {
          content: '';
          position: absolute;
          top: 0; left: -100%; width: 50%; height: 100%;
          background: linear-gradient(to right, transparent, rgba(255,255,255,0.1), transparent);
          transform: skewX(-20deg);
        }

        .card-chip {
          width: 45px;
          height: 35px;
          background: #ffd700;
          border-radius: 6px;
          opacity: 0.8;
        }

        .card-number {
          font-size: 1.4rem;
          letter-spacing: 4px;
          font-family: monospace;
          margin-top: auto;
          margin-bottom: 24px;
        }

        .card-footer {
          display: flex;
          justify-content: space-between;
          align-items: center;
          font-weight: 500;
          color: #94a3b8;
        }

        .landing-features {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 32px;
          padding: 80px 40px;
          max-width: 1200px;
          margin: 0 auto;
        }

        .feature-card {
          background: white;
          padding: 40px 32px;
          border-radius: 16px;
          border: 1px solid #e2e8f0;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
          position: relative;
        }

        .feature-card h3 {
          margin: 24px 0 12px 0;
          color: #0f172a;
          font-size: 1.25rem;
        }

        .feature-card p {
          color: #64748b;
          line-height: 1.6;
          margin: 0;
        }
        
        .feature-badge {
          position: absolute;
          top: 32px; right: 32px;
          background: #dcfce7;
          color: #166534;
          font-size: 0.75rem;
          font-weight: 600;
          padding: 4px 8px;
          border-radius: 12px;
        }

        .landing-footer {
          background: #0f172a;
          color: #94a3b8;
          padding: 60px 40px 32px 40px;
          margin-top: auto;
        }

        .footer-content {
          max-width: 1200px;
          margin: 0 auto;
          display: grid;
          grid-template-columns: 2fr 1fr 1fr;
          gap: 40px;
          border-bottom: 1px solid #1e293b;
          padding-bottom: 40px;
          margin-bottom: 32px;
        }

        .footer-col {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }
        
        .footer-col strong {
          color: white;
          font-size: 1.1rem;
        }

        .footer-col a {
          color: #94a3b8;
          text-decoration: none;
          transition: color 0.2s;
        }

        .footer-col a:hover {
          color: white;
        }

        .footer-bottom {
          text-align: center;
          font-size: 0.9rem;
        }
      `}</style>
    </div>
  )
}
