import React from 'react';

const FEATURES = [
  {
    icon: '🔍',
    title: 'Behaviour-Based Analysis',
    desc: 'Analyse purchase frequency, recency, cart abandonment and more to identify customers headed for the exit.',
  },
  {
    icon: '⚡',
    title: 'Real-Time Predictions',
    desc: 'Get instant churn probability scores for any customer profile—single or batch—powered by ML in milliseconds.',
  },
  {
    icon: '📊',
    title: 'Batch Processing',
    desc: 'Upload your entire customer CSV or Excel export and download enriched predictions ready for your CRM.',
  },
  {
    icon: '🎯',
    title: 'Actionable Insights',
    desc: 'Every prediction comes with a retention recommendation—win-back offer, loyalty reward, or proactive outreach.',
  },
  {
    icon: '🔒',
    title: 'Privacy-First',
    desc: 'All prediction runs locally on your infrastructure. Customer data never leaves your network.',
  },
  {
    icon: '🛒',
    title: 'Ecommerce-Optimised',
    desc: 'Trained on the 10 behavioural signals that matter most in ecommerce—not generic banking metrics.',
  },
];

const STEPS = [
  { num: 1, title: 'Import Customer Data', desc: 'Paste in a customer profile or upload a CSV / Excel file.' },
  { num: 2, title: 'Run ML Analysis',      desc: 'Our Decision Tree model scores churn probability instantly.' },
  { num: 3, title: 'Review Results',        desc: 'See confidence-rated predictions for every record.' },
  { num: 4, title: 'Take Action',           desc: 'Export results and act on retention recommendations.' },
];

const BARS = [
  { label: 'Jan', pct: 45, muted: true },
  { label: 'Feb', pct: 52, muted: true },
  { label: 'Mar', pct: 38, muted: true },
  { label: 'Apr', pct: 61, muted: true },
  { label: 'May', pct: 47, muted: true },
  { label: 'Jun', pct: 55, muted: false },
  { label: 'Jul', pct: 33, muted: false },
];

