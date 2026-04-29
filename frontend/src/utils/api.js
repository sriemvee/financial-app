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
  createCategory: async (category) => {
    const res = await fetch(`${API_BASE_URL}/categories/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(category),
      }
    );
    if (!res.ok) throw new Error('Failed to create category');
    return res.json();
  },

  updateCategory: async (id, category) => {
    const res = await fetch(`${API_BASE_URL}/categories/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(category),
      });
    if (!res.ok) throw new Error('Failed to update category');
    return res.json();
  },

  deleteCategory: async (id) => {
    const res = await fetch(`${API_BASE_URL}/categories/${id}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to delete category');
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

  // Income
  getIncome: async (filters = {}) => {
    const url = new URL(`${API_BASE_URL}/income/`);
    Object.entries(filters).forEach(([key, value]) => {
      if (value) url.searchParams.append(key, value);
    });
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch income');
    return res.json();
  },

  createIncome: async (income) => {
    const res = await fetch(`${API_BASE_URL}/income/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(income),
    });
    if (!res.ok) throw new Error('Failed to create income');
    return res.json();
  },

  updateIncome: async (id, income) => {
    const res = await fetch(`${API_BASE_URL}/income/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(income),
    });
    if (!res.ok) throw new Error('Failed to update income');
    return res.json();
  },

  deleteIncome: async (id) => {
    const res = await fetch(`${API_BASE_URL}/income/${id}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to delete income');
    return res.json();
  },

  // Income Sources
  getIncomeSources: async () => {
    const res = await fetch(`${API_BASE_URL}/sources/income`);
    if (!res.ok) throw new Error('Failed to fetch income sources');
    return res.json();
  },

  createIncomeSource: async (source) => {
    const res = await fetch(`${API_BASE_URL}/sources/income`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(source),
    });
    if (!res.ok) throw new Error('Failed to create income source');
    return res.json();
  },

  updateIncomeSource: async (id, source) => {
    const res = await fetch(`${API_BASE_URL}/sources/income/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(source),
    });
    if (!res.ok) throw new Error('Failed to update income source');
    return res.json();
  },

  deleteIncomeSource: async (id) => {
    const res = await fetch(`${API_BASE_URL}/sources/income/${id}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to delete income source');
    return res.json();
  },

  // Expense Sources
  getExpenseSources: async () => {
    const res = await fetch(`${API_BASE_URL}/sources/expense`);
    if (!res.ok) throw new Error('Failed to fetch expense sources');
    return res.json();
  },

  createExpenseSource: async (source) => {
    const res = await fetch(`${API_BASE_URL}/sources/expense`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(source),
    });
    if (!res.ok) throw new Error('Failed to create expense source');
    return res.json();
  },

  updateExpenseSource: async (id, source) => {
    const res = await fetch(`${API_BASE_URL}/sources/expense/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(source),
    });
    if (!res.ok) throw new Error('Failed to update expense source');
    return res.json();
  },

  deleteExpenseSource: async (id) => {
    const res = await fetch(`${API_BASE_URL}/sources/expense/${id}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to delete expense source');
    return res.json();
  },
};
