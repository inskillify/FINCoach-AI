"""Alert Pydantic schemas"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    ERROR = "error"

class AlertBase(BaseModel):
    title: str
    message: str
    severity: AlertSeverity = AlertSeverity.INFO

class AlertCreate(AlertBase):
    pass

class AlertResponse(AlertBase):
    id: int
    user_id: int
    is_read: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
