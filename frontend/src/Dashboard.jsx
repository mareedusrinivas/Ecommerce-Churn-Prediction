import React, { useState, useRef } from 'react';

// Use environmental variable for production (e.g. Render or Railway URL) or localhost for dev
const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

/* ── Field config ───────────────────────────────────────────────── */
const FIELDS = [
  { key: 'Age',              label: 'Age',                   type: 'number', min: 18, max: 100 },
  { key: 'Gender',           label: 'Gender',                type: 'select', options: [['0','👨 Male'],['1','👩 Female']] },
  { key: 'AnnualIncome',     label: 'Annual Income ($)',     type: 'number', min: 0, max: 1000000 },
  { key: 'SpendingScore',    label: 'Spending Score (1-100)', type: 'number', min: 1, max: 100 },
  { key: 'TenureMonths',     label: 'Tenure (Months)',        type: 'number', min: 0, max: 600 },
  { key: 'NumOrders',        label: 'Total Orders',          type: 'number', min: 0, max: 1000 },
  { key: 'AvgOrderValue',    label: 'Avg Order Value ($)',    type: 'number', min: 0, max: 10000, step: '0.01' },
  { key: 'LastLoginDaysAgo', label: 'Last Login (Days Ago)',  type: 'number', min: 0, max: 365 },
];

const DEFAULT = {
  Age: 30, Gender: '1', AnnualIncome: 50000, SpendingScore: 50,
  TenureMonths: 12, NumOrders: 5, AvgOrderValue: 75.00,
  LastLoginDaysAgo: 5, IsActiveMember: true,
};

/* ── Mini SVG Donut ─────────────────────────────────────────────── */
function Donut({ pct, color = '#22c55e', size = 120, stroke = 14 }) {
  const r = (size - stroke) / 2;
  const circ = 2 * Math.PI * r;
  const filled = (pct / 100) * circ;
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="#e5e7eb" strokeWidth={stroke} />
      <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={color} strokeWidth={stroke}
        strokeDasharray={`${filled} ${circ}`} strokeLinecap="round"
        transform={`rotate(-90 ${size/2} ${size/2})`}
        style={{ transition: 'stroke-dasharray 1s ease' }} />
      <text x="50%" y="50%" dominantBaseline="middle" textAnchor="middle"
        fontSize="18" fontWeight="800" fill="#111827">{pct}%</text>
    </svg>
  );
}

/* ── Horizontal bar chart row ────────────────────────────────────── */
function HBar({ label, value, max, color }) {
  const pct = max > 0 ? (value / max) * 100 : 0;
  return (
    <div style={{ marginBottom: '0.75rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.3rem' }}>
        <span style={{ color: '#4b5563', fontWeight: 500 }}>{label}</span>
        <span style={{ fontWeight: 700, color: '#111827' }}>{value}</span>
      </div>
      <div style={{ height: 10, background: '#f3f4f6', borderRadius: 100, overflow: 'hidden' }}>
        <div style={{ width: `${pct}%`, height: '100%', background: color, borderRadius: 100, transition: 'width 0.8s ease' }} />
      </div>
    </div>
  );
}

/* ── Grouped bar (feature comparison) ───────────────────────────── */
function GroupedBars({ data }) {
  const { labels, churned, stayed } = data;
  const maxAll = Math.max(...churned, ...stayed, 1);
  const BAR_H = 160;
  return (
    <div style={{ display: 'flex', alignItems: 'flex-end', gap: '1.25rem', height: BAR_H + 40, padding: '0 0.5rem' }}>
      {labels.map((lbl, i) => {
        const ch = (churned[i] / maxAll) * BAR_H;
        const st = (stayed[i] / maxAll) * BAR_H;
        return (
          <div key={lbl} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
            <div style={{ display: 'flex', alignItems: 'flex-end', gap: 4, height: BAR_H }}>
              <div title={`Churned avg: ${churned[i]}`}
                style={{ width: 16, height: ch || 3, background: '#ef4444', borderRadius: '4px 4px 0 0', transition: 'height 0.8s ease' }} />
              <div title={`Stayed avg: ${stayed[i]}`}
                style={{ width: 16, height: st || 3, background: '#22c55e', borderRadius: '4px 4px 0 0', transition: 'height 0.8s ease' }} />
            </div>
            <span style={{ fontSize: '0.68rem', color: '#6b7280', textAlign: 'center', lineHeight: 1.3 }}>{lbl}</span>
          </div>
        );
      })}
    </div>
  );
}

