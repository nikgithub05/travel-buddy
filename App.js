// src/App.js
import React from 'react';
import { Routes, Route } from 'react-router-dom';
import AuthForm from './components/AuthForm';
import Dashboard from './components/dashboard';
import TripPlan from './components/TripPlan';

const App = () => {
  return (
    <Routes>
      <Route path="/" element={<AuthForm />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/trip-plan" element={<TripPlan />} />
    </Routes>
  );
};

export default App;
