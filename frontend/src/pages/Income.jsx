import React, { useEffect, useState } from 'react';
import { api } from '../utils/api';
import { formatCurrency, formatDate } from '../utils/formatting';

const Income = () => {
  const [income, setIncome] = useState([]);
  const [incomeSources, setIncomeSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    user_id: 1,
    amount: '',
    date: new Date().toISOString().split('T')[0],
    source_id: '',
    note: '',
  });

  const [filters, setFilters] = useState({
    source_id: '',
    date_from: '',
    date_to: '',
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [incomeData, sourcesData] = await Promise.all([
        api.getIncome(filters),
        api.getIncomeSources(),
      ]);
      setIncome(incomeData);
      setIncomeSources(sourcesData);
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
        await api.updateIncome(editingId, formData);
      } else {
        await api.createIncome(formData);
      }
      setShowForm(false);
      setEditingId(null);
      setFormData({
        user_id: 1,
        amount: '',
        date: new Date().toISOString().split('T')[0],
        source_id: '',
        note: '',
      });
      fetchData();
    } catch (err) {
      alert('Error: ' + err.message);
    }
  };

  const handleEdit = (incomeItem) => {
    setFormData(incomeItem);
    setEditingId(incomeItem.id);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure?')) return;
    try {
      await api.deleteIncome(id);
      fetchData();
    } catch (err) {
      alert('Error: ' + err.message);
    }
  };

  const getSourceName = (id) => {
    const source = incomeSources.find((s) => s.id === id);
    return source ? source.name : 'Unknown';
  };

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Income</h1>
        <button
          onClick={() => {
            setShowForm(true);
            setEditingId(null);
            setFormData({
              user_id: 1,
              amount: '',
              date: new Date().toISOString().split('T')[0],
              source_id: '',
              note: '',
            });
          }}
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
        >
          + Add Income
        </button>
      </div>

      {/* Filters */}
      <div className="bg-gray-50 p-4 rounded-lg mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <select
            name="source_id"
            value={filters.source_id}
            onChange={handleFilterChange}
            className="border rounded px-3 py-2"
          >
            <option value="">All Sources</option>
            {incomeSources.map((source) => (
              <option key={source.id} value={source.id}>
                {source.name}
              </option>
            ))}
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
          className="mt-4 bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
        >
          Apply Filters
        </button>
      </div>

      {/* Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg w-96 max-h-96 overflow-y-auto">
            <h2 className="text-xl font-bold mb-4">
              {editingId ? 'Edit Income' : 'Add Income'}
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
                name="source_id"
                value={formData.source_id}
                onChange={handleFormChange}
                required
                className="w-full border rounded px-3 py-2 mb-3"
              >
                <option value="">Select Income Source</option>
                {incomeSources.map((source) => (
                  <option key={source.id} value={source.id}>
                    {source.name}
                  </option>
                ))}
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
                  className="flex-1 bg-green-600 text-white py-2 rounded hover:bg-green-700"
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

      {/* Income Table */}
      {error ? (
        <div className="text-red-600">Error: {error}</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="bg-gray-100 border">
                <th className="border p-3 text-left">Date</th>
                <th className="border p-3 text-left">Source</th>
                <th className="border p-3 text-left">Amount</th>
                <th className="border p-3 text-left">Note</th>
                <th className="border p-3 text-center">Actions</th>
              </tr>
            </thead>
            <tbody>
              {income.map((item) => (
                <tr key={item.id} className="border hover:bg-gray-50">
                  <td className="border p-3">{formatDate(item.date)}</td>
                  <td className="border p-3">{getSourceName(item.source_id)}</td>
                  <td className="border p-3 font-semibold text-green-600">
                    {formatCurrency(item.amount)}
                  </td>
                  <td className="border p-3 text-sm">{item.note || '-'}</td>
                  <td className="border p-3 text-center">
                    <button
                      onClick={() => handleEdit(item)}
                      className="bg-blue-500 text-white px-2 py-1 rounded mr-2 hover:bg-blue-600"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(item.id)}
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

export default Income;
