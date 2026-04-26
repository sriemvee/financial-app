import React, { useState } from 'react';

const ExpenseForm = ({ onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    amount: '',
    category: '',
    mode: 'credit_card',
    needType: 'household',
    note: '',
    date: new Date().toISOString().split('T')[0],
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
    setFormData({
      amount: '',
      category: '',
      mode: 'credit_card',
      needType: 'household',
      note: '',
      date: new Date().toISOString().split('T')[0],
    });
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <input
          type="number"
          name="amount"
          placeholder="Amount"
          value={formData.amount}
          onChange={handleChange}
          className="border rounded px-3 py-2"
          required
        />
        <input
          type="date"
          name="date"
          value={formData.date}
          onChange={handleChange}
          className="border rounded px-3 py-2"
          required
        />
      </div>

      <select
        name="category"
        value={formData.category}
        onChange={handleChange}
        className="w-full border rounded px-3 py-2"
        required
      >
        <option value="">Select Category</option>
        <option value="1">Groceries</option>
        <option value="2">Dining</option>
        <option value="3">Transportation</option>
      </select>

      <select
        name="mode"
        value={formData.mode}
        onChange={handleChange}
        className="w-full border rounded px-3 py-2"
      >
        <option value="credit_card">Credit Card</option>
        <option value="debit_card">Debit Card</option>
        <option value="cash">Cash</option>
        <option value="upi">UPI</option>
        <option value="bank_transfer">Bank Transfer</option>
      </select>

      <select
        name="needType"
        value={formData.needType}
        onChange={handleChange}
        className="w-full border rounded px-3 py-2"
      >
        <option value="household">Household</option>
        <option value="personal">Personal</option>
        <option value="spouse">Spouse</option>
        <option value="kids">Kids</option>
        <option value="family">Family</option>
      </select>

      <textarea
        name="note"
        placeholder="Notes"
        value={formData.note}
        onChange={handleChange}
        className="w-full border rounded px-3 py-2"
        rows="3"
      />

      <div className="flex gap-2">
        <button
          type="submit"
          className="flex-1 bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
        >
          Add Expense
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="flex-1 bg-gray-300 text-gray-900 py-2 rounded hover:bg-gray-400"
        >
          Cancel
        </button>
      </div>
    </form>
  );
};

export default ExpenseForm;