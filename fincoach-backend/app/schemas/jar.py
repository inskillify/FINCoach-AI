"""Jar Pydantic schemas"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class JarPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class JarBase(BaseModel):
    name: str
    description: Optional[str] = None
    target_amount: float
    priority: JarPriority = JarPriority.MEDIUM
    color: str = "#3B82F6"

class JarCreate(JarBase):
    pass

class JarUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_amount: Optional[float] = None
    current_amount: Optional[float] = None
    priority: Optional[JarPriority] = None
    color: Optional[str] = None

class JarResponse(JarBase):
    id: int
    user_id: int
    current_amount: float
    is_active: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
