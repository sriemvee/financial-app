import React, { useEffect, useState } from 'react';
import { api } from '../utils/api';
import { formatCurrency, formatDate } from '../utils/formatting';

const Expenses = () => {
  const [expenses, setExpenses] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    user_id: 1,
    amount: '',
    date: new Date().toISOString().split('T')[0],
    category_id: '',
    mode: 'cash',
    need_type: 'personal',
    note: '',
  });
  const [expenseSources, setExpenseSources] = useState([]);
  useEffect(() => {
  const fetchSources = async () => {
    try {
      const sources = await api.getExpenseSources();
      setExpenseSources(sources);
    } catch (err) {
      console.error('Failed to fetch expense sources:', err);
    }
  };
  fetchSources();
}, []);

// Add to formData state
const [formData, setFormData] = useState({
  user_id: 1,
  amount: '',
  date: new Date().toISOString().split('T')[0],
  category_id: '',
  mode: 'cash',
  need_type: 'personal',
  expense_source_id: '',  // Add this
  note: '',
});
  ;

  const [filters, setFilters] = useState({
    category_id: '',
    mode: '',
    need_type: '',
    date_from: '',
    date_to: '',
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [expensesData, categoriesData] = await Promise.all([
        api.getExpenses(filters),
        api.getCategories(),
      ]);
      setExpenses(expensesData);
      setCategories(categoriesData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  const applyFilters = () => {
    fetchData();
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'amount' ? parseFloat(value) : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) {
        await api.updateExpense(editingId, formData);
      } else {
        await api.createExpense(formData);
      }
      setShowForm(false);
      setEditingId(null);
      setFormData({
        user_id: 1,
        amount: '',
        date: new Date().toISOString().split('T')[0],
        category_id: '',
        mode: 'cash',
        need_type: 'personal',
        note: '',
      });
      fetchData();
    } catch (err) {
      alert('Error: ' + err.message);
    }
  };

  const handleEdit = (expense) => {
    setFormData(expense);
    setEditingId(expense.id);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure?')) return;
    try {
      await api.deleteExpense(id);
      fetchData();
    } catch (err) {
      alert('Error: ' + err.message);
    }
  };

  const getCategoryName = (id) => {
    const cat = categories.find((c) => c.id === id);
    return cat ? cat.name : 'Unknown';
  };

  const getSourceName = (id) => {
  if (!id) return '-';
  const source = expenseSources.find((s) => s.id === id);
  return source ? source.name : 'Unknown';
  };

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Expenses</h1>
        <button
          onClick={() => {
            setShowForm(true);
            setEditingId(null);
            setFormData({
              user_id: 1,
              amount: '',
              date: new Date().toISOString().split('T')[0],
              category_id: '',
              mode: 'cash',
              need_type: 'personal',
              note: '',
            });
          }}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          + Add Expense
        </button>
      </div>

      {/* Filters */}
      <div className="bg-gray-50 p-4 rounded-lg mb-6">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <select
            name="category_id"
            value={filters.category_id}
            onChange={handleFilterChange}
            className="border rounded px-3 py-2"
          >
            <option value="">All Categories</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.name}
              </option>
            ))}
          </select>

          <select
            name="mode"
            value={filters.mode}
            onChange={handleFilterChange}
            className="border rounded px-3 py-2"
          >
            <option value="">All Modes</option>
            <option value="cash">Cash</option>
            <option value="upi">UPI</option>
            <option value="card">Card</option>
            <option value="bank_transfer">Bank Transfer</option>
            <option value="subscription">Subscription</option>
          </select>

          <select
            name="need_type"
            value={filters.need_type}
            onChange={handleFilterChange}
            className="border rounded px-3 py-2"
          >
            <option value="">All Need Types</option>
            <option value="personal">Personal</option>
            <option value="spouse">Spouse</option>
            <option value="household">Household</option>
            <option value="official">Official</option>
            <option value="kids">Kids</option>
            <option value="family">Family</option>
          </select>

          <input
            type="date"
            name="date_from"
            value={filters.date_from}
            onChange={handleFilterChange}
            className="border rounded px-3 py-2"
            placeholder="From"
          />

          <input
            type="date"
            name="date_to"
            value={filters.date_to}
            onChange={handleFilterChange}
            className="border rounded px-3 py-2"
            placeholder="To"
          />
        </div>
        <button
          onClick={applyFilters}
          className="mt-4 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Apply Filters
        </button>
      </div>

      {/* Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg w-96 max-h-96 overflow-y-auto">
            <h2 className="text-xl font-bold mb-4">
              {editingId ? 'Edit Expense' : 'Add Expense'}
            </h2>
            <form onSubmit={handleSubmit}>
              <input
                type="number"
                name="amount"
                placeholder="Amount"
                value={formData.amount}
                onChange={handleFormChange}
                required
                className="w-full border rounded px-3 py-2 mb-3"
              />

              <input
                type="date"
                name="date"
                value={formData.date}
                onChange={handleFormChange}
                required
                className="w-full border rounded px-3 py-2 mb-3"
              />

              <select
                name="category_id"
                value={formData.category_id}
                onChange={handleFormChange}
                required
                className="w-full border rounded px-3 py-2 mb-3"
              >
                <option value="">Select Category</option>
                {categories.map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.name}
                  </option>
                ))}
              </select>

              <select
                name="mode"
                value={formData.mode}
                onChange={handleFormChange}
                className="w-full border rounded px-3 py-2 mb-3"
              >
                <option value="cash">Cash</option>
                <option value="upi">UPI</option>
                <option value="card">Card</option>
                <option value="bank_transfer">Bank Transfer</option>
                <option value="subscription">Subscription</option>
              </select>

              <select
                name="need_type"
                value={formData.need_type}
                onChange={handleFormChange}
                className="w-full border rounded px-3 py-2 mb-3"
              >
                <option value="personal">Personal</option>
                <option value="spouse">Spouse</option>
                <option value="household">Household</option>
                <option value="official">Official</option>
                <option value="kids">Kids</option>
                <option value="family">Family</option>
              </select>

              <select
                name="expense_source_id"
                value={formData.expense_source_id}
                onChange={handleFormChange}
                className="w-full border rounded px-3 py-2 mb-3"
              >
                <option value="">Select Expense Source (Optional)</option>
                {expenseSources.map((source) => 
                  (
                  <option key={source.id} value={source.id}>{source.name} ({source.owner}) </option>
                  ))
                }
              </select>
              
              <textarea
                name="note"
                placeholder="Notes"
                value={formData.note}
                onChange={handleFormChange}
                className="w-full border rounded px-3 py-2 mb-3"
              />

              <div className="flex gap-2">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
                >
                  Save
                </button>
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="flex-1 bg-gray-600 text-white py-2 rounded hover:bg-gray-700"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Expenses Table */}
      {error ? (
        <div className="text-red-600">Error: {error}</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="bg-gray-100 border">
                <th className="border p-3 text-left">Date</th>
                <th className="border p-3 text-left">Category</th>
                <th className="border p-3 text-left">Amount</th>
                <th className="border p-3 text-left">Mode</th>
                <th className="border p-3 text-left">Need Type</th>
                <th className="border p-3 text-left">Note</th>
                <th className="border p-3 text-left">Source</th>
                <th className="border p-3 text-center">Actions</th>
              </tr>
            </thead>
            <tbody>
              {expenses.map((expense) => (
                <tr key={expense.id} className="border hover:bg-gray-50">
                  <td className="border p-3">{formatDate(expense.date)}</td>
                  <td className="border p-3">{getCategoryName(expense.category_id)}</td>
                  <td className="border p-3 font-semibold">
                    {formatCurrency(expense.amount)}
                  </td>
                  <td className="border p-3 capitalize">{expense.mode}</td>
                  <td className="border p-3 capitalize">{expense.need_type}</td>
                  <td className="border p-3 text-sm">{expense.note || '-'}</td>
                  <td className="border p-3">{getSourceName(expense.expense_source_id)}</td>
                  <td className="border p-3 text-center">
                    <button
                      onClick={() => handleEdit(expense)}
                      className="bg-blue-500 text-white px-2 py-1 rounded mr-2 hover:bg-blue-600"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(expense.id)}
                      className="bg-red-500 text-white px-2 py-1 rounded hover:bg-red-600"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default Expenses;
