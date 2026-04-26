import React from 'react';

const ExpenseTable = ({ expenses }) => {
  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <table className="w-full">
        <thead className="bg-gray-100 border-b">
          <tr>
            <th className="px-6 py-3 text-left font-semibold text-gray-700">Date</th>
            <th className="px-6 py-3 text-left font-semibold text-gray-700">Category</th>
            <th className="px-6 py-3 text-left font-semibold text-gray-700">Mode</th>
            <th className="px-6 py-3 text-left font-semibold text-gray-700">Need Type</th>
            <th className="px-6 py-3 text-right font-semibold text-gray-700">Amount</th>
            <th className="px-6 py-3 text-left font-semibold text-gray-700">Notes</th>
          </tr>
        </thead>
        <tbody>
          {expenses.length === 0 ? (
            <tr>
              <td colSpan="6" className="px-6 py-4 text-center text-gray-500">
                No expenses found
              </td>
            </tr>
          ) : (
            expenses.map((expense) => (
              <tr key={expense.id} className="border-b hover:bg-gray-50">
                <td className="px-6 py-4">{expense.date}</td>
                <td className="px-6 py-4">{expense.category}</td>
                <td className="px-6 py-4 capitalize">{expense.mode.replace('_', ' ')}</td>
                <td className="px-6 py-4 capitalize">{expense.need_type}</td>
                <td className="px-6 py-4 text-right font-semibold">₹{expense.amount.toFixed(2)}</td>
                <td className="px-6 py-4 text-gray-600">{expense.note || '-'}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default ExpenseTable;