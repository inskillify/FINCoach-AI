"""Goals API routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import get_db
from app.models.goal import Goal
from app.schemas.goal import GoalCreate, GoalUpdate, GoalResponse
from app.api.users import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    goal_data: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new financial goal"""
    db_goal = Goal(
        user_id=current_user.id,
        title=goal_data.title,
        description=goal_data.description,
        target_amount=goal_data.target_amount,
        deadline=goal_data.deadline,
        category=goal_data.category
    )
    
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    
    return db_goal

@router.get("", response_model=list[GoalResponse])
async def list_goals(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user goals"""
    query = db.query(Goal).filter(Goal.user_id == current_user.id)
    
    if status:
        query = query.filter(Goal.status == status)
    
    goals = query.order_by(Goal.deadline).offset(skip).limit(limit).all()
    return goals

@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get goal by ID"""
    goal = db.query(Goal).filter(
        (Goal.id == goal_id) & (Goal.user_id == current_user.id)
    ).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )
    
    return goal

@router.put("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: int,
    goal_update: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update goal"""
    goal = db.query(Goal).filter(
        (Goal.id == goal_id) & (Goal.user_id == current_user.id)
    ).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )
    
    update_data = goal_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(goal, field, value)
    
    db.add(goal)
    db.commit()
    db.refresh(goal)
    
    return goal

@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete goal"""
    goal = db.query(Goal).filter(
        (Goal.id == goal_id) & (Goal.user_id == current_user.id)
    ).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )
    
    db.delete(goal)
    db.commit()

@router.post("/{goal_id}/add-progress")
async def add_goal_progress(
    goal_id: int,
    amount: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add progress to goal"""
    goal = db.query(Goal).filter(
        (Goal.id == goal_id) & (Goal.user_id == current_user.id)
    ).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )
    
    goal.current_amount += amount
    
    if goal.current_amount >= goal.target_amount:
        goal.status = "completed"
    
    db.add(goal)
    db.commit()
    db.refresh(goal)
    
    return {"message": "Progress added successfully", "goal": goal}

@router.get("/{goal_id}/progress", response_model=dict)
async def get_goal_progress(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get goal progress"""
    goal = db.query(Goal).filter(
        (Goal.id == goal_id) & (Goal.user_id == current_user.id)
    ).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )
    
    progress_percentage = (goal.current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0
    days_remaining = (goal.deadline - datetime.utcnow()).days
    
    return {
        "goal_id": goal.id,
        "title": goal.title,
        "current_amount": goal.current_amount,
        "target_amount": goal.target_amount,
        "remaining_amount": goal.target_amount - goal.current_amount,
        "progress_percentage": round(progress_percentage, 2),
        "days_remaining": days_remaining,
        "status": goal.status
    }
