import React, { useEffect, useState } from 'react';
import { api } from '../utils/api';
import Categories from './Categories';

const Sources = () => {
  const [incomeSources, setIncomeSources] = useState([]);
  const [expenseSources, setExpenseSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('income');
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    type: '',
    owner: '',
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [incomeData, expenseData] = await Promise.all([
        api.getIncomeSources(),
        api.getExpenseSources(),
      ]);
      setIncomeSources(incomeData);
      setExpenseSources(expenseData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (activeTab === 'income') {
        if (editingId) {
          await api.updateIncomeSource(editingId, formData);
        } else {
          await api.createIncomeSource(formData);
        }
      } else {
        if (editingId) {
          await api.updateExpenseSource(editingId, formData);
        } else {
          await api.createExpenseSource(formData);
        }
      }
      setShowForm(false);
      setEditingId(null);
      setFormData({ name: '', description: '', type: '', owner: '' });
      fetchData();
    } catch (err) {
      alert('Error: ' + err.message);
    }
  };

  const handleEdit = (source) => {
    setFormData(source);
    setEditingId(source.id);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure?')) return;
    try {
      if (activeTab === 'income') {
        await api.deleteIncomeSource(id);
      } else {
        await api.deleteExpenseSource(id);
      }
      fetchData();
    } catch (err) {
      alert('Error: ' + err.message);
    }
  };

  if (loading) return <div className="p-8">Loading...</div>;

  const sources = activeTab === 'income' ? incomeSources : expenseSources;

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Manage Sources</h1>
        <button
          onClick={() => {
            setShowForm(true);
            setEditingId(null);
            setFormData({ name: '', description: '', type: '', owner: '' });
          }}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          + Add Source
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-4 mb-6">
        <button
          onClick={() => setActiveTab('income')}
          className={`px-6 py-2 rounded font-semibold ${
            activeTab === 'income'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
          }`}
        >
          Income Sources
        </button>
        <button
          onClick={() => setActiveTab('expense')}
          className={`px-6 py-2 rounded font-semibold ${
            activeTab === 'expense'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
          }`}
        >
          Expense Sources
        </button>
        <button
          onClick={() => setActiveTab('categories')}
          className={`px-6 py-2 rounded font-semibold ${
          activeTab === 'categories'
            ? 'bg-blue-600 text-white'
            : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
        }`}
        >
          Categories
        </button>
      </div>

      {/* Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg w-96 max-h-96 overflow-y-auto">
            <h2 className="text-xl font-bold mb-4">
              {editingId ? 'Edit' : 'Add'} {activeTab === 'income' ? 'Income' : 'Expense'} Source
            </h2>
            <form onSubmit={handleSubmit}>
              <input
                type="text"
                name="name"
                placeholder="Source Name"
                value={formData.name}
                onChange={handleFormChange}
                required
                className="w-full border rounded px-3 py-2 mb-3"
              />

              <input
                type="text"
                name="description"
                placeholder="Description"
                value={formData.description}
                onChange={handleFormChange}
                className="w-full border rounded px-3 py-2 mb-3"
              />

              <input
                type="text"
                name="type"
                placeholder="Type (e.g., salary, upi, credit_card)"
                value={formData.type}
                onChange={handleFormChange}
                required
                className="w-full border rounded px-3 py-2 mb-3"
              />

              {activeTab === 'expense' && (
                <input
                  type="text"
                  name="owner"
                  placeholder="Owner (e.g., Srini, Jaya, Joint)"
                  value={formData.owner}
                  onChange={handleFormChange}
                  className="w-full border rounded px-3 py-2 mb-3"
                />
              )}

              {activeTab === 'categories' && <Categories />}

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

      {/* Sources Table */}
      {error ? (
        <div className="text-red-600">Error: {error}</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="bg-gray-100 border">
                <th className="border p-3 text-left">Name</th>
                <th className="border p-3 text-left">Description</th>
                <th className="border p-3 text-left">Type</th>
                {activeTab === 'expense' && (
                  <th className="border p-3 text-left">Owner</th>
                )}
                <th className="border p-3 text-center">Actions</th>
              </tr>
            </thead>
            <tbody>
              {sources.map((source) => (
                <tr key={source.id} className="border hover:bg-gray-50">
                  <td className="border p-3 font-semibold">{source.name}</td>
                  <td className="border p-3">{source.description || '-'}</td>
                  <td className="border p-3 capitalize">{source.type}</td>
                  {activeTab === 'expense' && (
                    <td className="border p-3">{source.owner || '-'}</td>
                  )}
                  <td className="border p-3 text-center">
                    <button
                      onClick={() => handleEdit(source)}
                      className="bg-blue-500 text-white px-2 py-1 rounded mr-2 hover:bg-blue-600"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(source.id)}
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

export default Sources;
