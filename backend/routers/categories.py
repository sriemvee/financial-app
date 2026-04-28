from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import sqlite3

router = APIRouter(prefix="/categories", tags=["categories"])

class CategoryCreate(BaseModel):
    name: str
    group_name: str

class Category(BaseModel):
    id: int
    name: str
    group_name: str

def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect('expenses.db')
    conn.row_factory = sqlite3.Row
    return conn

@router.get("/")
async def get_categories(group_name: Optional[str] = None) -> List[Category]:
    """Get all categories, optionally filtered by group"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if group_name:
        cursor.execute("SELECT id, name, group_name FROM categories WHERE group_name = ?", (group_name,))
    else:
        cursor.execute("SELECT id, name, group_name FROM categories")
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

@router.post("/")
async def create_category(category: CategoryCreate) -> Category:
    """Create a new category"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO categories (name, group_name) VALUES (?, ?)",
        (category.name, category.group_name)
    )
    conn.commit()
    category_id = cursor.lastrowid
    conn.close()
    
    return {"id": category_id, "name": category.name, "group_name": category.group_name}

@router.get("/{category_id}")
async def get_category(category_id: int) -> Category:
    """Get a specific category by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, group_name FROM categories WHERE id = ?", (category_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return dict(row)

@router.put("/{category_id}")
async def update_category(category_id: int, category: CategoryCreate) -> Category:
    """Update an existing category"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE categories SET name = ?, group_name = ? WHERE id = ?",
        (category.name, category.group_name, category_id)
    )
    conn.commit()
    conn.close()
    
    return {"id": category_id, "name": category.name, "group_name": category.group_name}

@router.delete("/{category_id}")
async def delete_category(category_id: int):
    """Delete a category"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    conn.commit()
    conn.close()
    
    return {"id": category_id, "status": "deleted"}
