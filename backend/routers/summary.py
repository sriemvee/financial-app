from fastapi import APIRouter
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/summary", tags=["summary"])

class MonthlySummary(BaseModel):
    month: str
    total_expenses: float
    category_breakdown: dict
    mode_breakdown: dict
    need_type_breakdown: dict

@router.get("/monthly")
async def get_monthly_summary(month: Optional[str] = None):
    """Get monthly expense summary"""
    # TODO: Implement database query for monthly totals
    # TODO: Group by category, mode, need_type
    return {
        "month": month or datetime.now().strftime("%Y-%m"),
        "total_expenses": 0,
        "category_breakdown": {},
        "mode_breakdown": {},
        "need_type_breakdown": {}
    }

@router.get("/trends")
async def get_expense_trends(months: int = 6):
    """Get expense trends over specified months"""
    # TODO: Implement trend analysis
    return {"months": months, "trends": []}

@router.get("/recurring")
async def get_recurring_expenses():
    """Get detected recurring expenses"""
    # TODO: Implement recurring expense detection
    return {"recurring_expenses": []}

@router.get("/category-breakdown")
async def get_category_breakdown():
    """Get expense breakdown by category"""
    # TODO: Implement category breakdown query
    return {"categories": {}}

@router.get("/mode-breakdown")
async def get_mode_breakdown():
    """Get expense breakdown by payment mode"""
    # TODO: Implement mode breakdown query
    return {"modes": {}}