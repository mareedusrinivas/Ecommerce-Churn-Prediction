import React, { useState, useEffect } from 'react';
import HomePage from './HomePage';
import Dashboard from './Dashboard';
import Auth from './Auth';
import './App.css';

function App() {
  const [view, setView] = useState('home');
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check if session exists in browser localStorage on load
  useEffect(() => {
    const checkAuth = () => {
      const storedUser = localStorage.getItem('churn_app_current_user');
      if (storedUser) {
        setUser(storedUser);
      }
      // Added a slight artificial delay for a premium loading feel
      setTimeout(() => setLoading(false), 500);
    };
    checkAuth();
  }, []);

  const handleLogin = (username) => {
    setUser(username);
    setView('dashboard');
  };

  const handleLogout = () => {
    localStorage.removeItem('churn_app_current_user');
    setUser(null);
    setView('home');
  };

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loader"></div>
        <p>Verifying authentication...</p>
      </div>
    );
  }

  // View logic
  if (view === 'auth') {
    return <Auth onLogin={handleLogin} />;
  }

  if (view === 'dashboard' && user) {
    return <Dashboard onBack={() => setView('home')} onLogout={handleLogout} username={user} />;
  }

  return (
    <HomePage 
      onGetStarted={() => user ? setView('dashboard') : setView('auth')} 
      user={user} 
      onLogout={handleLogout}
    />
  );
}

export default App;
