import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Expenses from './pages/Expenses';
import Import from './pages/Import';
import SummaryPage from './pages/Summary';
import './App.css';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <nav className="bg-white shadow-lg">
          <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">💰 Financial Tracker</h1>
            <ul className="flex gap-6">
              <li>
                <Link to="/" className="text-gray-700 hover:text-blue-600 font-semibold">
                  Dashboard
                </Link>
              </li>
              <li>
                <Link to="/expenses" className="text-gray-700 hover:text-blue-600 font-semibold">
                  Expenses
                </Link>
              </li>
              <li>
                <Link to="/import" className="text-gray-700 hover:text-blue-600 font-semibold">
                  Import
                </Link>
              </li>
              <li>
                <Link to="/summary" className="text-gray-700 hover:text-blue-600 font-semibold">
                  Summary
                </Link>
              </li>
            </ul>
          </div>
        </nav>

        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/expenses" element={<Expenses />} />
          <Route path="/import" element={<Import />} />
          <Route path="/summary" element={<SummaryPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;