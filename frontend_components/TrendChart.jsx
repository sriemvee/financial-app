import React, { useMemo } from 'react';

const TrendChart = ({ expenses }) => {
  const monthlyData = useMemo(() => {
    const data = {};
    expenses.forEach((exp) => {
      const month = exp.date.substring(0, 7);
      data[month] = (data[month] || 0) + exp.amount;
    });
    return Object.entries(data).sort((a, b) => a[0].localeCompare(b[0]));
  }, [expenses]);

  const maxAmount = Math.max(...monthlyData.map(([, amount]) => amount), 1);

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-bold mb-4">Monthly Trend</h2>
      <div className="space-y-3">
        {monthlyData.map(([month, amount]) => (
          <div key={month}>
            <div className="flex justify-between text-sm mb-1">
              <span>{month}</span>
              <span className="font-semibold">₹{amount.toFixed(2)}</span>
            </div>
            <div className="w-full bg-gray-200 rounded h-4">
              <div
                className="bg-green-600 h-4 rounded"
                style={{ width: `${(amount / maxAmount) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TrendChart;