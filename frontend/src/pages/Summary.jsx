import React, { useEffect, useState } from 'react';

const Summary = () => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedMonth, setSelectedMonth] = useState(null);
  const [months, setMonths] = useState([]);

  useEffect(() => {
    // Generate last 4 months (current + 3 prior)
    const monthList = [];
    for (let i = 0; i < 4; i++) {
      const date = new Date();
      date.setMonth(date.getMonth() - i);
      const monthStr = date.toISOString().slice(0, 7);
      monthList.push({
        value: monthStr,
        label: new Date(monthStr + '-01').toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
      });
    }
    setMonths(monthList);
    setSelectedMonth(monthList[0].value); // Set current month as default
  }, []);

  useEffect(() => {
    if (selectedMonth) {
      fetchSummary(selectedMonth);
    }
  }, [selectedMonth]);

  const fetchSummary = async (month) => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/summary/monthly?month=${month}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch summary: ${response.status}`);
      }
      
      const data = await response.json();
      setSummary(data);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching summary:', err);
    } finally {
      setLoading(false);
    }
  };

  if (error) {
    return <div className="bg-white rounded-lg shadow p-6 text-red-600">Error: {error}</div>;
  }

  if (!summary && !loading) {
    return <div className="bg-white rounded-lg shadow p-6">No data available</div>;
  }

  return (
    <div className="space-y-6">
      {/* Month Selector */}
      <div className="bg-white rounded-lg shadow p-6">
        <label className="block text-sm font-semibold text-gray-700 mb-3">Select Month</label>
        <div className="flex gap-2 flex-wrap">
          {months.map((month) => (
            <button
              key={month.value}
              onClick={() => setSelectedMonth(month.value)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                selectedMonth === month.value
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {month.label}
            </button>
          ))}
        </div>
      </div>

      {/* Summary Cards */}
      {loading ? (
        <div className="bg-white rounded-lg shadow p-6 text-center">Loading...</div>
      ) : summary ? (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">Monthly Summary - {summary.month}</h2>
          
          {/* Income & Expenses Summary */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-green-50 p-4 rounded-lg border border-green-200">
              <p className="text-gray-600 text-sm">Total Income</p>
              <p className="text-2xl font-bold text-green-600">₹{summary.total_income?.toFixed(2) || '0.00'}</p>
            </div>
            <div className="bg-red-50 p-4 rounded-lg border border-red-200">
              <p className="text-gray-600 text-sm">Total Expenses</p>
              <p className="text-2xl font-bold text-red-600">₹{summary.total_expenses?.toFixed(2) || '0.00'}</p>
            </div>
            <div className={`p-4 rounded-lg border ${summary.net >= 0 ? 'bg-blue-50 border-blue-200' : 'bg-orange-50 border-orange-200'}`}>
              <p className="text-gray-600 text-sm">Net</p>
              <p className={`text-2xl font-bold ${summary.net >= 0 ? 'text-blue-600' : 'text-orange-600'}`}>
                ₹{summary.net?.toFixed(2) || '0.00'}
              </p>
            </div>
          </div>

          {/* Category Breakdown */}
          {summary.category_breakdown && Object.keys(summary.category_breakdown).length > 0 && (
            <div className="border-t pt-4 mb-4">
              <p className="text-sm font-semibold text-gray-700 mb-3">Expenses by Category</p>
              <div className="space-y-2">
                {Object.entries(summary.category_breakdown).map(([category, amount]) => (
                  <div key={category} className="flex justify-between text-sm py-1 px-2 bg-gray-50 rounded">
                    <span className="text-gray-700">{category}</span>
                    <span className="font-semibold">₹{amount.toFixed(2)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Mode Breakdown */}
          {summary.mode_breakdown && Object.keys(summary.mode_breakdown).length > 0 && (
            <div className="border-t pt-4 mb-4">
              <p className="text-sm font-semibold text-gray-700 mb-3">Payment Methods</p>
              <div className="space-y-2">
                {Object.entries(summary.mode_breakdown).map(([mode, amount]) => (
                  <div key={mode} className="flex justify-between text-sm py-1 px-2 bg-gray-50 rounded">
                    <span className="text-gray-700">{mode}</span>
                    <span className="font-semibold">₹{amount.toFixed(2)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Need Type Breakdown */}
          {summary.need_type_breakdown && Object.keys(summary.need_type_breakdown).length > 0 && (
            <div className="border-t pt-4">
              <p className="text-sm font-semibold text-gray-700 mb-3">Expenses by Type</p>
              <div className="space-y-2">
                {Object.entries(summary.need_type_breakdown).map(([type, amount]) => (
                  <div key={type} className="flex justify-between text-sm py-1 px-2 bg-gray-50 rounded">
                    <span className="text-gray-700">{type}</span>
                    <span className="font-semibold">₹{amount.toFixed(2)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : null}
    </div>
  );
};

export default Summary;
