"""Alerts API routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.alert import Alert
from app.schemas.alert import AlertCreate, AlertResponse
from app.api.users import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_data: AlertCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new alert"""
    db_alert = Alert(
        user_id=current_user.id,
        title=alert_data.title,
        message=alert_data.message,
        severity=alert_data.severity
    )
    
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    
    return db_alert

@router.get("", response_model=list[AlertResponse])
async def list_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    is_read: bool = Query(None),
    severity: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user alerts"""
    query = db.query(Alert).filter(Alert.user_id == current_user.id)
    
    if is_read is not None:
        query = query.filter(Alert.is_read == is_read)
    if severity:
        query = query.filter(Alert.severity == severity)
    
    alerts = query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()
    return alerts

@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get alert by ID"""
    alert = db.query(Alert).filter(
        (Alert.id == alert_id) & (Alert.user_id == current_user.id)
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    return alert

@router.put("/{alert_id}/mark-as-read")
async def mark_alert_as_read(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark alert as read"""
    alert = db.query(Alert).filter(
        (Alert.id == alert_id) & (Alert.user_id == current_user.id)
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    alert.is_read = True
    db.add(alert)
    db.commit()
    db.refresh(alert)
    
    return {"message": "Alert marked as read", "alert": alert}

@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete alert"""
    alert = db.query(Alert).filter(
        (Alert.id == alert_id) & (Alert.user_id == current_user.id)
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    db.delete(alert)
    db.commit()

@router.get("/stats/summary", response_model=dict)
async def get_alerts_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get alerts summary"""
    alerts = db.query(Alert).filter(Alert.user_id == current_user.id).all()
    
    unread_count = sum(1 for a in alerts if not a.is_read)
    critical_count = sum(1 for a in alerts if a.severity == "critical")
    warning_count = sum(1 for a in alerts if a.severity == "warning")
    
    return {
        "total_alerts": len(alerts),
        "unread_alerts": unread_count,
        "critical_alerts": critical_count,
        "warning_alerts": warning_count
    }
