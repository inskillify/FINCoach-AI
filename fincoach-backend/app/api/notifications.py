"""Real-time Notifications API endpoints for FINCoach AI Backend"""
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.alert import Alert
from app.schemas.user import UserResponse
from app.schemas.alert import AlertResponse
import json

router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])

# Store active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
    
    async def disconnect(self, user_id: int, websocket: WebSocket):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    
    async def broadcast_to_user(self, user_id: int, message: dict):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"Error sending message: {e}")

manager = ConnectionManager()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, db: Session = Depends(get_db)):
    """WebSocket endpoint for real-time notifications"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        await manager.connect(user_id, websocket)
        
        # Send initial connection message
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        })
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
    except WebSocketDisconnect:
        await manager.disconnect(user_id, websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        await manager.disconnect(user_id, websocket)

@router.get("/unread-count", response_model=Dict[str, Any])
async def get_unread_notification_count(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get count of unread notifications"""
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        unread_alerts = db.query(Alert).filter(
            Alert.user_id == user.id,
            Alert.is_read == False
        ).count()
        
        return {
            "unread_count": unread_alerts,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/list", response_model=List[Dict[str, Any]])
async def get_notifications(
    limit: int = 20,
    offset: int = 0,
    unread_only: bool = False,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notifications with pagination"""
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        query = db.query(Alert).filter(Alert.user_id == user.id)
        
        if unread_only:
            query = query.filter(Alert.is_read == False)
        
        alerts = query.order_by(Alert.created_at.desc()).offset(offset).limit(limit).all()
        
        return [
            {
                "id": alert.id,
                "title": alert.title,
                "message": alert.message,
                "severity": alert.severity,
                "is_read": alert.is_read,
                "created_at": alert.created_at.isoformat(),
                "action_url": alert.action_url if hasattr(alert, 'action_url') else None
            }
            for alert in alerts
        ]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/{notification_id}/mark-as-read")
async def mark_notification_as_read(
    notification_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a notification as read"""
    try:
        alert = db.query(Alert).filter(
            Alert.id == notification_id,
            Alert.user_id == current_user.id
        ).first()
        
        if not alert:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
        
        alert.is_read = True
        db.commit()
        
        return {
            "status": "success",
            "message": "Notification marked as read",
            "notification_id": notification_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/mark-all-as-read")
async def mark_all_notifications_as_read(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read"""
    try:
        alerts = db.query(Alert).filter(
            Alert.user_id == current_user.id,
            Alert.is_read == False
        ).all()
        
        for alert in alerts:
            alert.is_read = True
        
        db.commit()
        
        return {
            "status": "success",
            "message": "All notifications marked as read",
            "count": len(alerts)
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a notification"""
    try:
        alert = db.query(Alert).filter(
            Alert.id == notification_id,
            Alert.user_id == current_user.id
        ).first()
        
        if not alert:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
        
        db.delete(alert)
        db.commit()
        
        return {
            "status": "success",
            "message": "Notification deleted",
            "notification_id": notification_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/by-severity/{severity}", response_model=List[Dict[str, Any]])
async def get_notifications_by_severity(
    severity: str,
    limit: int = 20,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notifications filtered by severity"""
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        alerts = db.query(Alert).filter(
            Alert.user_id == user.id,
            Alert.severity == severity
        ).order_by(Alert.created_at.desc()).limit(limit).all()
        
        return [
            {
                "id": alert.id,
                "title": alert.title,
                "message": alert.message,
                "severity": alert.severity,
                "is_read": alert.is_read,
                "created_at": alert.created_at.isoformat()
            }
            for alert in alerts
        ]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/send-test-notification")
async def send_test_notification(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a test notification to the user"""
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        test_alert = Alert(
            user_id=user.id,
            title="Test Notification",
            message="This is a test notification from FINCoach AI",
            severity="info",
            is_read=False
        )
        
        db.add(test_alert)
        db.commit()
        db.refresh(test_alert)
        
        # Broadcast to WebSocket if connected
        await manager.broadcast_to_user(user.id, {
            "type": "notification",
            "id": test_alert.id,
            "title": test_alert.title,
            "message": test_alert.message,
            "severity": test_alert.severity,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "status": "success",
            "message": "Test notification sent",
            "notification_id": test_alert.id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
