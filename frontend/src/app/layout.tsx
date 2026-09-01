import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'RiskShield AI Manager',
  description: 'AI-powered financial transaction risk management',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
