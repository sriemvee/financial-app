import React, { useState } from 'react';

const ExpenseForm = () => {
    const [amount, setAmount] = useState('');
    const [category, setCategory] = useState('');
    const [mode, setMode] = useState('');
    const [needType, setNeedType] = useState('');
    const [note, setNote] = useState('');
    const [date, setDate] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        // Add your submission logic here
    };

    return (
        <form onSubmit={handleSubmit}>
            <input type="number" value={amount} onChange={(e) => setAmount(e.target.value)} placeholder="Amount" required />
            <input type="text" value={category} onChange={(e) => setCategory(e.target.value)} placeholder="Category" required />
            <input type="text" value={mode} onChange={(e) => setMode(e.target.value)} placeholder="Mode" required />
            <input type="text" value={needType} onChange={(e) => setNeedType(e.target.value)} placeholder="Need Type" required />
            <textarea value={note} onChange={(e) => setNote(e.target.value)} placeholder="Note"></textarea>
            <input type="date" value={date} onChange={(e) => setDate(e.target.value)} required />
            <button type="submit">Add Expense</button>
        </form>
    );
};

export default ExpenseForm;