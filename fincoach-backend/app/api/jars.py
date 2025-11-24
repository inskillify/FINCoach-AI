"""Jars API routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.jar import Jar
from app.schemas.jar import JarCreate, JarUpdate, JarResponse
from app.api.users import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("", response_model=JarResponse, status_code=status.HTTP_201_CREATED)
async def create_jar(
    jar_data: JarCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new savings jar"""
    db_jar = Jar(
        user_id=current_user.id,
        name=jar_data.name,
        description=jar_data.description,
        target_amount=jar_data.target_amount,
        priority=jar_data.priority,
        color=jar_data.color
    )
    
    db.add(db_jar)
    db.commit()
    db.refresh(db_jar)
    
    return db_jar

@router.get("", response_model=list[JarResponse])
async def list_jars(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    priority: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user jars"""
    query = db.query(Jar).filter(Jar.user_id == current_user.id)
    
    if priority:
        query = query.filter(Jar.priority == priority)
    
    jars = query.offset(skip).limit(limit).all()
    return jars

@router.get("/{jar_id}", response_model=JarResponse)
async def get_jar(
    jar_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get jar by ID"""
    jar = db.query(Jar).filter(
        (Jar.id == jar_id) & (Jar.user_id == current_user.id)
    ).first()
    
    if not jar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Jar not found"
        )
    
    return jar

@router.put("/{jar_id}", response_model=JarResponse)
async def update_jar(
    jar_id: int,
    jar_update: JarUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update jar"""
    jar = db.query(Jar).filter(
        (Jar.id == jar_id) & (Jar.user_id == current_user.id)
    ).first()
    
    if not jar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Jar not found"
        )
    
    update_data = jar_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(jar, field, value)
    
    db.add(jar)
    db.commit()
    db.refresh(jar)
    
    return jar

@router.delete("/{jar_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_jar(
    jar_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete jar"""
    jar = db.query(Jar).filter(
        (Jar.id == jar_id) & (Jar.user_id == current_user.id)
    ).first()
    
    if not jar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Jar not found"
        )
    
    db.delete(jar)
    db.commit()

@router.post("/{jar_id}/add-funds")
async def add_funds_to_jar(
    jar_id: int,
    amount: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add funds to jar"""
    jar = db.query(Jar).filter(
        (Jar.id == jar_id) & (Jar.user_id == current_user.id)
    ).first()
    
    if not jar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Jar not found"
        )
    
    jar.current_amount += amount
    db.add(jar)
    db.commit()
    db.refresh(jar)
    
    return {"message": "Funds added successfully", "jar": jar}

@router.get("/{jar_id}/progress", response_model=dict)
async def get_jar_progress(
    jar_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get jar progress"""
    jar = db.query(Jar).filter(
        (Jar.id == jar_id) & (Jar.user_id == current_user.id)
    ).first()
    
    if not jar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Jar not found"
        )
    
    progress_percentage = (jar.current_amount / jar.target_amount * 100) if jar.target_amount > 0 else 0
    
    return {
        "jar_id": jar.id,
        "name": jar.name,
        "current_amount": jar.current_amount,
        "target_amount": jar.target_amount,
        "remaining_amount": jar.target_amount - jar.current_amount,
        "progress_percentage": round(progress_percentage, 2)
    }
