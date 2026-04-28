import React from 'react';
import { Link, Outlet } from 'react-router-dom';

const Layout = () => {
  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Sidebar */}
      <nav className="w-64 bg-gray-900 text-white p-6">
        <h1 className="text-2xl font-bold mb-8">💰 Finance Tracker</h1>
        <ul className="space-y-2">
          <li>
            <Link
              to="/"
              className="block p-3 rounded hover:bg-gray-800 transition"
            >
              📊 Dashboard
            </Link>
          </li>
          <li>
            <Link
              to="/income"
              className="block p-3 rounded hover:bg-gray-800 transition"
            >
              💰 Income
            </Link>
          </li>
          <li>
            <Link
              to="/sources"
              className="block p-3 rounded hover:bg-gray-800 transition"
            >
              🔗 Manage Sources
            </Link>
          </li>
          <li>
            <Link
              to="/expenses"
              className="block p-3 rounded hover:bg-gray-800 transition"
            >
              💸 Expenses
            </Link>
          </li>
          <li>
            <Link
              to="/summary"
              className="block p-3 rounded hover:bg-gray-800 transition"
            >
              📈 Summary
            </Link>
          </li>
          <li>
            <Link
              to="/import"
              className="block p-3 rounded hover:bg-gray-800 transition"
            >
              📥 Import CSV
            </Link>
          </li>
        </ul>
      </nav>

      {/* Main Content */}
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
