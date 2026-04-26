import React, { useMemo } from 'react';

const RecurringExpenses = ({ expenses }) => {
  const recurring = useMemo(() => {
    const categoryCount = {};
    const categoryTotal = {};
    
    expenses.forEach((exp) => {
      const key = exp.category;
      categoryCount[key] = (categoryCount[key] || 0) + 1;
      categoryTotal[key] = (categoryTotal[key] || 0) + exp.amount;
    });

    return Object.entries(categoryCount)
      .filter(([, count]) => count >= 3)
      .map(([category, count]) => ({
        category,
        count,
        avgAmount: categoryTotal[category] / count,
      }))
      .sort((a, b) => b.count - a.count);
  }, [expenses]);

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-bold mb-4">Recurring Expenses</h2>
      {recurring.length === 0 ? (
        <p className="text-gray-500 text-sm">No recurring patterns found</p>
      ) : (
        <div className="space-y-3">
          {recurring.map((item) => (
            <div key={item.category} className="border rounded p-3">
              <p className="font-semibold">{item.category}</p>
              <p className="text-sm text-gray-600">Occurrences: {item.count}</p>
              <p className="text-sm text-gray-600">Avg: ₹{item.avgAmount.toFixed(2)}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default RecurringExpenses;