import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  LineChart, Line, AreaChart, Area 
} from 'recharts';
import { 
  ShieldAlert, Activity, Map as MapIcon, 
  TrendingUp, Users, AlertCircle, CheckCircle2, 
  Clock, ArrowUpRight, Zap
} from 'lucide-react';
import api from '../api';

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [fraudRings, setFraudRings] = useState([]);
  const [heatmap, setHeatmap] = useState([]);
  const [payouts, setPayouts] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchAdminData = async () => {
    try {
      const [sRes, fRes, hRes, pRes] = await Promise.all([
        api.get('/api/v1/claims/admin/stats'),
        api.get('/api/v1/claims/admin/fraud-rings'),
        api.get('/api/v1/claims/admin/heatmap'),
        api.get('/api/v1/claims/admin/payouts')
      ]);
      setStats(sRes.data);
      setFraudRings(fRes.data);
      setHeatmap(hRes.data);
      setPayouts(pRes.data);
    } catch (err) {
      console.error("Failed to fetch admin data", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAdminData();
    const interval = setInterval(fetchAdminData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="p-8 text-center text-muted">Loading AI Analytics...</div>;

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }} 
      animate={{ opacity: 1, y: 0 }} 
      className="admin-dashboard-container"
      style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '24px', maxWidth: '1200px', margin: '0 auto' }}
    >
      <header className="flex-between">
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 700, color: 'var(--text-primary)' }}>Phase 3 Orchestrator</h1>
          <p className="text-muted">Real-time AI Monitoring & Decision Engine</p>
        </div>
        <div className="status-badge active">
          <Activity size={14} style={{ marginRight: '6px' }} /> LIVE ENGINE
        </div>
      </header>

      {/* Top Stats Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
        {[
          { label: 'Total Workers', val: stats?.total_workers, icon: <Users />, color: '#3b82f6' },
          { label: 'Active Policies', val: stats?.active_policies, icon: <ShieldAlert />, color: '#10b981' },
          { label: 'Total Paid Out', val: `₹${stats?.total_paid_out_rs}`, icon: <Zap />, color: '#f59e0b' },
          { label: 'Approval Rate', val: `${stats?.approval_rate_pct}%`, icon: <TrendingUp />, color: '#8b5cf6' }
        ].map((stat, i) => (
          <div key={i} className="glass-panel" style={{ padding: '20px', borderLeft: `4px solid ${stat.color}` }}>
            <div style={{ color: 'var(--text-tertiary)', display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              {stat.icon} <span style={{ fontSize: '12px', fontWeight: 600, letterSpacing: '0.05em' }}>{stat.label.toUpperCase()}</span>
            </div>
            <div style={{ fontSize: '24px', fontWeight: 700 }}>{stat.val}</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '24px' }}>
        
        {/* Predictive Reserve Analysis */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div className="flex-between" style={{ marginBottom: '20px' }}>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '10px' }}> <TrendingUp size={20} color="#8b5cf6" /> Predictive Reserve Forecasting</h3>
            <span className="text-muted" style={{ fontSize: '12px' }}>Next 7 Days</span>
          </div>
          <div style={{ height: '250px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={[
                { day: 'Mon', prob: 0.12, claims: 2 },
                { day: 'Tue', prob: 0.18, claims: 5 },
                { day: 'Wed', prob: 0.45, claims: 15 },
                { day: 'Thu', prob: 0.78, claims: 32 },
                { day: 'Fri', prob: 0.65, claims: 24 },
                { day: 'Sat', prob: 0.32, claims: 12 },
                { day: 'Sun', prob: 0.15, claims: 4 },
              ]}>
                <defs>
                  <linearGradient id="colorProb" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="day" stroke="var(--text-tertiary)" fontSize={12} />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'rgba(23, 23, 23, 0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                />
                <Area type="monotone" dataKey="prob" stroke="#8b5cf6" fillOpacity={1} fill="url(#colorProb)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <p className="text-muted" style={{ fontSize: '13px', marginTop: '16px' }}>
            <AlertCircle size={14} style={{ display: 'inline', marginRight: '6px' }}/> 
            AI suggests increasing liquidity reserve by <strong>₹45,000</strong> for high-risk rainfall on Thursday.
          </p>
        </div>

        {/* Fraud Detection: GNN Ring Alerts */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div className="flex-between" style={{ marginBottom: '20px' }}>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '10px' }}> <Activity size={20} color="#ef4444" /> AI Fraud Discovery (GNN)</h3>
            <span style={{ fontSize: '11px', background: 'rgba(239,68,68,0.1)', color: '#ef4444', padding: '2px 8px', borderRadius: '12px' }}>{fraudRings.length} Clusters Detected</span>
          </div>
          
          <div className="flex-col gap-3">
            {fraudRings.length === 0 ? (
              <div className="text-center text-muted" style={{ padding: '40px' }}>No fraud rings detected in current cycle.</div>
            ) : (
              fraudRings.map(ring => (
                <div key={ring.id} style={{ padding: '16px', backgroundColor: 'rgba(255,255,255,0.02)', borderRadius: '12px', border: '1px solid rgba(239,68,68,0.2)' }}>
                  <div className="flex-between">
                    <span style={{ fontWeight: 600, fontSize: '14px' }}>Ring Cluster ID: ...{ring.id.slice(-6)}</span>
                    <span style={{ color: '#ef4444', fontWeight: 700 }}>{Math.round(ring.score * 100)}% Match</span>
                  </div>
                  <div style={{ display: 'flex', gap: '6px', marginTop: '10px' }}>
                    {ring.claims.map((cId, idx) => (
                      <span key={idx} style={{ fontSize: '10px', background: 'rgba(255,255,255,0.05)', padding: '2px 6px', borderRadius: '4px' }}>Claim #{cId.slice(-4)}</span>
                    ))}
                  </div>
                  <button className="btn" style={{ width: '100%', marginTop: '12px', padding: '8px', fontSize: '12px', background: '#ef4444', color: 'white' }}>
                    Suspend Cluster for Review
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Real-time Heatmap / Payout Feed */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <h3 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}> <MapIcon size={20} color="#10b981" /> Geographic Claim Intensity (Heatmap)</h3>
        <div style={{ height: '300px', backgroundColor: 'rgba(255,255,255,0.02)', borderRadius: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative', overflow: 'hidden' }}>
           {/* Placeholder for Leaflet/Mapbox until installed */}
           <div className="text-muted" style={{ textAlign: 'center' }}>
             <MapIcon size={48} style={{ opacity: 0.1, marginBottom: '12px' }} />
             <p>Rendering Real-time Heatmap for Zones {heatmap.map(h => h.zone).join(', ')}</p>
           </div>
           
           {/* Visual mock of heatmap nodes */}
           {heatmap.map((h, i) => (
             <motion.div 
               key={i}
               initial={{ scale: 0 }}
               animate={{ scale: 1 }}
               style={{ 
                 position: 'absolute', 
                 left: `${20 + (i * 15)}%`, 
                 top: `${40 + (i * 10)}%`,
                 width: `${20 + (h.intensity * 20)}px`,
                 height: `${20 + (h.intensity * 20)}px`,
                 backgroundColor: 'rgba(16, 185, 129, 0.4)',
                 borderRadius: '50%',
                 filter: 'blur(10px)',
                 boxShadow: '0 0 20px rgba(16, 185, 129, 0.2)'
               }}
             />
           ))}
        </div>
      </div>

      {/* Payout Transaction Feed */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <h3 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}> <Clock size={20} color="#f59e0b" /> Instant Payout Transaction Ledger</h3>
        <div className="table-responsive">
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ textAlign: 'left', color: 'var(--text-tertiary)', fontSize: '12px', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                <th style={{ padding: '12px 8px' }}>TXN ID</th>
                <th style={{ padding: '12px 8px' }}>CLAIM REF</th>
                <th style={{ padding: '12px 8px' }}>STATUS</th>
                <th style={{ padding: '12px 8px' }}>GATEWAY</th>
                <th style={{ padding: '12px 8px' }}>RETRIES</th>
              </tr>
            </thead>
            <tbody>
              {payouts.map(p => (
                <tr key={p.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.02)', fontSize: '14px' }}>
                  <td style={{ padding: '12px 8px', fontFamily: 'monospace' }}>{p.razorpay_txn_id}</td>
                  <td style={{ padding: '12px 8px' }}>...{p.claim_id.slice(-8)}</td>
                  <td style={{ padding: '12px 8px' }}>
                    <span className={`status-badge ${p.status === 'success' ? 'active' : 'inactive'}`} style={{ fontSize: '10px' }}>
                      {p.status.toUpperCase()}
                    </span>
                  </td>
                  <td style={{ padding: '12px 8px' }}>RAZORPAY_SB</td>
                  <td style={{ padding: '12px 8px' }}>{p.retry_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </motion.div>
  );
}
