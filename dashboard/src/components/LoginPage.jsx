import { useState } from 'react';

const PASSKEY = '100120';
const AUTH_KEY = 'healthcare_research_auth';

export function isAuthenticated() {
  return sessionStorage.getItem(AUTH_KEY) === 'true';
}

export function clearAuth() {
  sessionStorage.removeItem(AUTH_KEY);
}

export default function LoginPage({ onSuccess }) {
  const [passkey, setPasskey] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    if (passkey.trim() === PASSKEY) {
      setLoading(true);
      sessionStorage.setItem(AUTH_KEY, 'true');
      setTimeout(() => onSuccess(), 400);
      return;
    }

    setError('Invalid passkey. Please try again.');
    setPasskey('');
  };

  return (
    <div className="login-page">
      <div className="login-bg">
        <div className="login-bg-pattern" />
        <div className="login-bg-icons">
          <span>🩺</span>
          <span>💊</span>
          <span>❤️</span>
          <span>🏥</span>
          <span>📊</span>
          <span>🔬</span>
        </div>
      </div>

      <div className="login-card">
        <div className="login-logo">
          <div className="login-logo-icon">+</div>
        </div>
        <h1>Healthcare Research</h1>
        <p className="login-subtitle">Literature Review Analytics Portal</p>

        <div className="login-user">
          <div className="login-user-avatar">AY</div>
          <div>
            <strong>Aakash Yadav</strong>
            <span>Dalhousie University · Student Research</span>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <label htmlFor="passkey">Enter Passkey</label>
          <input
            id="passkey"
            type="password"
            inputMode="numeric"
            autoComplete="off"
            placeholder="••••••"
            value={passkey}
            onChange={(e) => setPasskey(e.target.value)}
            disabled={loading}
            autoFocus
          />
          {error && <p className="login-error">{error}</p>}
          <button type="submit" className="login-btn" disabled={loading || !passkey.trim()}>
            {loading ? 'Opening dashboard…' : 'Access Dashboard'}
          </button>
        </form>

        <p className="login-footer">Secure access · Healthcare literature review data</p>
      </div>
    </div>
  );
}
