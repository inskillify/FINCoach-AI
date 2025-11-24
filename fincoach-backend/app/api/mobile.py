"""Mobile App Integration API endpoints for FINCoach AI Backend"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.transaction import Transaction
from app.models.goal import Goal
from app.models.jar import Jar
from app.models.alert import Alert
from app.schemas.user import UserResponse
from app.schemas.transaction import TransactionCreate, TransactionResponse
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/mobile", tags=["Mobile Integration"])

class MobileDeviceRegister(BaseModel):
    device_id: str
    device_type: str  # ios, android
    device_name: str
    app_version: str

class MobileNotificationPreference(BaseModel):
    push_notifications: bool
    email_notifications: bool
    sms_notifications: bool
    notification_frequency: str  # daily, weekly, monthly

@router.post("/register-device")
async def register_mobile_device(
    device_data: MobileDeviceRegister,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Register a mobile device for push notifications"""
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        # Store device information (in production, use a Device model)
        return {
            "status": "success",
            "message": "Device registered successfully",
            "device_id": device_data.device_id,
            "device_type": device_data.device_type,
            "registered_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/notification-preferences")
async def update_notification_preferences(
    preferences: MobileNotificationPreference,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update mobile notification preferences"""
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        return {
            "status": "success",
            "message": "Notification preferences updated",
            "preferences": preferences.dict(),
            "updated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/quick-summary", response_model=Dict[str, Any])
async def get_mobile_quick_summary(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get quick summary for mobile home screen"""
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        today = datetime.now()
        month_start = today.replace(day=1)
        
        # Get today's transactions
        today_transactions = db.query(Transaction).filter(
            Transaction.user_id == user.id,
            Transaction.date >= today.replace(hour=0, minute=0, second=0, microsecond=0)
        ).all()
        
        today_expense = sum(t.amount for t in today_transactions if t.type == "expense")
        today_income = sum(t.amount for t in today_transactions if t.type == "income")
        
        # Get month summary
        month_transactions = db.query(Transaction).filter(
            Transaction.user_id == user.id,
            Transaction.date >= month_start
        ).all()
        
        month_expense = sum(t.amount for t in month_transactions if t.type == "expense")
        month_income = sum(t.amount for t in month_transactions if t.type == "income")
        
        # Get jars
        jars = db.query(Jar).filter(Jar.user_id == user.id).all()
        total_saved = sum(jar.current_amount for jar in jars)
        
        # Get pending alerts
        alerts = db.query(Alert).filter(
            Alert.user_id == user.id,
            Alert.is_read == False
        ).all()
        
        return {
            "today": {
                "income": round(today_income, 2),
                "expense": round(today_expense, 2),
                "net": round(today_income - today_expense, 2),
                "transaction_count": len(today_transactions)
            },
            "month": {
                "income": round(month_income, 2),
                "expense": round(month_expense, 2),
                "net": round(month_income - month_expense, 2),
                "transaction_count": len(month_transactions)
            },
            "savings": {
                "total_saved": round(total_saved, 2),
                "jars_count": len(jars)
            },
            "alerts": {
                "unread_count": len(alerts),
                "recent_alerts": [
                    {
                        "id": alert.id,
                        "title": alert.title,
                        "message": alert.message,
                        "severity": alert.severity,
                        "created_at": alert.created_at.isoformat()
                    }
                    for alert in alerts[:3]
                ]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/quick-transaction")
async def add_quick_transaction(
    transaction: TransactionCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Quick transaction add from mobile app"""
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        new_transaction = Transaction(
            user_id=user.id,
            amount=transaction.amount,
            category=transaction.category,
            description=transaction.description,
            type=transaction.type,
            date=transaction.date or datetime.now()
        )
        
        db.add(new_transaction)
        db.commit()
        db.refresh(new_transaction)
        
        return {
            "status": "success",
            "message": "Transaction added successfully",
            "transaction_id": new_transaction.id,
            "created_at": new_transaction.date.isoformat()
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/goals-mobile", response_model=List[Dict[str, Any]])
async def get_mobile_goals(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get goals optimized for mobile display"""
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        goals = db.query(Goal).filter(Goal.user_id == user.id).all()
        
        mobile_goals = []
        for goal in goals:
            progress = (goal.current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0
            mobile_goals.append({
                "id": goal.id,
                "name": goal.name,
                "target": round(goal.target_amount, 2),
                "current": round(goal.current_amount, 2),
                "progress": round(progress, 2),
                "deadline": goal.deadline.isoformat() if goal.deadline else None,
                "status": "completed" if progress >= 100 else "in_progress"
            })
        
        return sorted(mobile_goals, key=lambda x: x["progress"], reverse=True)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/jars-mobile", response_model=List[Dict[str, Any]])
async def get_mobile_jars(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get jars optimized for mobile display"""
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        jars = db.query(Jar).filter(Jar.user_id == user.id).all()
        
        mobile_jars = []
        for jar in jars:
            mobile_jars.append({
                "id": jar.id,
                "name": jar.name,
                "current_amount": round(jar.current_amount, 2),
                "target_amount": round(jar.target_amount, 2) if jar.target_amount else None,
                "priority": jar.priority,
                "color": jar.color if hasattr(jar, 'color') else "#3498db"
            })
        
        return sorted(mobile_jars, key=lambda x: x["priority"])
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/recent-transactions", response_model=List[Dict[str, Any]])
async def get_recent_transactions(
    limit: int = 10,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent transactions for mobile app"""
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user.id
        ).order_by(Transaction.date.desc()).limit(limit).all()
        
        return [
            {
                "id": t.id,
                "amount": round(t.amount, 2),
                "category": t.category,
                "description": t.description,
                "type": t.type,
                "date": t.date.isoformat()
            }
            for t in transactions
        ]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/sync-offline-data")
async def sync_offline_data(
    data: Dict[str, Any],
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync offline data from mobile app"""
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        # Process transactions from offline sync
        synced_count = 0
        if "transactions" in data:
            for trans_data in data["transactions"]:
                new_transaction = Transaction(
                    user_id=user.id,
                    amount=trans_data.get("amount"),
                    category=trans_data.get("category"),
                    description=trans_data.get("description"),
                    type=trans_data.get("type"),
                    date=datetime.fromisoformat(trans_data.get("date", datetime.now().isoformat()))
                )
                db.add(new_transaction)
                synced_count += 1
        
        db.commit()
        
        return {
            "status": "success",
            "message": "Offline data synced successfully",
            "synced_items": synced_count,
            "synced_at": datetime.now().isoformat()
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
