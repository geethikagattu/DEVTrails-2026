import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, KeyRound, ArrowRight } from 'lucide-react';
import api from '../api';

export default function Login() {
  const [phone, setPhone] = useState('9876543210'); 
  const [otp, setOtp] = useState('');
  const [step, setStep] = useState(1); // 1 = Phone, 2 = OTP
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSendOtp = async (e) => {
    e.preventDefault();
    if(phone.length < 10) {
        setError('Please enter a valid 10-digit phone number');
        return;
    }
    setLoading(true);
    setError('');
    
    try {
        const res = await api.post('/api/v1/workers/otp/send', { phone });
        // NOTE: For demo purposes we are showing the OTP visibly!
        alert(`DEMO MODE\n\nYour secure OTP is: ${res.data.demo_otp}`);
        setStep(2);
    } catch (err) {
        setError('Failed to send OTP. Check backend connection.');
    } finally {
        setLoading(false);
    }
  };

  const handleVerifyOtp = async (e) => {
    e.preventDefault();
    if(otp.length < 4) {
        setError('Please enter the 4-digit OTP');
        return;
    }
    setLoading(true);
    setError('');
    
    try {
      const res = await api.post(`/api/v1/workers/login`, { phone, otp_code: otp });
      localStorage.setItem('worker_id', res.data.id);
      navigate('/dashboard');
    } catch (err) {
      if(err.response?.status === 404) {
        setError('Phone number not found. Please register.');
      } else if (err.response?.status === 400) {
        setError('Invalid or expired OTP.');
      } else {
        setError('Login failed. Check connection.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container flex-col flex-center" style={{ padding: '20px' }}>
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-panel" 
        style={{ width: '100%', maxWidth: '400px', overflow: 'hidden' }}
      >
        <div className="flex-center" style={{ marginBottom: '24px' }}>
          <div style={{ background: 'var(--accent-glow)', padding: '16px', borderRadius: '50%' }}>
            {step === 1 ? <Shield size={40} className="text-accent" /> : <KeyRound size={40} className="text-accent" />}
          </div>
        </div>
        
        <h1 style={{ textAlign: 'center', marginBottom: '8px' }}>
            {step === 1 ? 'Welcome Back' : 'Verify Device'}
        </h1>
        <p style={{ textAlign: 'center', marginBottom: '32px' }} className="text-muted">
            {step === 1 ? 'Enter your registered number' : `Enter the 4-digit OTP sent to +91 ${phone}`}
        </p>

        {error && <p className="text-danger" style={{ marginBottom: '16px', textAlign: 'center' }}>{error}</p>}

        <AnimatePresence mode="wait">
            {step === 1 && (
                <motion.form key="phone-form" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} onSubmit={handleSendOtp} className="flex-col gap-4">
                  <div>
                    <input 
                      type="tel" 
                      className="input-field" 
                      value={phone}
                      onChange={(e) => setPhone(e.target.value.replace(/\D/g, ''))}
                      placeholder="e.g. 9876543210"
                      maxLength={10}
                      required
                    />
                  </div>

                  <button type="submit" className="btn btn-primary" disabled={loading}>
                    {loading ? 'Sending OTP...' : 'Send Secure OTP'}
                    {!loading && <ArrowRight size={18} />}
                  </button>
                </motion.form>
            )}

            {step === 2 && (
                <motion.form key="otp-form" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }} onSubmit={handleVerifyOtp} className="flex-col gap-4">
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
                    {loading ? 'Verifying...' : 'Verify & Login'}
                  </button>
                  
                  <button type="button" onClick={() => setStep(1)} className="btn btn-secondary" style={{ background: 'transparent', border: 'none', color: 'var(--text-tertiary)', fontSize: '14px', marginTop: '-8px' }}>
                     Re-enter Phone Number
                  </button>
                </motion.form>
            )}
        </AnimatePresence>

        {step === 1 && (
            <div style={{ textAlign: 'center', marginTop: '24px' }}>
            <p className="text-muted">New worker? <Link to="/register" className="text-accent" style={{ textDecoration: 'none' }}>Register here</Link></p>
            </div>
        )}
      </motion.div>
    </div>
  );
}
