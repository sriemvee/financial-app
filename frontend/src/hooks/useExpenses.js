// useExpenses.js
import { useState, useEffect } from 'react';

const useExpenses = () => {
    const [expenses, setExpenses] = useState([]);

    useEffect(() => {
        // Fetch data or perform other side effects here
        const fetchExpenses = async () => {
            const response = await fetch('/api/expenses');
            const data = await response.json();
            setExpenses(data);
        };

        fetchExpenses();
    }, []);

    return expenses;
};

export default useExpenses;