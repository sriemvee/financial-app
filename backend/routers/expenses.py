from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import sqlite3

router = APIRouter(prefix="/expenses", tags=["expenses"])

class ExpenseCreate(BaseModel):
    user_id: int
    amount: float
    date: str
    category_id: int
    mode: str
    need_type: str
    expense_source_id: Optional[int] = None  # Add this
    note: Optional[str] = None
    source: str = "manual"
    import_batch_id: Optional[int] = None

class ExpenseUpdate(BaseModel):
    amount: Optional[float] = None
    date: Optional[str] = None
    category_id: Optional[int] = None
    mode: Optional[str] = None
    need_type: Optional[str] = None
    note: Optional[str] = None

class Expense(BaseModel):
    id: int
    user_id: int
    amount: float
    date: str
    category_id: int
    mode: str
    need_type: str
    note: Optional[str]

def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect('expenses.db')
    conn.row_factory = sqlite3.Row
    return conn

@router.get("/")
async def get_expenses(
    user_id: Optional[int] = None,
    category_id: Optional[int] = None,
    mode: Optional[str] = None,
    need_type: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
):
    """Get all expenses with optional filters"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT id, user_id, amount, date, category_id, mode, need_type, note FROM expenses WHERE 1=1"
    params = []
    
    if user_id:
        query += " AND user_id = ?"
        params.append(user_id)
    
    if category_id:
        query += " AND category_id = ?"
        params.append(category_id)
    
    if mode:
        query += " AND mode = ?"
        params.append(mode)
    
    if need_type:
        query += " AND need_type = ?"
        params.append(need_type)
    
    if date_from:
        query += " AND date >= ?"
        params.append(date_from)
    
    if date_to:
        query += " AND date <= ?"
        params.append(date_to)
    
    query += " ORDER BY date DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

@router.post("/")
async def create_expense(expense: ExpenseCreate):
    """Create a new expense"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """INSERT INTO expenses 
           (user_id, amount, date, category_id, mode, need_type, expense_source_id, note, source, import_batch_id) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            expense.user_id,
            expense.amount,
            expense.date,
            expense.category_id,
            expense.mode,
            expense.need_type,
            expense.expense_source_id,
            expense.note,
            expense.source,
            expense.import_batch_id
        )
    )
    conn.commit()
    expense_id = cursor.lastrowid
    conn.close()
    
    return {
        "id": expense_id,
        "user_id": expense.user_id,
        "amount": expense.amount,
        "date": expense.date,
        "category_id": expense.category_id,
        "mode": expense.mode,
        "need_type": expense.need_type,
        "expense_source_id": expense.expense_source_id,
        "note": expense.note
    }

@router.get("/{expense_id}")
async def get_expense(expense_id: int):
    """Get a specific expense by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, user_id, amount, date, category_id, mode, need_type, note FROM expenses WHERE id = ?",
        (expense_id,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    return dict(row)

@router.put("/{expense_id}")
async def update_expense(expense_id: int, expense: ExpenseUpdate):
    """Update an existing expense"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get current expense
    cursor.execute(
        "SELECT * FROM expenses WHERE id = ?",
        (expense_id,)
    )
    current = cursor.fetchone()
    
    if not current:
        conn.close()
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # Update only provided fields
    update_fields = []
    update_values = []
    
    if expense.amount is not None:
        update_fields.append("amount = ?")
        update_values.append(expense.amount)
    
    if expense.date is not None:
        update_fields.append("date = ?")
        update_values.append(expense.date)
    
    if expense.category_id is not None:
        update_fields.append("category_id = ?")
        update_values.append(expense.category_id)
    
    if expense.mode is not None:
        update_fields.append("mode = ?")
        update_values.append(expense.mode)
    
    if expense.need_type is not None:
        update_fields.append("need_type = ?")
        update_values.append(expense.need_type)
    
    if expense.note is not None:
        update_fields.append("note = ?")
        update_values.append(expense.note)
    
    if not update_fields:
        conn.close()
        return dict(current)
    
    update_values.append(expense_id)
    query = f"UPDATE expenses SET {', '.join(update_fields)} WHERE id = ?"
    
    cursor.execute(query, update_values)
    conn.commit()
    conn.close()
    
    # Return updated expense
    return await get_expense(expense_id)

@router.delete("/{expense_id}")
async def delete_expense(expense_id: int):
    """Delete an expense"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()
    
    return {"id": expense_id, "status": "deleted"}
