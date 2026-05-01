from fastapi import APIRouter
from typing import Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import sqlite3
from collections import defaultdict

router = APIRouter(prefix="/summary", tags=["summary"])

class MonthlySummary(BaseModel):
    month: str
    total_income: float
    total_expenses: float
    net: float
    category_breakdown: dict
    mode_breakdown: dict
    need_type_breakdown: dict

def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect('expenses.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_month_date_range(month_str=None):
    """Convert month string (YYYY-MM) to start and end dates"""
    if not month_str:
        month_str = datetime.now().strftime("%Y-%m")
    
    year, month = map(int, month_str.split('-'))
    start_date = f"{year:04d}-{month:02d}-01"
    
    # Get last day of month
    if month == 12:
        end_date = f"{year+1:04d}-01-01"
    else:
        end_date = f"{year:04d}-{month+1:02d}-01"
    
    return start_date, end_date

@router.get("/monthly")
async def get_monthly_summary(month: Optional[str] = None):
    """Get monthly expense and income summary"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    user_id = 1  # Should come from auth
    start_date, end_date = get_month_date_range(month)
    month_str = month or datetime.now().strftime("%Y-%m")
    
    # Get total expenses
    cursor.execute(
        "SELECT COALESCE(SUM(amount), 0) as total FROM expenses "
        "WHERE user_id = ? AND date >= ? AND date < ?",
        (user_id, start_date, end_date)
    )
    total_expenses = cursor.fetchone()[0]
    
    # Get total income
    cursor.execute(
        "SELECT COALESCE(SUM(amount), 0) as total FROM income "
        "WHERE user_id = ? AND date >= ? AND date < ?",
        (user_id, start_date, end_date)
    )
    total_income = cursor.fetchone()[0]
    
    # Get category breakdown for expenses
    cursor.execute(
        "SELECT c.name, SUM(e.amount) as total FROM expenses e "
        "LEFT JOIN categories c ON e.category_id = c.id "
        "WHERE e.user_id = ? AND e.date >= ? AND e.date < ? "
        "GROUP BY e.category_id ORDER BY total DESC",
        (user_id, start_date, end_date)
    )
    category_breakdown = {row[0] or 'Uncategorized': row[1] for row in cursor.fetchall()}
    
    # Get mode breakdown for expenses
    cursor.execute(
        "SELECT mode, SUM(amount) as total FROM expenses "
        "WHERE user_id = ? AND date >= ? AND date < ? "
        "GROUP BY mode ORDER BY total DESC",
        (user_id, start_date, end_date)
    )
    mode_breakdown = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Get need_type breakdown for expenses
    cursor.execute(
        "SELECT need_type, SUM(amount) as total FROM expenses "
        "WHERE user_id = ? AND date >= ? AND date < ? "
        "GROUP BY need_type ORDER BY total DESC",
        (user_id, start_date, end_date)
    )
    need_type_breakdown = {row[0]: row[1] for row in cursor.fetchall()}
    
    conn.close()
    
    return {
        "month": month_str,
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "net": round(total_income - total_expenses, 2),
        "category_breakdown": {k: round(v, 2) for k, v in category_breakdown.items()},
        "mode_breakdown": {k: round(v, 2) for k, v in mode_breakdown.items()},
        "need_type_breakdown": {k: round(v, 2) for k, v in need_type_breakdown.items()}
    }

@router.get("/trends")
async def get_expense_trends(months: int = 6):
    """Get expense and income trends over specified months"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    user_id = 1
    trends = []
    
    # Get last N months
    current_date = datetime.now()
    for i in range(months):
        month_date = current_date - timedelta(days=30*i)
        month_str = month_date.strftime("%Y-%m")
        start_date, end_date = get_month_date_range(month_str)
        
        # Expenses
        cursor.execute(
            "SELECT COALESCE(SUM(amount), 0) as total FROM expenses "
            "WHERE user_id = ? AND date >= ? AND date < ?",
            (user_id, start_date, end_date)
        )
        total_expenses = cursor.fetchone()[0]
        
        # Income
        cursor.execute(
            "SELECT COALESCE(SUM(amount), 0) as total FROM income "
            "WHERE user_id = ? AND date >= ? AND date < ?",
            (user_id, start_date, end_date)
        )
        total_income = cursor.fetchone()[0]
        
        trends.insert(0, {
            "month": month_str,
            "expenses": round(total_expenses, 2),
            "income": round(total_income, 2),
            "net": round(total_income - total_expenses, 2)
        })
    
    conn.close()
    return {"months": months, "trends": trends}

@router.get("/category-breakdown")
async def get_category_breakdown():
    """Get expense breakdown by category (all time)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    user_id = 1
    
    cursor.execute(
        "SELECT c.name, c.group_name, SUM(e.amount) as total, COUNT(e.id) as count "
        "FROM expenses e "
        "LEFT JOIN categories c ON e.category_id = c.id "
        "WHERE e.user_id = ? "
        "GROUP BY e.category_id ORDER BY total DESC",
        (user_id,)
    )
    
    categories = []
    for row in cursor.fetchall():
        categories.append({
            "name": row[0] or 'Uncategorized',
            "group": row[1],
            "total": round(row[2], 2),
            "count": row[3]
        })
    
    conn.close()
    return {"categories": categories}

@router.get("/mode-breakdown")
async def get_mode_breakdown():
    """Get expense breakdown by payment mode (all time)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    user_id = 1
    
    cursor.execute(
        "SELECT mode, SUM(amount) as total, COUNT(id) as count "
        "FROM expenses "
        "WHERE user_id = ? "
        "GROUP BY mode ORDER BY total DESC",
        (user_id,)
    )
    
    modes = []
    for row in cursor.fetchall():
        modes.append({
            "mode": row[0],
            "total": round(row[1], 2),
            "count": row[2]
        })
    
    conn.close()
    return {"modes": modes}

@router.get("/recurring")
async def get_recurring_expenses():
    """Get detected recurring expenses (same day of month, multiple months)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    user_id = 1
    
    # Get expenses grouped by day of month and amount (within ±5% tolerance)
    cursor.execute(
        "SELECT strftime('%d', date) as day_of_month, amount, note, COUNT(*) as occurrence "
        "FROM expenses "
        "WHERE user_id = ? AND note NOT LIKE '%UPI%' "  # Exclude UPI transactions
        "GROUP BY strftime('%d', date), ROUND(amount / 100) * 100 "
        "HAVING occurrence >= 2 "
        "ORDER BY occurrence DESC",
        (user_id,)
    )
    
    recurring = []
    for row in cursor.fetchall():
        recurring.append({
            "day_of_month": int(row[0]),
            "amount": round(row[1], 2),
            "description": row[2][:50] if row[2] else "Recurring",
            "occurrences": row[3]
        })
    
    conn.close()
    return {"recurring_expenses": recurring}
