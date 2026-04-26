import React, { useMemo } from 'react';

const Summary = ({ expenses }) => {
  const stats = useMemo(() => {
    const total = expenses.reduce((sum, exp) => sum + exp.amount, 0);
    const categories = {};
    expenses.forEach((exp) => {
      categories[exp.category] = (categories[exp.category] || 0) + exp.amount;
    });
    return { total, categories };
  }, [expenses]);

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-bold mb-4">Summary</h2>
      <div className="space-y-3">
        <div>
          <p className="text-gray-600 text-sm">Total Expenses</p>
          <p className="text-2xl font-bold">₹{stats.total.toFixed(2)}</p>
        </div>
        <div className="border-t pt-3">
          <p className="text-sm font-semibold text-gray-700 mb-2">By Category</p>
          {Object.entries(stats.categories).map(([category, amount]) => (
            <div key={category} className="flex justify-between text-sm py-1">
              <span>{category}</span>
              <span>₹{amount.toFixed(2)}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Summary;