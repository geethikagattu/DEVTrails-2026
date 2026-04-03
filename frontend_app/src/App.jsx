import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from './AppLayout';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Quotes from './pages/Quotes';
import Profile from './pages/Profile';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          {/* Public */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* Protected (Handled by AppLayout logic) */}
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/quotes" element={<Quotes />} />
          <Route path="/profile" element={<Profile />} />
          
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
