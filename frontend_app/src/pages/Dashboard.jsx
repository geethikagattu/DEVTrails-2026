import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ShieldAlert, AlertTriangle, CheckCircle, Zap } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const workerId = localStorage.getItem('worker_id');
  const navigate = useNavigate();

  const fetchDashboard = async () => {
    try {
      const res = await api.get(`/api/v1/workers/${workerId}/dashboard`);
      setData(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
    // Poll every 10 seconds for demo automatic claim updates
    const interval = setInterval(fetchDashboard, 10000);
    return () => clearInterval(interval);
  }, [workerId]);

  // Demo Trigger Action
  const triggerDemoEvent = async () => {
    try {
      await api.post(`/api/v1/claims/demo/trigger`, {
        worker_id: workerId,
        trigger_type: 'heavy_rain',
        trigger_value: 40.0
      });
      // Fetch instantly so UI updates
      fetchDashboard();
      alert("⚠️ Demo Event: Heavy Rain Auto-Claim triggered!");
    } catch(err) {
      alert("Trigger failed");
    }
  };

  if (loading) {
    return (
      <div className="flex-col gap-4">
        <div className="loader-skeleton" style={{ height: '150px' }}></div>
        <div className="loader-skeleton" style={{ height: '80px' }}></div>
      </div>
    );
  }

  if (!data) return <div>Failed to load data</div>;

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex-col gap-4">
      
      {/* Visual Protection Status Card */}
      <div className="glass-panel" style={{ 
        background: data.is_protected ? 'linear-gradient(135deg, rgba(16,185,129,0.2), rgba(16,185,129,0.05))' : 'linear-gradient(135deg, rgba(239,68,68,0.2), rgba(239,68,68,0.05))',
        border: `1px solid ${data.is_protected ? 'var(--success)' : 'var(--danger)'}`
      }}>
        <div className="flex-between">
          <div>
            <h2 style={{ color: data.is_protected ? 'var(--success)' : 'var(--danger)', marginBottom: '4px' }}>
              {data.is_protected ? 'Protected' : 'Unprotected'}
            </h2>
            <p className="text-muted">
              {data.is_protected ? `Active Plan: ${data.active_policy.plan.toUpperCase()}` : 'No active coverage'}
            </p>
          </div>
          {data.is_protected ? <CheckCircle size={40} color="var(--success)"/> : <AlertTriangle size={40} color="var(--danger)"/>}
        </div>
        
        {!data.is_protected && (
          <button className="btn btn-primary" style={{ marginTop: '16px' }} onClick={() => navigate('/quotes')}>
            Get Protected Now
          </button>
        )}
      </div>

      {/* Demo Developer Trigger (Hidden in prod, visible for demo) */}
      {data.is_protected && (
        <button className="btn" style={{ background: '#3b82f6', color: 'white' }} onClick={triggerDemoEvent}>
          <Zap size={18}/> Simulate Heavy Rain (Demo)
        </button>
      )}

      {/* Recent Claims UI */}
      <h3 style={{ marginTop: '16px' }}>Claim History</h3>
      {data.recent_claims.length === 0 ? (
        <p className="text-muted">No recent claims.</p>
      ) : (
        <div className="flex-col gap-3">
          {data.recent_claims.map(claim => (
            <div key={claim.id} className="glass-panel" style={{ padding: '16px' }}>
              <div className="flex-between" style={{ marginBottom: '8px' }}>
                <span className={`status-badge ${claim.status === 'approved' ? 'active' : claim.status === 'pending' ? 'pending' : 'inactive'}`}>
                  {claim.status.toUpperCase()}
                </span>
                <span style={{ fontWeight: 600 }}>₹{claim.payout_amount_paise / 100}</span>
              </div>
              <p style={{ fontSize: '14px' }}><ShieldAlert size={14} style={{ display: 'inline', marginRight: '4px' }}/>{claim.trigger_label} - Event detected</p>
            </div>
          ))}
        </div>
      )}
    </motion.div>
  );
}
