from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import sqlite3

router = APIRouter(prefix="/sources", tags=["sources"])

class IncomeSourceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    type: str

class ExpenseSourceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    type: str
    owner: Optional[str] = None

def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect('expenses.db')
    conn.row_factory = sqlite3.Row
    return conn

# Income Sources

@router.get("/income")
async def get_income_sources():
    """Get all income sources"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, description, type FROM income_sources ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

@router.post("/income")
async def create_income_source(source: IncomeSourceCreate):
    """Create a new income source"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO income_sources (name, description, type) VALUES (?, ?, ?)",
            (source.name, source.description, source.type)
        )
        conn.commit()
        source_id = cursor.lastrowid
        conn.close()
        
        return {
            "id": source_id,
            "name": source.name,
            "description": source.description,
            "type": source.type
        }
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Income source already exists")

@router.put("/income/{source_id}")
async def update_income_source(source_id: int, source: IncomeSourceCreate):
    """Update an income source"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE income_sources SET name = ?, description = ?, type = ? WHERE id = ?",
        (source.name, source.description, source.type, source_id)
    )
    conn.commit()
    conn.close()
    
    return {
        "id": source_id,
        "name": source.name,
        "description": source.description,
        "type": source.type
    }

@router.delete("/income/{source_id}")
async def delete_income_source(source_id: int):
    """Delete an income source"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM income_sources WHERE id = ?", (source_id,))
    conn.commit()
    conn.close()
    
    return {"id": source_id, "status": "deleted"}

# Expense Sources

@router.get("/expense")
async def get_expense_sources():
    """Get all expense sources"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, description, type, owner FROM expense_sources ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

@router.post("/expense")
async def create_expense_source(source: ExpenseSourceCreate):
    """Create a new expense source"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO expense_sources (name, description, type, owner) VALUES (?, ?, ?, ?)",
            (source.name, source.description, source.type, source.owner)
        )
        conn.commit()
        source_id = cursor.lastrowid
        conn.close()
        
        return {
            "id": source_id,
            "name": source.name,
            "description": source.description,
            "type": source.type,
            "owner": source.owner
        }
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Expense source already exists")

@router.put("/expense/{source_id}")
async def update_expense_source(source_id: int, source: ExpenseSourceCreate):
    """Update an expense source"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE expense_sources SET name = ?, description = ?, type = ?, owner = ? WHERE id = ?",
        (source.name, source.description, source.type, source.owner, source_id)
    )
    conn.commit()
    conn.close()
    
    return {
        "id": source_id,
        "name": source.name,
        "description": source.description,
        "type": source.type,
        "owner": source.owner
    }

@router.delete("/expense/{source_id}")
async def delete_expense_source(source_id: int):
    """Delete an expense source"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM expense_sources WHERE id = ?", (source_id,))
    conn.commit()
    conn.close()
    
    return {"id": source_id, "status": "deleted"}
