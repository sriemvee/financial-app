const API_BASE_URL = 'http://localhost:8000';

export const api = {
  // Categories
  getCategories: async (groupName = null) => {
    const url = new URL(`${API_BASE_URL}/categories/`);
    if (groupName) url.searchParams.append('group_name', groupName);
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch categories');
    return res.json();
  },

  // Expenses
  getExpenses: async (filters = {}) => {
    const url = new URL(`${API_BASE_URL}/expenses/`);
    Object.entries(filters).forEach(([key, value]) => {
      if (value) url.searchParams.append(key, value);
    });
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch expenses');
    return res.json();
  },

  createExpense: async (expense) => {
    const res = await fetch(`${API_BASE_URL}/expenses/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(expense),
    });
    if (!res.ok) throw new Error('Failed to create expense');
    return res.json();
  },

  updateExpense: async (id, expense) => {
    const res = await fetch(`${API_BASE_URL}/expenses/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(expense),
    });
    if (!res.ok) throw new Error('Failed to update expense');
    return res.json();
  },

  deleteExpense: async (id) => {
    const res = await fetch(`${API_BASE_URL}/expenses/${id}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to delete expense');
    return res.json();
  },

  // Summary
  getMonthlySummary: async (month = null) => {
    const url = new URL(`${API_BASE_URL}/summary/monthly`);
    if (month) url.searchParams.append('month', month);
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch summary');
    return res.json();
  },

  getExpenseTrends: async (months = 6) => {
    const url = new URL(`${API_BASE_URL}/summary/trends`);
    url.searchParams.append('months', months);
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch trends');
    return res.json();
  },

  getCategoryBreakdown: async () => {
    const res = await fetch(`${API_BASE_URL}/summary/category-breakdown`);
    if (!res.ok) throw new Error('Failed to fetch category breakdown');
    return res.json();
  },

  getModeBreakdown: async () => {
    const res = await fetch(`${API_BASE_URL}/summary/mode-breakdown`);
    if (!res.ok) throw new Error('Failed to fetch mode breakdown');
    return res.json();
  },

  getRecurringExpenses: async () => {
    const res = await fetch(`${API_BASE_URL}/summary/recurring`);
    if (!res.ok) throw new Error('Failed to fetch recurring expenses');
    return res.json();
  },

  // CSV Import
  uploadCSV: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE_URL}/csv-import/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) throw new Error('Failed to upload CSV');
    return res.json();
  },

  getImportBatches: async () => {
    const res = await fetch(`${API_BASE_URL}/csv-import/batches`);
    if (!res.ok) throw new Error('Failed to fetch import batches');
    return res.json();
  },

  deleteImportBatch: async (id) => {
    const res = await fetch(`${API_BASE_URL}/csv-import/batches/${id}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to delete import batch');
    return res.json();
  },
};
