import React, { useEffect, useState } from 'react';
import { api } from '../utils/api';
import { formatCurrency } from '../utils/formatting';
import { PieChart, Pie, BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const Summary = () => {
  const [summary, setSummary] = useState(null);
  const [categoryBreakdown, setCategoryBreakdown] = useState([]);
  const [modeBreakdown, setModeBreakdown] = useState([]);
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        setLoading(true);
        const [summaryData, catBreakdown, modeBreakdown, trendsData] = await Promise.all([
          api.getMonthlySummary(),
          api.getCategoryBreakdown(),
          api.getModeBreakdown(),
          api.getExpenseTrends(6),
        ]);

        setSummary(summaryData);
        setCategoryBreakdown(catBreakdown);
        setModeBreakdown(modeBreakdown);
        setTrends(trendsData);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchSummary();
  }, []);

  if (loading) return <div className="p-8">Loading...</div>;
  if (error) return <div className="p-8 text-red-600">Error: {error}</div>;

  const COLORS = ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899'];

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">Summary & Analytics</h1>

      {/* Monthly Summary */}
      {summary && (
        <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-6 rounded-lg mb-8">
          <h2 className="text-2xl font-bold mb-4">Monthly Summary</h2>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-blue-100">Total Income</p>
              <p className="text-3xl font-bold">{formatCurrency(summary.total_income || 0)}</p>
            </div>
            <div>
              <p className="text-blue-100">Total Expenses</p>
              <p className="text-3xl font-bold">{formatCurrency(summary.total_expenses || 0)}</p>
            </div>
            <div>
              <p className="text-blue-100">Balance</p>
              <p className="text-3xl font-bold">{formatCurrency((summary.total_income || 0) - (summary.total_expenses || 0))}</p>
            </div>
          </div>
        </div>
      )}

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Category Breakdown */}
        {categoryBreakdown && categoryBreakdown.length > 0 && (
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">Category Breakdown</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={categoryBreakdown}
                  dataKey="amount"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label
                >
                  {categoryBreakdown.map((entry, index) => (
                    <circle key={`color-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => formatCurrency(value)} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Mode Breakdown */}
        {modeBreakdown && modeBreakdown.length > 0 && (
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">Payment Mode Breakdown</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={modeBreakdown}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="mode" />
                <YAxis />
                <Tooltip formatter={(value) => formatCurrency(value)} />
                <Bar dataKey="amount" fill="#3B82F6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Trends */}
      {trends && trends.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow mb-8">
          <h3 className="text-lg font-semibold mb-4">6-Month Expense Trends</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trends}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip formatter={(value) => formatCurrency(value)} />
              <Legend />
              <Line type="monotone" dataKey="amount" stroke="#3B82F6" name="Expenses" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

export default Summary;
