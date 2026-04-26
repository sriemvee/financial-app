const API_BASE_URL = 'http://localhost:8000';

export const fetchExpenses = async () => {
  const response = await fetch(`${API_BASE_URL}/expenses`);
  if (!response.ok) throw new Error('Failed to fetch expenses');
  return response.json();
};

export const addExpenseAPI = async (data) => {
  const response = await fetch(`${API_BASE_URL}/expenses`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to add expense');
  return response.json();
};

export const deleteExpenseAPI = async (id) => {
  const response = await
