"""Jar database model"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from app.core.database import Base

class JarPriority(str, PyEnum):
    """Jar priority enum"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Jar(Base):
    """Jar model for savings goals"""
    __tablename__ = "jars"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    priority = Column(Enum(JarPriority), default=JarPriority.MEDIUM)
    color = Column(String(7), default="#3B82F6")
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="jars")
    
    def __repr__(self):
        return f"<Jar(id={self.id}, user_id={self.user_id}, name={self.name}, current={self.current_amount}/{self.target_amount})>"
