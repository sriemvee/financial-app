import React, { useMemo } from 'react';

const CategoryBreakdown = ({ expenses }) => {
  const categoryData = useMemo(() => {
    const data = {};
    expenses.forEach((exp) => {
      data[exp.category] = (data[exp.category] || 0) + exp.amount;
    });
    return Object.entries(data).sort((a, b) => b[1] - a[1]);
  }, [expenses]);

  const total = categoryData.reduce((sum, [, amount]) => sum + amount, 0);

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-bold mb-4">Category Breakdown</h2>
      <div className="space-y-3">
        {categoryData.map(([category, amount]) => (
          <div key={category}>
            <div className="flex justify-between text-sm mb-1">
              <span>{category}</span>
              <span className="font-semibold">₹{amount.toFixed(2)}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full"
                style={{ width: `${(amount / total) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CategoryBreakdown;