export default function HomePage({ onGetStarted, user, onLogout }) {
  return (
    <>
      {/* ── Navbar ── */}
      <nav className="nav">
        <div className="nav-brand">
          <div className="nav-logo">🛒</div>
          <span className="nav-name">Ecommerce Churn Prediction</span>
        </div>
        <ul className="nav-links">
          <li><a href="#features">Features</a></li>
          <li><a href="#how">How It Works</a></li>
          <li><a href="#metrics">Metrics</a></li>
          {user ? (
            <>
              <li style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div style={{ background: 'var(--green-100)', color: 'var(--green-700)', padding: '0.3rem 0.8rem', borderRadius: '100px', fontSize: '0.8rem', fontWeight: 700 }}>
                   👋 {user}
                </div>
              </li>
              <li>
                <button 
                   onClick={(e) => { e.preventDefault(); onLogout(); }}
                   style={{ background: 'none', border: 'none', color: '#ef4444', fontSize: '0.85rem', fontWeight: 600, cursor: 'pointer' }}>
                   Logout
                </button>
              </li>
            </>
          ) : null}
          <li>
            <a href="#get-started" className="nav-cta" onClick={e => { e.preventDefault(); onGetStarted(); }}>
              {user ? 'Open Dashboard →' : 'Launch Dashboard →'}
            </a>
          </li>
        </ul>
      </nav>

      {/* ── Hero ── */}
      <section className="hero">
        <div className="hero-inner">
          {/* Left */}
          <div>
            <div className="hero-tag">🌿 Built for Ecommerce Retention Teams</div>
            <h1 className="hero-heading">
              Stop Losing Customers.<br />
              <span className="highlight">Predict Churn Before It Happens.</span>
            </h1>
            <p className="hero-sub">
              Ecommerce Churn Prediction uses machine learning trained on real shopping behaviour to flag
              at-risk customers days before they leave — so your team can act first.
            </p>
            <div className="hero-actions">
              <button className="btn-hero-primary" onClick={onGetStarted}>
                🚀 Try it Free
              </button>
              <a href="#how" className="btn-hero-outline">See How It Works</a>
            </div>
          </div>

          {/* Right – animated card */}
          <div className="hero-visual">
            <div className="hero-badge-float badge-pop-1">
              <span className="badge-dot dot-green" />
              <span>Customer retained ✓</span>
            </div>

            <div className="hero-card-main">
              <p className="hero-card-label">Churn Risk Score</p>
              <p className="hero-card-value">78.4%</p>
              <p className="hero-card-sub">⚠️ High risk — act now</p>

              <div className="hero-bar-wrap">
                {[
                  { label: 'Recency',   pct: 82 },
                  { label: 'Frequency', pct: 35 },
                  { label: 'Spend',     pct: 55 },
                  { label: 'CSAT',      pct: 20 },
                ].map(b => (
                  <div className="hero-bar-row" key={b.label}>
                    <span className="hero-bar-label">{b.label}</span>
                    <div className="hero-bar-bg">
                      <div className="hero-bar-fill" style={{ width: `${b.pct}%` }} />
                    </div>
                    <span className="hero-bar-pct">{b.pct}%</span>
                  </div>
                ))}
              </div>

              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <span style={{
                  background: '#fee2e2', color: '#dc2626',
                  padding: '0.3rem 0.75rem', borderRadius: '100px',
                  fontSize: '0.78rem', fontWeight: 700,
                }}>
                  Churn Risk
                </span>
                <span style={{
                  background: '#dcfce7', color: '#15803d',
                  padding: '0.3rem 0.75rem', borderRadius: '100px',
                  fontSize: '0.78rem', fontWeight: 700,
                }}>
                  High Confidence
                </span>
              </div>
            </div>

            <div className="hero-badge-float badge-pop-2">
              <span className="badge-dot dot-red" />
              <span>Win-back email sent</span>
            </div>
          </div>
        </div>
      </section>

      {/* ── Stats Strip ── */}
      <div className="stats-strip">
        <div className="stats-inner">
          {[
            { num: '3,000+', label: 'Training Samples' },
            { num: '10',     label: 'Behaviour Features' },
            { num: '~65%',   label: 'Model Accuracy' },
            { num: '< 1s',   label: 'Prediction Speed' },
          ].map(s => (
            <div key={s.label}>
              <div className="stat-num">{s.num}</div>
              <div className="stat-label">{s.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Features ── */}
      <section className="section" id="features">
        <div className="section-inner">
          <span className="section-tag">✨ Features</span>
          <h2 className="section-title">Everything You Need to Retain Customers</h2>
          <p className="section-sub">
            From single-customer analysis to bulk batch processing — built for ecommerce teams of every size.
          </p>

          <div className="features-grid">
            {FEATURES.map(f => (
              <div className="feature-card" key={f.title}>
                <div className="feature-icon">{f.icon}</div>
                <h3 className="feature-title">{f.title}</h3>
                <p className="feature-desc">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── How It Works ── */}
      <section className="section how-section" id="how">
        <div className="section-inner">
          <span className="section-tag">🔄 Process</span>
          <h2 className="section-title">Go From Data to Decision in 4 Steps</h2>
          <p className="section-sub">
            No data science experience required. Upload, score, and take action — all in minutes.
          </p>

          <div className="steps-grid">
            {STEPS.map(s => (
              <div className="step-card" key={s.num}>
                <div className="step-num">{s.num}</div>
                <h4 className="step-title">{s.title}</h4>
                <p className="step-desc">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Metrics ── */}
      <section className="section metrics-section" id="metrics">
        <div className="section-inner">
          <div className="metrics-grid">
            <div>
              <span className="section-tag">📈 Key Signals</span>
              <h2 className="section-title">10 Features Drive Every Prediction</h2>
              <p className="section-sub" style={{ marginBottom: '1.5rem' }}>
                Our model weighs these behavioural indicators to produce an accurate churn probability.
              </p>
              <div className="metric-list">
                {[
                  { emoji: '🛒', name: 'Purchase Frequency',       val: 'Orders last 3 months', pill: 'Top Signal', warn: false },
                  { emoji: '📅', name: 'Days Since Last Purchase',  val: 'Recency score',         pill: 'Top Signal', warn: false },
                  { emoji: '😊', name: 'Satisfaction Score',        val: 'CSAT rating 1–5',       pill: 'Key Factor', warn: false },
                  { emoji: '🛍️', name: 'Cart Abandonment Rate',     val: '% of carts dropped',    pill: 'Risk Indicator', warn: true },
                ].map(m => (
                  <div className="metric-row" key={m.name}>
                    <span className="metric-emoji">{m.emoji}</span>
                    <div className="metric-info">
                      <div className="metric-name">{m.name}</div>
                      <div className="metric-val">{m.val}</div>
                    </div>
                    <span className={`metric-pill${m.warn ? ' warn' : ''}`}>{m.pill}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="metrics-visual">
              <p className="chart-title">Monthly Churn Rate by Segment</p>
              <div className="chart-bars">
                {BARS.map(b => (
                  <div className="chart-bar-col" key={b.label}>
                    <span className="chart-bar-pct">{b.pct}%</span>
                    <div
                      className={`chart-bar${b.muted ? ' muted' : ''}`}
                      style={{ height: `${b.pct * 1.5}px` }}
                    />
                    <span className="chart-bar-label">{b.label}</span>
                  </div>
                ))}
              </div>
              <p style={{ fontSize: '0.75rem', color: 'var(--gray-400)', marginTop: '0.5rem' }}>
                Green bars = this year · Light bars = last year
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="cta-section" id="get-started">
        <div className="cta-inner">
          <h2 className="cta-title">Ready to Reduce Churn?</h2>
          <p className="cta-sub">
            Launch the prediction dashboard now — no sign-up, no credit card. Just data-driven retention.
          </p>
          <button className="btn-cta" onClick={onGetStarted}>
            🚀 Open Dashboard
          </button>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="footer">
        <div className="footer-inner">
          <div className="footer-brand">
            <div className="footer-logo-row">
              <div className="footer-logo">🛒</div>
              <span className="footer-brand-name">Ecommerce Churn Prediction</span>
            </div>
            <p className="footer-desc">
              Machine learning-powered customer retention intelligence, built specifically for ecommerce teams.
            </p>
          </div>

          <div className="footer-col">
            <h4>Product</h4>
            <ul className="footer-links">
              <li><a href="#features">Features</a></li>
              <li><a href="#how">How It Works</a></li>
              <li><a href="#metrics">Metrics</a></li>
            </ul>
          </div>

          <div className="footer-col">
            <h4>Resources</h4>
            <ul className="footer-links">
              <li><a href="#">API Docs</a></li>
              <li><a href="#">Template Download</a></li>
              <li><a href="#">Data Format Guide</a></li>
            </ul>
          </div>

          <div className="footer-col">
            <h4>Company</h4>
            <ul className="footer-links">
              <li><a href="#">About</a></li>
              <li><a href="#">Privacy Policy</a></li>
              <li><a href="#">Contact</a></li>
            </ul>
          </div>
        </div>

        <div className="footer-bottom">
          <span>© 2026 Ecommerce Churn Prediction. All rights reserved.</span>
          <span>Powered by Scikit-learn · Flask · React</span>
        </div>
      </footer>
    </>
  );
}
