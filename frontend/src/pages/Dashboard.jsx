import React, { useEffect, useState } from 'react';
import { api } from '../utils/api';
import { formatCurrency } from '../utils/formatting';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const [expenses, summary] = await Promise.all([
          api.getExpenses(),
          api.getMonthlySummary(),
        ]);

        const totalExpenses = expenses.reduce((sum, e) => sum + e.amount, 0);
        const totalIncome = expenses
          .filter((e) => e.category_id === 6 || e.category_id === 7)
          .reduce((sum, e) => sum + e.amount, 0);

        setStats({
          totalExpenses,
          totalIncome,
          balance: totalIncome - totalExpenses,
          transactionCount: expenses.length,
        });
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) return <div className="p-8">Loading...</div>;
  if (error) return <div className="p-8 text-red-600">Error: {error}</div>;

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-blue-50 p-6 rounded-lg">
          <p className="text-gray-600 text-sm">Total Income</p>
          <p className="text-2xl font-bold text-blue-600">
            {stats && formatCurrency(stats.totalIncome)}
          </p>
        </div>

        <div className="bg-red-50 p-6 rounded-lg">
          <p className="text-gray-600 text-sm">Total Expenses</p>
          <p className="text-2xl font-bold text-red-600">
            {stats && formatCurrency(stats.totalExpenses)}
          </p>
        </div>

        <div className="bg-green-50 p-6 rounded-lg">
          <p className="text-gray-600 text-sm">Balance</p>
          <p className="text-2xl font-bold text-green-600">
            {stats && formatCurrency(stats.balance)}
          </p>
        </div>

        <div className="bg-gray-50 p-6 rounded-lg">
          <p className="text-gray-600 text-sm">Transactions</p>
          <p className="text-2xl font-bold text-gray-600">
            {stats && stats.transactionCount}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <a
          href="/expenses"
          className="bg-blue-600 text-white p-6 rounded-lg hover:bg-blue-700 cursor-pointer"
        >
          <p className="text-lg font-semibold">View Expenses</p>
          <p className="text-sm text-blue-100">Manage all transactions</p>
        </a>

        <a
          href="/import"
          className="bg-green-600 text-white p-6 rounded-lg hover:bg-green-700 cursor-pointer"
        >
          <p className="text-lg font-semibold">Import CSV</p>
          <p className="text-sm text-green-100">Upload bank statements</p>
        </a>

        <a
          href="/summary"
          className="bg-purple-600 text-white p-6 rounded-lg hover:bg-purple-700 cursor-pointer"
        >
          <p className="text-lg font-semibold">View Summary</p>
          <p className="text-sm text-purple-100">Analytics and trends</p>
        </a>
      </div>
    </div>
  );
};

export default Dashboard;
