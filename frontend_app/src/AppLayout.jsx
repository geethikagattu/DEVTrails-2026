import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { User, Home, Shield, LogOut } from 'lucide-react';
import { useEffect } from 'react';

export default function AppLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const workerId = localStorage.getItem('worker_id');

  useEffect(() => {
    if (!workerId && location.pathname !== '/login' && location.pathname !== '/register') {
      navigate('/login');
    } else if (workerId && (location.pathname === '/login' || location.pathname === '/register')) {
      navigate('/dashboard');
    }
  }, [workerId, location.pathname, navigate]);

  const handleLogout = () => {
    localStorage.removeItem('worker_id');
    navigate('/login');
  };

  if (!workerId && (location.pathname === '/login' || location.pathname === '/register')) return <Outlet />; 


  return (
    <div className="app-container">
      <div style={{ padding: '20px 20px 80px 20px' }}>
        <header className="flex-between" style={{ marginBottom: '24px' }}>
          <h2 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Shield className="text-accent" /> ShieldRun
          </h2>
          <button onClick={handleLogout} style={{ background: 'transparent', border: 'none', color: 'var(--text-tertiary)' }}>
            <LogOut size={20} />
          </button>
        </header>

        <Outlet />
      </div>

      {/* Bottom Nav */}
      <nav style={{
        position: 'fixed',
        bottom: 0,
        width: '100%',
        maxWidth: '480px',
        backgroundColor: 'var(--glass-bg)',
        backdropFilter: 'blur(20px)',
        borderTop: 'var(--glass-border)',
        display: 'flex',
        justifyContent: 'space-around',
        padding: '16px 0',
        zIndex: 50
      }}>
        <button onClick={() => navigate('/dashboard')} style={{ background: 'transparent', border: 'none', color: 'var(--text-primary)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
          <Home size={24} />
          <span style={{ fontSize: '12px' }}>Home</span>
        </button>
        <button onClick={() => navigate('/quotes')} style={{ background: 'transparent', border: 'none', color: 'var(--text-primary)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
          <Shield size={24} />
          <span style={{ fontSize: '12px' }}>Protection</span>
        </button>
        <button onClick={() => navigate('/profile')} style={{ background: 'transparent', border: 'none', color: 'var(--text-primary)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
          <User size={24} />
          <span style={{ fontSize: '12px' }}>Profile</span>
        </button>
      </nav>
    </div>
  );
}
