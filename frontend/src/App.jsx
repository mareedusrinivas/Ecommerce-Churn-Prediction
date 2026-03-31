import React, { useState } from 'react';
import './index.css';
import './App.css';
import HomePage from './HomePage';
import Dashboard from './Dashboard';

export default function App() {
  const [page, setPage] = useState('home'); // 'home' | 'dashboard'

  return page === 'home'
    ? <HomePage onGetStarted={() => setPage('dashboard')} />
    : <Dashboard onBack={() => setPage('home')} />;
}
