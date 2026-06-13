import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../../services/api';

const Register: React.FC = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await api.post('/api/v1/auth/signup', { name, email, password });
      
      // Auto-login: Store tokens and user info from signup response
      const { tokens, user: userData } = response.data;
      if (tokens && tokens.access_token) {
        localStorage.setItem('token', tokens.access_token);
        localStorage.setItem('refresh_token', tokens.refresh_token);
        localStorage.setItem('user', JSON.stringify(userData));
        navigate('/');
      } else {
        navigate('/login', { state: { message: 'Account created! Please sign in.' } });
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create account');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container" role="main">
      <div className="auth-card glass">
        <header>
          <h1 className="gradient-text">PulseTask</h1>
          <p className="subtitle">Start your enterprise collaboration</p>
        </header>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="name">Full Name</label>
            <input
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="John Doe"
              required
              aria-required="true"
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@company.com"
              required
              aria-required="true"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              aria-required="true"
              minLength={8}
            />
          </div>

          {error && <div className="error-message" role="alert">{error}</div>}

          <button 
            type="submit" 
            className="btn btn-primary btn-block" 
            disabled={loading}
            aria-busy={loading}
          >
            {loading ? 'Creating Account...' : 'Get Started'}
          </button>
        </form>

        <footer>
          <p>Already have an account? <Link to="/login">Sign In</Link></p>
        </footer>
      </div>
    </div>
  );
};

export default Register;
