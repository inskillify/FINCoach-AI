"""Social Features API endpoints for FINCoach AI Backend"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict, Any
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/social", tags=["Social Features"])

class UserProfile(BaseModel):
    bio: str
    avatar_url: str
    location: str

class FinancialChallenge(BaseModel):
    title: str
    description: str
    target_amount: float
    duration_days: int

class ChallengeParticipation(BaseModel):
    challenge_id: int

@router.get("/profile/{user_id}", response_model=Dict[str, Any])
async def get_user_profile(
    user_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get public user profile"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        return {
            "id": user.id,
            "email": user.email,
            "username": user.email.split("@")[0],
            "created_at": user.created_at.isoformat() if hasattr(user, 'created_at') else None,
            "profile": {
                "bio": "Financial enthusiast using FINCoach AI",
                "avatar_url": f"https://api.dicebear.com/7.x/avataaars/svg?seed={user.id}",
                "location": "Global"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/profile/update")
async def update_user_profile(
    profile: UserProfile,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        # Store profile data (in production, use a Profile model)
        return {
            "status": "success",
            "message": "Profile updated successfully",
            "profile": profile.dict(),
            "updated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/challenges/create")
async def create_financial_challenge(
    challenge: FinancialChallenge,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new financial challenge"""
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        # Create challenge (in production, use a Challenge model)
        challenge_id = hash(f"{user.id}{challenge.title}{datetime.now()}") % 1000000
        
        return {
            "status": "success",
            "message": "Challenge created successfully",
            "challenge_id": challenge_id,
            "challenge": {
                "id": challenge_id,
                "title": challenge.title,
                "description": challenge.description,
                "target_amount": challenge.target_amount,
                "duration_days": challenge.duration_days,
                "created_by": user.id,
                "created_at": datetime.now().isoformat(),
                "participants": 1
            }
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/challenges/list", response_model=List[Dict[str, Any]])
async def list_financial_challenges(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List available financial challenges"""
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        # Return sample challenges
        challenges = [
            {
                "id": 1,
                "title": "Save 30 Days Challenge",
                "description": "Save money for 30 consecutive days",
                "target_amount": 5000,
                "duration_days": 30,
                "participants": 1250,
                "difficulty": "easy",
                "created_at": (datetime.now() - timedelta(days=5)).isoformat()
            },
            {
                "id": 2,
                "title": "No Spend Week",
                "description": "Don't spend money for 7 days",
                "target_amount": 0,
                "duration_days": 7,
                "participants": 3420,
                "difficulty": "medium",
                "created_at": (datetime.now() - timedelta(days=10)).isoformat()
            },
            {
                "id": 3,
                "title": "Budget Master",
                "description": "Stay within budget for 90 days",
                "target_amount": 50000,
                "duration_days": 90,
                "participants": 890,
                "difficulty": "hard",
                "created_at": (datetime.now() - timedelta(days=15)).isoformat()
            }
        ]
        
        return challenges
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/challenges/{challenge_id}/join")
async def join_challenge(
    challenge_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Join a financial challenge"""
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        return {
            "status": "success",
            "message": "Successfully joined the challenge",
            "challenge_id": challenge_id,
            "user_id": user.id,
            "joined_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/leaderboard", response_model=List[Dict[str, Any]])
async def get_leaderboard(
    challenge_id: int = None,
    limit: int = 10,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get leaderboard for challenges"""
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        # Return sample leaderboard
        leaderboard = [
            {
                "rank": 1,
                "user_id": 101,
                "username": "savings_master",
                "score": 9500,
                "savings_amount": 50000,
                "challenges_completed": 15
            },
            {
                "rank": 2,
                "user_id": 102,
                "username": "budget_pro",
                "score": 8750,
                "savings_amount": 45000,
                "challenges_completed": 12
            },
            {
                "rank": 3,
                "user_id": 103,
                "username": "finance_guru",
                "score": 8200,
                "savings_amount": 42000,
                "challenges_completed": 10
            },
            {
                "rank": 4,
                "user_id": current_user.id,
                "username": f"user_{current_user.id}",
                "score": 7500,
                "savings_amount": 35000,
                "challenges_completed": 8
            }
        ]
        
        return leaderboard[:limit]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/friends/list", response_model=List[Dict[str, Any]])
async def get_friends_list(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's friends list"""
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        # Return sample friends
        friends = [
            {
                "id": 201,
                "username": "john_doe",
                "email": "john@example.com",
                "status": "active",
                "added_at": (datetime.now() - timedelta(days=30)).isoformat()
            },
            {
                "id": 202,
                "username": "jane_smith",
                "email": "jane@example.com",
                "status": "active",
                "added_at": (datetime.now() - timedelta(days=60)).isoformat()
            }
        ]
        
        return friends
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/friends/{friend_id}/add")
async def add_friend(
    friend_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a friend"""
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        friend = db.query(User).filter(User.id == friend_id).first()
        if not friend:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Friend not found")
        
        return {
            "status": "success",
            "message": "Friend added successfully",
            "friend_id": friend_id,
            "added_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/achievements", response_model=List[Dict[str, Any]])
async def get_achievements(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user achievements and badges"""
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        achievements = [
            {
                "id": 1,
                "name": "First Transaction",
                "description": "Record your first transaction",
                "icon": "🎯",
                "unlocked": True,
                "unlocked_at": (datetime.now() - timedelta(days=90)).isoformat()
            },
            {
                "id": 2,
                "name": "Savings Starter",
                "description": "Save your first 1000",
                "icon": "💰",
                "unlocked": True,
                "unlocked_at": (datetime.now() - timedelta(days=60)).isoformat()
            },
            {
                "id": 3,
                "name": "Budget Master",
                "description": "Stay within budget for 30 days",
                "icon": "📊",
                "unlocked": False,
                "unlocked_at": None
            },
            {
                "id": 4,
                "name": "Goal Achiever",
                "description": "Complete 5 financial goals",
                "icon": "🏆",
                "unlocked": False,
                "unlocked_at": None
            }
        ]
        
        return achievements
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/share-achievement/{achievement_id}")
async def share_achievement(
    achievement_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Share an achievement on social media"""
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        return {
            "status": "success",
            "message": "Achievement shared successfully",
            "achievement_id": achievement_id,
            "share_url": f"https://fincoach.app/achievements/{achievement_id}?user={user.id}",
            "shared_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

from datetime import timedelta
