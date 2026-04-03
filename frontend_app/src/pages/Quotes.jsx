import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Sparkles, ShieldCheck } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

export default function Quotes() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [purchasing, setPurchasing] = useState(false);
  const workerId = localStorage.getItem('worker_id');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchQuotes = async () => {
      try {
        const res = await api.get(`/api/v1/policies/quote/all/${workerId}`);
        setData(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchQuotes();
  }, [workerId]);

  const handlePurchase = async (plan) => {
    setPurchasing(true);
    try {
      await api.post(`/api/v1/policies/purchase`, { worker_id: workerId, plan });
      navigate('/dashboard'); // Go back to dashboard to see active policy
    } catch (err) {
      alert("Purchase failed");
    } finally {
      setPurchasing(false);
    }
  };

  if (loading) {
    return (
      <div className="flex-col gap-4">
        <div className="flex-center" style={{ padding: '40px' }}>
          <div className="loader-skeleton" style={{ width: '100%', height: '200px' }}></div>
        </div>
      </div>
    );
  }

  if (!data) return <div>Failed to load AI quotes</div>;

  const plans = [data.quotes.basic, data.quotes.standard, data.quotes.premium];

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex-col gap-4">
      
      <div style={{ textAlign: 'center', marginBottom: '16px' }}>
        <h2 style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
          <Sparkles className="text-accent" /> AI Dynamic Pricing
        </h2>
        <p className="text-muted" style={{ marginTop: '8px' }}>
          Prices adapted for your zone risk score ({data.zone_risk_score}/100)
        </p>
      </div>

      <div className="flex-col gap-4">
        {plans.map((plan, i) => (
          <motion.div 
            key={plan.plan}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.1 }}
            className="glass-panel"
            style={{ 
              border: plan.plan === 'premium' ? '1px solid var(--accent-primary)' : 'var(--glass-border)',
              position: 'relative',
              overflow: 'hidden'
            }}
          >
            {plan.plan === 'premium' && (
              <div style={{ position: 'absolute', top: 0, right: 0, background: 'var(--accent-primary)', color: 'white', padding: '4px 12px', fontSize: '10px', fontWeight: 'bold', borderBottomLeftRadius: '12px' }}>
                RECOMMENDED
              </div>
            )}
            
            <div className="flex-between">
              <h3 style={{ textTransform: 'capitalize' }}>{plan.plan} Plan</h3>
              <h2 className="text-accent">₹{plan.adjusted_premium_rs}/wk</h2>
            </div>
            
            <div style={{ margin: '16px 0', padding: '12px', background: 'var(--bg-secondary)', borderRadius: '8px' }}>
              <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}><b>AI Adjustment:</b> {plan.risk_explanation}</p>
            </div>
            
            <div className="flex-between" style={{ fontSize: '14px', marginBottom: '16px' }}>
              <span>Payout per day:</span>
              <span style={{ fontWeight: 'bold' }}>₹{plan.coverage_per_day_rs}</span>
            </div>

            <button 
              className={`btn ${plan.plan === 'premium' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => handlePurchase(plan.plan)}
              disabled={purchasing}
            >
              <ShieldCheck size={18} /> Buy {plan.plan.toUpperCase()}
            </button>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
