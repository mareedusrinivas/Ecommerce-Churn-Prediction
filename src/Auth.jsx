import React, { useState } from 'react';

export default function Auth({ onLogin }) {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    // Simulate network delay for premium feel
    setTimeout(() => {
      try {
        const storedUsers = JSON.parse(localStorage.getItem('churn_app_users') || '{}');

        if (isLogin) {
          // LOGIN LOGIC
          if (!storedUsers[username] || storedUsers[username] !== password) {
            throw new Error('Invalid username or password. Please try again.');
          }
          // Set as currently logged in
          localStorage.setItem('churn_app_current_user', username);
          onLogin(username);
        } else {
          // REGISTRATION LOGIC
          if (storedUsers[username]) {
            throw new Error('This username is already taken. Try another?');
          }
          
          storedUsers[username] = password;
          localStorage.setItem('churn_app_users', JSON.stringify(storedUsers));
          
          alert('Account created successfully! Now you can login.');
          setIsLogin(true);
          setUsername('');
          setPassword('');
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }, 600);
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-header">
          <div className="auth-logo">🛒</div>
          <h1>{isLogin ? 'Welcome Back' : 'Create Account'}</h1>
          <p>{isLogin ? 'Enter your credentials to continue' : 'Join the ecommerce churn network'}</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label>Username</label>
            <input 
              type="text" 
              required 
              value={username} 
              onChange={e => setUsername(e.target.value)}
              placeholder="e.g. srinivas_analytics"
            />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input 
              type="password" 
              required 
              value={password} 
              onChange={e => setPassword(e.target.value)}
              placeholder="••••••••"
            />
          </div>

          {error && <div className="auth-error">⚠️ {error}</div>}

          <button className="auth-btn" type="submit" disabled={loading}>
            {loading ? <span className="spin">⟳</span> : (isLogin ? 'Login Now' : 'Sign Up')}
          </button>
        </form>

        <div className="auth-footer">
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <button className="text-btn" onClick={() => { setIsLogin(!isLogin); setError(null); }}>
            {isLogin ? 'Register' : 'Login'}
          </button>
        </div>
      </div>
    </div>
  );
}