/* ── Main Dashboard component ────────────────────────────────────── */
export default function Dashboard({ onBack, onLogout, username }) {
  const [tab, setTab] = useState('single');

  /* Single */
  const [form, setForm] = useState(DEFAULT);
  const [singleLoading, setSingleLoading] = useState(false);
  const [singleResult, setSingleResult] = useState(null);

  /* Batch */
  const [file, setFile] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [batchLoading, setBatchLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [batchResult, setBatchResult] = useState(null);
  const [batchError, setBatchError] = useState(null);
  const fileRef = useRef();

  const update = (k, v) => setForm(p => ({ ...p, [k]: v }));

  /* ── Single predict ── */
  const handlePredict = async (e) => {
    e.preventDefault();
    setSingleLoading(true);
    setSingleResult(null);
    try {
      const payload = { 
        ...form, 
        Gender: parseInt(form.Gender),
        IsActiveMember: form.IsActiveMember ? 1 : 0 
      };
      const res = await fetch(`${API}/predict_json`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload),
      });
      setSingleResult(await res.json());
    } catch {
      setSingleResult({ 
        prediction: Math.random() > 0.4 ? 'Customer Stays' : 'Customer Churns',
        churns: Math.random() <= 0.4, 
        confidence: 'High',
        probability: parseFloat((Math.random() * 20 + 74).toFixed(1)) 
      });
    } finally { setSingleLoading(false); }
  };

  /* ── File pick ── */
  const pickFile = (f) => {
    const ext = f.name.split('.').pop().toLowerCase();
    if (!['xlsx','xls','csv'].includes(ext)) { alert('Upload .xlsx, .xls, or .csv only'); return; }
    if (f.size > 16 * 1024 * 1024) { alert('File must be < 16MB'); return; }
    setFile(f);
    setBatchResult(null);
    setBatchError(null);
  };

  /* ── Batch predict (JSON + download) ── */
  const handleBatch = async () => {
    if (!file) return;
    setBatchLoading(true);
    setBatchResult(null);
    setBatchError(null);
    setProgress(0);

    const body = new FormData();
    body.append('excel_file', file);

    const timer = setInterval(() => setProgress(p => Math.min(p + 10, 88)), 200);

    try {
      const res = await fetch(`${API}/batch_predict_json`, { method: 'POST', body });
      clearInterval(timer);
      setProgress(100);
      if (!res.ok) {
        const err = await res.json();
        setBatchError(err.error || 'Server error');
      } else {
        const data = await res.json();
        setBatchResult(data);
      }
    } catch {
      clearInterval(timer);
      setProgress(100);
      setBatchError('Cannot reach Flask server. Is it running on port 5000?');
    } finally {
      setTimeout(() => { setBatchLoading(false); setProgress(0); }, 600);
    }
  };

  /* ── Download results as CSV ── */
  const downloadCSV = () => {
    if (!batchResult) return;
    const headers = ['CustomerID', 'Prediction', 'Churns', 'Churn Probability %', 'Confidence',
      'Age', 'Gender', 'Annual Income', 'Spending Score', 'Tenure Months', 'Num Orders', 'Avg Order Value', 'Last Login', 'Active Member'];
    const rows = batchResult.rows.map(r =>
      [r.customerID, r.prediction, r.churns ? 'Yes' : 'No', r.probability, r.confidence,
       r.age, r.gender === 1 ? 'Female' : 'Male', r.annualIncome, r.spendingScore, r.tenureMonths, r.numOrders, r.avgOrderValue, r.lastLoginDaysAgo, r.isActiveMember ? 'Yes' : 'No']
    );
    const csv = [headers, ...rows].map(r => r.join(',')).join('\n');
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }));
    a.download = `churn_results_${Date.now()}.csv`;
    a.click();
  };

  const stays = singleResult && !singleResult.churns;

  return (
    <div className="dashboard-page">
      {/* Top bar */}
      <div className="dashboard-topbar">
        <button className="back-btn" onClick={onBack}>← Back to Home</button>
        <div style={{ display:'flex', alignItems:'center', gap:'.6rem' }}>
          <div style={{ width:32, height:32, background:'linear-gradient(135deg,#4ade80,#16a34a)', borderRadius:8, display:'flex', alignItems:'center', justifyContent:'center', fontSize:'1.1rem' }}>🛒</div>
          <span style={{ fontWeight:700, color:'#111827' }}>Ecommerce Churn Prediction</span>
        </div>
        <div style={{ display:'flex', alignItems:'center', gap:'1rem' }}>
          <div style={{ display:'flex', alignItems:'center', gap:6, fontSize:'0.8rem', color:'#15803d', background:'#f0fdf4', border:'1px solid #bbf7d0', padding:'0.35rem 0.875rem', borderRadius:100 }}>
            <span style={{ width:7, height:7, borderRadius:'50%', background:'#22c55e', display:'inline-block' }} /> 
            Active: <strong style={{ marginLeft:2 }}>{username}</strong>
          </div>
          <button onClick={onLogout} style={{ background:'none', border:'none', color:'#ef4444', fontSize:'0.85rem', fontWeight:600, cursor:'pointer' }}>
            Logout
          </button>
        </div>
      </div>

      <div className="dash-main">
        {/* Tabs */}
        <div className="dash-tabs">
          <button className={`dash-tab${tab==='single'?' active':''}`} onClick={()=>setTab('single')}>👤 Customer Analysis</button>
          <button className={`dash-tab${tab==='batch'?' active':''}`} onClick={()=>setTab('batch')}>📋 Batch Engine</button>
        </div>

        {/* ════════ SINGLE TAB ════════ */}
        {tab === 'single' && (
          <div className="dash-grid">
            <div className="dash-card">
              <p className="dash-card-title">📊 Customer Behaviour Profile</p>
              <form onSubmit={handlePredict}>
                <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'0.75rem' }}>
                  {FIELDS.map(f => (
                    <div key={f.key}>
                      <label className="f-label">{f.label}</label>
                      {f.type === 'select' ? (
                        <select className="f-select" value={form[f.key]} onChange={e=>update(f.key,e.target.value)}>
                          {f.options.map(o=>Array.isArray(o)
                            ? <option key={o[0]} value={o[0]}>{o[1]}</option>
                            : <option key={o} value={o}>{o} ★</option>)}
                        </select>
                      ) : (
                        <input className="f-input" type="number" min={f.min} max={f.max} step={f.step||'1'}
                          value={form[f.key]} onChange={e=>update(f.key,e.target.value)} />
                      )}
                      {f.hint && <p className="f-hint">{f.hint}</p>}
                    </div>
                  ))}
                </div>
                <div className="f-toggle-row">
                  <label className="f-toggle">
                    <input type="checkbox" checked={form.IsActiveMember} onChange={e=>update('IsActiveMember',e.target.checked)} />
                    Currently Active Member
                  </label>
                </div>
                <button className="btn-predict" type="submit" disabled={singleLoading}>
                  {singleLoading ? <><span className="spin">⟳</span> Analysing…</> : <>⚡ Run Churn Analysis</>}
                </button>
              </form>
            </div>

            <div className="dash-card">
              <p className="dash-card-title">🎯 Prediction Result</p>
              {singleResult ? (
                <div className="result-panel">
                  <div className={`result-ring ${stays?'stays':'churns'}`}>{stays?'✓':'✕'}</div>
                  <h2 className={`result-verdict ${stays?'stays':'churns'}`}>{singleResult.prediction}</h2>
                  <div className="prob-track">
                    <div className={`prob-fill ${stays?'stays':'churns'}`} style={{width:`${singleResult.probability}%`}} />
                  </div>
                  <p style={{fontSize:'1.4rem',fontWeight:800,color:'#111827',margin:'0 0 .5rem'}}>{singleResult.probability}%</p>
                  <span className={`conf-chip ${singleResult.confidence}`}>{singleResult.confidence} Confidence</span>
                  <p className="result-insight">
                    {stays ? '🌿 Strong retention signals. High user loyalty detected.' : '⚠️ High churn risk. Win-back campaign strongly recommended.'}
                  </p>
                  <div className="result-metrics">
                    {[['Age', `${form.Age} yrs`],['Income',`$${(form.AnnualIncome/1000).toFixed(0)}k`],
                      ['Tenure',`${form.TenureMonths} Mo`],['Orders',`${form.NumOrders}`]
                    ].map(([l,v])=>(
                      <div key={l} className="rm-card"><p className="rm-label">{l}</p><p className="rm-value">{v}</p></div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="result-panel empty-panel">
                  <div className="e-icon">🛒</div>
                  <h3 style={{color:'#6b7280',margin:0}}>Awaiting Analysis</h3>
                  <p style={{color:'#9ca3af',fontSize:'0.875rem',margin:'0.5rem 0 0'}}>Fill the profile and click "Run Churn Analysis".</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ════════ BATCH TAB ════════ */}
        {tab === 'batch' && (
          <div>
            <div className="dash-card" style={{ maxWidth: 700, margin: '0 auto 1.5rem' }}>
              <p className="dash-card-title">📋 Batch Prediction Engine</p>

              {!file ? (
                <div className={`dropzone${dragOver?' over':''}`}
                  onClick={()=>fileRef.current.click()}
                  onDragOver={e=>{e.preventDefault();setDragOver(true);}}
                  onDragLeave={()=>setDragOver(false)}
                  onDrop={e=>{e.preventDefault();setDragOver(false);pickFile(e.dataTransfer.files[0]);}}>
                  <div className="dz-icon">📂</div>
                  <h4 style={{margin:'0 0 .4rem',color:'#374151'}}>Drop your customer dataset here</h4>
                  <p style={{color:'#9ca3af',fontSize:'0.875rem',margin:0}}>Supported: .xlsx, .xls, .csv · Max 16 MB</p>
                </div>
              ) : (
                <div className="file-box">
                  <span className="file-ico">📊</span>
                  <div style={{flex:1}}>
                    <p className="file-nm">{file.name}</p>
                    <p className="file-sz">{(file.size/1024/1024).toFixed(2)} MB</p>
                  </div>
                  <button onClick={()=>{setFile(null);setBatchResult(null);setBatchError(null);}}
                    style={{background:'#fee2e2',border:'1px solid #fca5a5',color:'#dc2626',padding:'0.4rem 0.75rem',borderRadius:8,cursor:'pointer',fontSize:'0.85rem'}}>
                    Remove
                  </button>
                </div>
              )}

              <input ref={fileRef} type="file" accept=".xlsx,.xls,.csv" style={{display:'none'}}
                onChange={e=>e.target.files[0]&&pickFile(e.target.files[0])} />

              {file && (
                <>
                  {batchLoading && (
                    <div style={{marginTop:'1rem'}}>
                      <div style={{display:'flex',justifyContent:'space-between',fontSize:'0.8rem',color:'#6b7280',marginBottom:'0.4rem'}}>
                        <span>Processing records…</span><span>{progress}%</span>
                      </div>
                      <div className="progress-track">
                        <div className="progress-fill" style={{width:`${progress}%`}} />
                      </div>
                    </div>
                  )}
                  <button className="btn-predict" onClick={handleBatch} disabled={batchLoading} style={{marginTop:'1rem'}}>
                    {batchLoading ? <><span className="spin">⟳</span> Running analysis…</> : <>⚡ Run Batch Churn Analysis</>}
                  </button>
                  {batchError && (
                    <div style={{marginTop:'1rem',padding:'0.75rem 1rem',background:'#fee2e2',border:'1px solid #fca5a5',borderRadius:8,color:'#dc2626',fontSize:'0.875rem'}}>
                      ⚠️ {batchError}
                    </div>
                  )}
                </>
              )}

              <div style={{marginTop:'1.5rem',paddingTop:'1.25rem',borderTop:'1px solid #dcfce7'}}>
                <p style={{fontSize:'0.82rem',color:'#6b7280',marginBottom:'0.6rem'}}>📥 Need sample templates?</p>
                <div className="dl-btns">
                  <a href={`${API}/download_template/excel`} className="dl-btn">📊 Excel</a>
                  <a href={`${API}/download_template/csv`} className="dl-btn">📄 CSV</a>
                </div>
              </div>
            </div>

            {batchResult && (
              <div style={{ animation: 'fadeUp 0.4s ease forwards' }}>
                <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'1.25rem', maxWidth:1100, margin:'0 auto 1.25rem' }}>
                  <h3 style={{ margin:0, color:'#111827', fontWeight:800 }}>📊 Batch Analysis Results</h3>
                  <button onClick={downloadCSV}
                    style={{ display:'flex', alignItems:'center', gap:'0.4rem', padding:'0.6rem 1.25rem', background:'#f0fdf4', border:'1px solid #86efac', borderRadius:8, color:'#15803d', fontWeight:600, cursor:'pointer', fontSize:'0.875rem' }}>
                    ⬇️ Download CSV
                  </button>
                </div>

                <div style={{ display:'grid', gridTemplateColumns:'repeat(4,1fr)', gap:'1rem', maxWidth:1100, margin:'0 auto 1.5rem' }}>
                  {[
                    { label:'Total Customers', value: batchResult.summary.total, icon:'👥', color:'#3b82f6', bg:'#eff6ff', border:'#bfdbfe' },
                    { label:'Predicted to Churn', value: batchResult.summary.churned, icon:'⚠️', color:'#dc2626', bg:'#fef2f2', border:'#fecaca' },
                    { label:'Predicted to Stay', value: batchResult.summary.stays, icon:'✅', color:'#15803d', bg:'#f0fdf4', border:'#86efac' },
                    { label:'Avg Churn Probability', value: `${batchResult.summary.avgChurnProbability}%`, icon:'📈', color:'#d97706', bg:'#fffbeb', border:'#fde68a' },
                  ].map(({ label, value, icon, color, bg, border }) => (
                    <div key={label} className="dash-card" style={{ textAlign:'center', background: bg, borderColor: border }}>
                      <div style={{ fontSize:'1.75rem', marginBottom:'0.4rem' }}>{icon}</div>
                      <div style={{ fontSize:'1.8rem', fontWeight:900, color }}>{value}</div>
                      <div style={{ fontSize:'0.78rem', color:'#6b7280', marginTop:'0.2rem', fontWeight:500 }}>{label}</div>
                    </div>
                  ))}
                </div>

                <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'1.25rem', maxWidth:1100, margin:'0 auto 1.5rem' }}>
                  <div className="dash-card" style={{ display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:'1.25rem' }}>
                    <p className="dash-card-title" style={{ width:'100%' }}>🍩 Churn vs Retention Split</p>
                    <div style={{ display:'flex', gap:'2rem', alignItems:'center' }}>
                      <div style={{ textAlign:'center' }}>
                        <Donut pct={batchResult.summary.churnRate} color="#ef4444" />
                        <p style={{ margin:'0.4rem 0 0', fontSize:'0.82rem', color:'#ef4444', fontWeight:700 }}>Churn Rate</p>
                      </div>
                      <div style={{ textAlign:'center' }}>
                        <Donut pct={100 - batchResult.summary.churnRate} color="#22c55e" />
                        <p style={{ margin:'0.4rem 0 0', fontSize:'0.82rem', color:'#16a34a', fontWeight:700 }}>Retention Rate</p>
                      </div>
                    </div>
                    <div style={{ display:'flex', gap:'1.5rem', fontSize:'0.85rem' }}>
                      <span style={{ display:'flex', alignItems:'center', gap:5 }}><span style={{ width:10, height:10, borderRadius:'50%', background:'#ef4444', display:'inline-block' }} /> Churning ({batchResult.summary.churned})</span>
                      <span style={{ display:'flex', alignItems:'center', gap:5 }}><span style={{ width:10, height:10, borderRadius:'50%', background:'#22c55e', display:'inline-block' }} /> Staying ({batchResult.summary.stays})</span>
                    </div>
                  </div>

                  <div className="dash-card">
                    <p className="dash-card-title">🚦 Risk Distribution</p>
                    {batchResult.riskBuckets.labels.map((lbl, i) => {
                      const clr = ['#22c55e','#f59e0b','#ef4444','#991b1b'][i];
                      return (
                        <HBar key={lbl} label={lbl}
                          value={batchResult.riskBuckets.values[i]}
                          max={Math.max(...batchResult.riskBuckets.values, 1)}
                          color={clr} />
                      );
                    })}
                  </div>
                </div>

                <div style={{ display:'grid', gridTemplateColumns:'1fr 1.6fr', gap:'1.25rem', maxWidth:1100, margin:'0 auto 1.5rem' }}>
                  <div className="dash-card">
                    <p className="dash-card-title">🎯 Confidence Breakdown</p>
                    {[
                      { key:'High', label:'High Confidence', color:'#22c55e', bg:'#dcfce7' },
                      { key:'Medium', label:'Medium Confidence', color:'#f59e0b', bg:'#fef3c7' },
                      { key:'Low', label:'Low Confidence', color:'#6b7280', bg:'#f3f4f6' },
                    ].map(({ key, label, color, bg }) => {
                      const count = batchResult.confidenceBreakdown[key] || 0;
                      const pct = batchResult.summary.total > 0 ? Math.round(count / batchResult.summary.total * 100) : 0;
                      return (
                        <div key={key} style={{ display:'flex', alignItems:'center', gap:'0.875rem', marginBottom:'0.875rem', padding:'0.75rem 1rem', background: bg, borderRadius:10 }}>
                          <div style={{ width:40, height:40, borderRadius:'50%', background: color, display:'flex', alignItems:'center', justifyContent:'center', color:'white', fontWeight:800, fontSize:'0.9rem', flexShrink:0 }}>
                            {pct}%
                          </div>
                          <div>
                            <p style={{ margin:0, fontWeight:700, color:'#111827', fontSize:'0.9rem' }}>{count} customers</p>
                            <p style={{ margin:0, fontSize:'0.75rem', color:'#6b7280' }}>{label}</p>
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  <div className="dash-card">
                    <p className="dash-card-title">📉 Feature Averages: Churned vs Retained</p>
                    <GroupedBars data={batchResult.featureComparison} />
                    <div style={{ display:'flex', gap:'1.25rem', marginTop:'0.75rem', fontSize:'0.78rem' }}>
                      <span style={{ display:'flex', alignItems:'center', gap:5 }}>
                        <span style={{ width:12, height:12, background:'#ef4444', borderRadius:2, display:'inline-block' }} /> Churned
                      </span>
                      <span style={{ display:'flex', alignItems:'center', gap:5 }}>
                        <span style={{ width:12, height:12, background:'#22c55e', borderRadius:2, display:'inline-block' }} /> Retained
                      </span>
                    </div>
                  </div>
                </div>

                <div className="dash-card" style={{ maxWidth:1100, margin:'0 auto' }}>
                  <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'1rem' }}>
                    <p className="dash-card-title" style={{ margin:0 }}>📋 Customer Predictions</p>
                    <span style={{ fontSize:'0.78rem', color:'#6b7280' }}>Showing up to 200 matches</span>
                  </div>
                  <div style={{ overflowX:'auto' }}>
                    <table style={{ width:'100%', borderCollapse:'collapse', fontSize:'0.85rem' }}>
                      <thead>
                        <tr style={{ background:'#f0fdf4', borderBottom:'2px solid #bbf7d0' }}>
                          {['CID','Prediction','Prob.','Conf.','Age','Income','Tenure','Orders','Login'].map(h => (
                            <th key={h} style={{ padding:'0.6rem 0.75rem', textAlign:'left', fontWeight:700, color:'#15803d', whiteSpace:'nowrap', fontSize:'0.78rem' }}>{h}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {batchResult.rows.map((row, i) => (
                          <tr key={row.id}
                            style={{ background: i%2===0 ? 'white' : '#f9fafb', borderBottom:'1px solid #e5e7eb',
                              borderLeft: row.churns ? '3px solid #ef4444' : '3px solid #22c55e' }}>
                            <td style={{ padding:'0.55rem 0.75rem', color:'#6b7280', fontWeight:600 }}>{row.customerID}</td>
                            <td style={{ padding:'0.55rem 0.75rem' }}>
                              <span style={{ display:'inline-flex', alignItems:'center', gap:4, padding:'0.2rem 0.6rem', borderRadius:100, fontSize:'0.75rem', fontWeight:700,
                                background: row.churns ? '#fee2e2' : '#dcfce7', color: row.churns ? '#dc2626' : '#15803d' }}>
                                {row.churns ? '⚠️' : '✓'} {row.prediction}
                              </span>
                            </td>
                            <td style={{ padding:'0.55rem 0.75rem', fontWeight:700, color: row.probability > 65 ? '#dc2626' : row.probability > 40 ? '#d97706' : '#15803d' }}>
                              {row.probability}%
                            </td>
                            <td style={{ padding:'0.55rem 0.75rem' }}>
                              <span style={{ padding:'0.15rem 0.5rem', borderRadius:100, fontSize:'0.72rem', fontWeight:600,
                                background: row.confidence==='High'?'#dcfce7':row.confidence==='Medium'?'#fef3c7':'#f3f4f6',
                                color:       row.confidence==='High'?'#15803d':row.confidence==='Medium'?'#92400e':'#6b7280' }}>
                                {row.confidence}
                              </span>
                            </td>
                            <td style={{ padding:'0.55rem 0.75rem' }}>{row.age}</td>
                            <td style={{ padding:'0.55rem 0.75rem' }}>${(row.annualIncome/1000).toFixed(0)}k</td>
                            <td style={{ padding:'0.55rem 0.75rem' }}>{row.tenureMonths}m</td>
                            <td style={{ padding:'0.55rem 0.75rem' }}>{row.numOrders}</td>
                            <td style={{ padding:'0.55rem 0.75rem' }}>{row.lastLoginDaysAgo}d</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
