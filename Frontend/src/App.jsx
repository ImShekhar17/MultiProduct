import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import Onboarding from './pages/Onboarding';
import CommandMenu from './components/CommandMenu';
import Toast from './components/Toast';
import MockWebSocket from './components/MockWebSocket';
import Cart from './components/Cart';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-white dark:bg-deep-midnight text-apple-slate dark:text-gray-100 selection:bg-apple-violet/30">
        <MockWebSocket />
        <Toast />
        <Cart />
        <CommandMenu />
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          <Route path="/onboarding" element={<Onboarding />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
