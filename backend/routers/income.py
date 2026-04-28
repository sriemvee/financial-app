from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import sqlite3

router = APIRouter(prefix="/income", tags=["income"])

class IncomeCreate(BaseModel):
    user_id: int
    amount: float
    date: str
    source_id: int
    note: Optional[str] = None

class IncomeUpdate(BaseModel):
    amount: Optional[float] = None
    date: Optional[str] = None
    source_id: Optional[int] = None
    note: Optional[str] = None

def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect('expenses.db')
    conn.row_factory = sqlite3.Row
    return conn

@router.get("/")
async def get_income(
    user_id: Optional[int] = None,
    source_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
):
    """Get all income with optional filters"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT id, user_id, amount, date, source_id, note FROM income WHERE 1=1"
    params = []
    
    if user_id:
        query += " AND user_id = ?"
        params.append(user_id)
    
    if source_id:
        query += " AND source_id = ?"
        params.append(source_id)
    
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
async def create_income(income: IncomeCreate):
    """Create a new income entry"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """INSERT INTO income (user_id, amount, date, source_id, note) 
           VALUES (?, ?, ?, ?, ?)""",
        (income.user_id, income.amount, income.date, income.source_id, income.note)
    )
    conn.commit()
    income_id = cursor.lastrowid
    conn.close()
    
    return {
        "id": income_id,
        "user_id": income.user_id,
        "amount": income.amount,
        "date": income.date,
        "source_id": income.source_id,
        "note": income.note
    }

@router.get("/{income_id}")
async def get_income_by_id(income_id: int):
    """Get a specific income by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, user_id, amount, date, source_id, note FROM income WHERE id = ?",
        (income_id,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Income not found")
    
    return dict(row)

@router.put("/{income_id}")
async def update_income(income_id: int, income: IncomeUpdate):
    """Update an existing income entry"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM income WHERE id = ?", (income_id,))
    current = cursor.fetchone()
    
    if not current:
        conn.close()
        raise HTTPException(status_code=404, detail="Income not found")
    
    update_fields = []
    update_values = []
    
    if income.amount is not None:
        update_fields.append("amount = ?")
        update_values.append(income.amount)
    
    if income.date is not None:
        update_fields.append("date = ?")
        update_values.append(income.date)
    
    if income.source_id is not None:
        update_fields.append("source_id = ?")
        update_values.append(income.source_id)
    
    if income.note is not None:
        update_fields.append("note = ?")
        update_values.append(income.note)
    
    if not update_fields:
        conn.close()
        return dict(current)
    
    update_values.append(income_id)
    query = f"UPDATE income SET {', '.join(update_fields)} WHERE id = ?"
    
    cursor.execute(query, update_values)
    conn.commit()
    conn.close()
    
    return await get_income_by_id(income_id)

@router.delete("/{income_id}")
async def delete_income(income_id: int):
    """Delete an income entry"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM income WHERE id = ?", (income_id,))
    conn.commit()
    conn.close()
    
    return {"id": income_id, "status": "deleted"}
