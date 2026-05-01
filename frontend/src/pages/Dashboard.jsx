import React, { useEffect, useState } from 'react';
import { formatCurrency } from '../utils/formatting';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const month = new Date().toISOString().slice(0, 7); // Current month YYYY-MM
        const response = await fetch(`http://localhost:8000/summary/monthly?month=${month}`);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch summary: ${response.status}`);
        }
        
        const data = await response.json();
        
        setStats({
          totalIncome: data.total_income,
          totalExpenses: data.total_expenses,
          balance: data.net,
          month: data.month,
          categoryBreakdown: data.category_breakdown,
          transactionCount: Object.values(data.category_breakdown).reduce((sum, val) => sum + (val > 0 ? 1 : 0), 0)
        });
        setError(null);
      } catch (err) {
        setError(err.message);
        console.error('Error fetching stats:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) return <div className="p-8 text-center">Loading...</div>;
  if (error) return <div className="p-8 text-red-600">Error: {error}</div>;
  if (!stats) return <div className="p-8">No data available</div>;

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
      <p className="text-gray-600 mb-8">Month of {new Date(stats.month + '-01').toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}</p>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-green-50 p-6 rounded-lg border border-green-200">
          <p className="text-gray-600 text-sm">Total Income</p>
          <p className="text-2xl font-bold text-green-600">
            ₹{stats.totalIncome.toFixed(2)}
          </p>
        </div>

        <div className="bg-red-50 p-6 rounded-lg border border-red-200">
          <p className="text-gray-600 text-sm">Total Expenses</p>
          <p className="text-2xl font-bold text-red-600">
            ₹{stats.totalExpenses.toFixed(2)}
          </p>
        </div>

        <div className={`p-6 rounded-lg border ${stats.balance >= 0 ? 'bg-blue-50 border-blue-200' : 'bg-orange-50 border-orange-200'}`}>
          <p className="text-gray-600 text-sm">Balance</p>
          <p className={`text-2xl font-bold ${stats.balance >= 0 ? 'text-blue-600' : 'text-orange-600'}`}>
            ₹{stats.balance.toFixed(2)}
          </p>
        </div>

        <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
          <p className="text-gray-600 text-sm">Savings Rate</p>
          <p className="text-2xl font-bold text-gray-600">
            {stats.totalIncome > 0 ? ((stats.balance / stats.totalIncome) * 100).toFixed(1) : 0}%
          </p>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <a
          href="/expenses"
          className="bg-blue-600 text-white p-6 rounded-lg hover:bg-blue-700 cursor-pointer transition-colors"
        >
          <p className="text-lg font-semibold">💰 View Expenses</p>
          <p className="text-sm text-blue-100">Manage all transactions</p>
        </a>

        <a
          href="/import"
          className="bg-green-600 text-white p-6 rounded-lg hover:bg-green-700 cursor-pointer transition-colors"
        >
          <p className="text-lg font-semibold">📥 Import CSV</p>
          <p className="text-sm text-green-100">Upload bank statements</p>
        </a>

        <a
          href="/summary"
          className="bg-purple-600 text-white p-6 rounded-lg hover:bg-purple-700 cursor-pointer transition-colors"
        >
          <p className="text-lg font-semibold">📊 View Summary</p>
          <p className="text-sm text-purple-100">Analytics and trends</p>
        </a>
      </div>

      {/* Top Categories */}
      {Object.keys(stats.categoryBreakdown).length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-bold mb-4">Top Expense Categories</h2>
          <div className="space-y-2">
            {Object.entries(stats.categoryBreakdown)
              .filter(([_, amount]) => amount > 0)
              .sort((a, b) => b[1] - a[1])
              .slice(0, 5)
              .map(([category, amount]) => (
                <div key={category} className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded">
                  <span className="text-gray-700">{category || 'Uncategorized'}</span>
                  <span className="font-semibold text-gray-900">₹{amount.toFixed(2)}</span>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
