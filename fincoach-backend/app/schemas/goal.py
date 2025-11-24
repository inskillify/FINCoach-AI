"""Goal Pydantic schemas"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class GoalStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

class GoalBase(BaseModel):
    title: str
    description: Optional[str] = None
    target_amount: float
    deadline: datetime
    category: Optional[str] = None

class GoalCreate(GoalBase):
    pass

class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    target_amount: Optional[float] = None
    current_amount: Optional[float] = None
    deadline: Optional[datetime] = None
    status: Optional[GoalStatus] = None
    category: Optional[str] = None

class GoalResponse(GoalBase):
    id: int
    user_id: int
    current_amount: float
    status: GoalStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
