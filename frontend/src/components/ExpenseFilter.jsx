import React from 'react';

const ExpenseFilter = ({ filters, onFilterChange }) => {
  const handleChange = (e) => {
    const { name, value } = e.target;
    onFilterChange({ ...filters, [name]: value });
  };

  return (
    <div className="bg-white rounded-lg shadow p-4 mb-6">
      <h3 className="text-lg font-semibold mb-4">Filters</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <select
          name="category"
          value={filters.category}
          onChange={handleChange}
          className="border rounded px-3 py-2"
        >
          <option value="">All Categories</option>
          <option value="1">Groceries</option>
          <option value="2">Dining</option>
          <option value="3">Transportation</option>
        </select>

        <select
          name="mode"
          value={filters.mode}
          onChange={handleChange}
          className="border rounded px-3 py-2"
        >
          <option value="">All Modes</option>
          <option value="cash">Cash</option>
          <option value="credit_card">Credit Card</option>
          <option value="debit_card">Debit Card</option>
          <option value="upi">UPI</option>
        </select>

        <select
          name="needType"
          value={filters.needType}
          onChange={handleChange}
          className="border rounded px-3 py-2"
        >
          <option value="">All Need Types</option>
          <option value="personal">Personal</option>
          <option value="household">Household</option>
          <option value="spouse">Spouse</option>
          <option value="kids">Kids</option>
        </select>

        <input
          type="date"
          name="dateFrom"
          value={filters.dateFrom}
          onChange={handleChange}
          className="border rounded px-3 py-2"
          placeholder="From"
        />

        <input
          type="date"
          name="dateTo"
          value={filters.dateTo}
          onChange={handleChange}
          className="border rounded px-3 py-2"
          placeholder="To"
        />
      </div>
    </div>
  );
};

export default ExpenseFilter;