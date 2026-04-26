from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/categories", tags=["categories"])

class CategoryCreate(BaseModel):
    name: str
    group_name: str  # household, personal, official, financial, misc

class Category(BaseModel):
    id: int
    name: str
    group_name: str

@router.get("/")
async def get_categories(group_name: Optional[str] = None) -> List[Category]:
    """Get all categories, optionally filtered by group"""
    # TODO: Implement database query
    return []

@router.post("/")
async def create_category(category: CategoryCreate) -> Category:
    """Create a new category"""
    # TODO: Implement database insert
    return {"id": 1, "name": category.name, "group_name": category.group_name}

@router.get("/{category_id}")
async def get_category(category_id: int) -> Category:
    """Get a specific category by ID"""
    # TODO: Implement database query
    return {}

@router.put("/{category_id}")
async def update_category(category_id: int, category: CategoryCreate) -> Category:
    """Update an existing category"""
    # TODO: Implement database update
    return {"id": category_id, "name": category.name, "group_name": category.group_name}

@router.delete("/{category_id}")
async def delete_category(category_id: int):
    """Delete a category"""
    # TODO: Implement database delete
    return {"id": category_id, "status": "deleted"}