import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { KeyRound, ArrowRight } from 'lucide-react';
import api from '../api';

export default function Register() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [step, setStep] = useState(1); 
  const [otp, setOtp] = useState('');
  
  const [formData, setFormData] = useState({
    name: 'Test Worker',
    phone: '',
    platform: 'zomato',
    platform_id: 'ZOM001',
    zone_pincode: '500032',
    city: 'Hyderabad',
    avg_daily_earnings: 500
  });

  const handleProcessForm = async (e) => {
      e.preventDefault();
      if(formData.phone.length < 10) {
          setError('Invalid phone number length');
          return;
      }
      setLoading(true);
      setError('');
      try {
          const res = await api.post('/api/v1/workers/otp/send', { phone: formData.phone });
          alert(`DEMO MODE\n\nYour secure OTP is: ${res.data.demo_otp}`);
          setStep(2);
      } catch (err) {
          setError('Failed to send OTP.');
      } finally {
          setLoading(false);
      }
  }

  const handleVerifyAndRegister = async (e) => {
    e.preventDefault();
    if(otp.length < 4) {
        setError("Invalid OTP");
        return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const payload = { ...formData, otp_code: otp };
      const res = await api.post('/api/v1/workers/register', payload);
      localStorage.setItem('worker_id', res.data.id);
      navigate('/dashboard');
    } catch (err) {
      if (err.response?.status === 400) {
          setError("Invalid or expired OTP");
      } else {
          setError(err.response?.data?.detail?.[0]?.msg || err.response?.data?.detail || 'Registration failed');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container" style={{ padding: '20px', minHeight: '100vh', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-panel">
        
        {step === 1 && (
            <motion.div key="form" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <h2 style={{ marginBottom: '8px' }}>Create Account</h2>
                <p style={{ marginBottom: '24px' }}>Join ShieldRun to protect your income.</p>

                {error && <p className="text-danger" style={{ marginBottom: '16px' }}>{error}</p>}

                <form onSubmit={handleProcessForm} className="flex-col gap-4">
                  <div>
                    <label className="text-muted">Full Name</label>
                    <input className="input-field" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} required/>
                  </div>
                  <div>
                    <label className="text-muted">Phone Number</label>
                    <input type="tel" className="input-field" placeholder="10 Digits" value={formData.phone} onChange={e => setFormData({...formData, phone: e.target.value.replace(/\D/g, '')})} maxLength={10} required/>
                  </div>
                  <div className="flex-between gap-4">
                     <div style={{ flex: 1 }}>
                       <label className="text-muted">Platform</label>
                       <select className="input-field" value={formData.platform} onChange={e => setFormData({...formData, platform: e.target.value})}>
                         <option value="zomato">Zomato</option>
                         <option value="swiggy">Swiggy</option>
                       </select>
                     </div>
                     <div style={{ flex: 1 }}>
                       <label className="text-muted">Pincode</label>
                       <input className="input-field" value={formData.zone_pincode} onChange={e => setFormData({...formData, zone_pincode: e.target.value})} required/>
                     </div>
                  </div>

                  <button type="submit" className="btn btn-primary" style={{ marginTop: '16px' }} disabled={loading}>
                    {loading ? 'Processing...' : 'Continue'}
                    {!loading && <ArrowRight size={18} />}
                  </button>
                </form>

                <p className="text-muted" style={{ textAlign: 'center', marginTop: '24px' }}>
                  Already registered? <Link to="/login" className="text-accent" style={{ textDecoration: 'none' }}>Login</Link>
                </p>
            </motion.div>
        )}

        {step === 2 && (
             <motion.div key="otp" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}>
                <div className="flex-center" style={{ marginBottom: '24px' }}>
                  <div style={{ background: 'var(--accent-glow)', padding: '16px', borderRadius: '50%' }}>
                    <KeyRound size={40} className="text-accent" />
                  </div>
                </div>
                
                <h1 style={{ textAlign: 'center', marginBottom: '8px' }}>Verify Number</h1>
                <p style={{ textAlign: 'center', marginBottom: '32px' }} className="text-muted">
                    Enter the 4-digit OTP sent to +91 {formData.phone}
                </p>
        
                {error && <p className="text-danger" style={{ marginBottom: '16px', textAlign: 'center' }}>{error}</p>}
                
                <form onSubmit={handleVerifyAndRegister} className="flex-col gap-4">
                  <div className="flex-center">
                    <input 
                      type="text" 
                      className="input-field" 
                      style={{ fontSize: '24px', letterSpacing: '12px', textAlign: 'center', fontWeight: 'bold' }}
                      value={otp}
                      onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                      placeholder="••••"
                      maxLength={4}
                      autoFocus
                      required
                    />
                  </div>

                  <button type="submit" className="btn btn-primary" disabled={loading}>
                    {loading ? 'Verifying...' : 'Verify & Register'}
                  </button>
                  
                  <button type="button" onClick={() => setStep(1)} className="btn btn-secondary" style={{ background: 'transparent', border: 'none', color: 'var(--text-tertiary)', fontSize: '14px', marginTop: '-8px' }}>
                     Back
                  </button>
                </form>
             </motion.div>
        )}

      </motion.div>
    </div>
  );
}
