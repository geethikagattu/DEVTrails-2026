import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { User, MapPin, Briefcase } from 'lucide-react';
import api from '../api';

export default function Profile() {
  const [worker, setWorker] = useState(null);
  const [loading, setLoading] = useState(true);
  const workerId = localStorage.getItem('worker_id');

  useEffect(() => {
    const fetchWorker = async () => {
      try {
        const res = await api.get(`/api/v1/workers/${workerId}`);
        setWorker(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchWorker();
  }, [workerId]);

  if (loading) {
    return (
      <div className="flex-col gap-4">
        <div className="loader-skeleton" style={{ height: '200px' }}></div>
      </div>
    );
  }

  if (!worker) return <div>Failed to load profile</div>;

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex-col gap-4">
      
      <div style={{ textAlign: 'center', marginBottom: '16px' }}>
        <h2 style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
          <User className="text-accent" /> Profile Settings
        </h2>
      </div>

      <div className="glass-panel text-center flex-col flex-center" style={{ padding: '32px 16px' }}>
         <div style={{ width: '80px', height: '80px', borderRadius: '50%', background: 'var(--bg-tertiary)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px' }}>
            <span style={{ fontSize: '32px', fontWeight: 'bold', color: 'var(--accent-primary)' }}>
                {worker.name.charAt(0).toUpperCase()}
            </span>
         </div>
         <h2 style={{ marginBottom: '4px' }}>{worker.name}</h2>
         <p className="text-muted">+91 {worker.phone}</p>
      </div>

      <div className="glass-panel flex-col gap-4">
         <div className="flex-between">
            <span className="flex-center gap-2 text-muted"><MapPin size={18}/> Zone Area</span>
            <span style={{ fontWeight: 600 }}>{worker.city} - {worker.zone_pincode}</span>
         </div>
         <div style={{ height: '1px', background: 'var(--border-color)' }}></div>
         <div className="flex-between">
            <span className="flex-center gap-2 text-muted"><Briefcase size={18}/> Platform</span>
            <span style={{ fontWeight: 600, textTransform: 'capitalize' }}>{worker.platform}</span>
         </div>
         <div style={{ height: '1px', background: 'var(--border-color)' }}></div>
         <div className="flex-between">
             <span className="text-muted" style={{ paddingLeft: '26px' }}>Daily Earnings</span>
             <span style={{ fontWeight: 600 }}>₹{worker.avg_daily_earnings}</span>
         </div>
      </div>
    </motion.div>
  );
}
