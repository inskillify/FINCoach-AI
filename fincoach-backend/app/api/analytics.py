"""Analytics API endpoints for FINCoach AI Backend"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.transaction import Transaction
from app.models.goal import Goal
from app.models.jar import Jar
from app.schemas.user import UserResponse
from sqlalchemy import func

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])

@router.get("/dashboard", response_model=Dict[str, Any])
async def get_dashboard_analytics(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive dashboard analytics for the user"""
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        # Get transactions for the current month
        today = datetime.now()
        month_start = today.replace(day=1)
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user.id,
            Transaction.date >= month_start
        ).all()
        
        # Calculate totals
        total_income = sum(t.amount for t in transactions if t.type == "income")
        total_expense = sum(t.amount for t in transactions if t.type == "expense")
        net_balance = total_income - total_expense
        
        # Get category breakdown
        category_breakdown = {}
        for transaction in transactions:
            if transaction.type == "expense":
                category = transaction.category
                if category not in category_breakdown:
                    category_breakdown[category] = 0
                category_breakdown[category] += transaction.amount
        
        # Get goals progress
        goals = db.query(Goal).filter(Goal.user_id == user.id).all()
        goals_progress = []
        for goal in goals:
            progress_percentage = (goal.current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0
            goals_progress.append({
                "id": goal.id,
                "name": goal.name,
                "target": goal.target_amount,
                "current": goal.current_amount,
                "progress_percentage": round(progress_percentage, 2),
                "deadline": goal.deadline.isoformat() if goal.deadline else None
            })
        
        # Get jars summary
        jars = db.query(Jar).filter(Jar.user_id == user.id).all()
        total_saved = sum(jar.current_amount for jar in jars)
        
        return {
            "period": f"{month_start.strftime('%B %Y')}",
            "summary": {
                "total_income": round(total_income, 2),
                "total_expense": round(total_expense, 2),
                "net_balance": round(net_balance, 2),
                "total_saved": round(total_saved, 2)
            },
            "category_breakdown": {k: round(v, 2) for k, v in category_breakdown.items()},
            "goals_progress": goals_progress,
            "transaction_count": len(transactions),
            "goals_count": len(goals),
            "jars_count": len(jars)
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/spending-trends", response_model=Dict[str, Any])
async def get_spending_trends(
    months: int = 6,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get spending trends for the last N months"""
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        trends = []
        for i in range(months):
            month_date = datetime.now() - timedelta(days=30*i)
            month_start = month_date.replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            month_transactions = db.query(Transaction).filter(
                Transaction.user_id == user.id,
                Transaction.date >= month_start,
                Transaction.date <= month_end,
                Transaction.type == "expense"
            ).all()
            
            total_expense = sum(t.amount for t in month_transactions)
            trends.append({
                "month": month_start.strftime("%B %Y"),
                "total_expense": round(total_expense, 2),
                "transaction_count": len(month_transactions)
            })
        
        return {
            "trends": list(reversed(trends)),
            "average_monthly_expense": round(sum(t["total_expense"] for t in trends) / len(trends), 2) if trends else 0
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/category-analysis", response_model=Dict[str, Any])
async def get_category_analysis(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed category-wise spending analysis"""
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        today = datetime.now()
        month_start = today.replace(day=1)
        
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user.id,
            Transaction.date >= month_start,
            Transaction.type == "expense"
        ).all()
        
        category_analysis = {}
        for transaction in transactions:
            category = transaction.category
            if category not in category_analysis:
                category_analysis[category] = {
                    "total": 0,
                    "count": 0,
                    "average": 0
                }
            category_analysis[category]["total"] += transaction.amount
            category_analysis[category]["count"] += 1
        
        # Calculate averages
        for category in category_analysis:
            category_analysis[category]["average"] = round(
                category_analysis[category]["total"] / category_analysis[category]["count"], 2
            )
            category_analysis[category]["total"] = round(category_analysis[category]["total"], 2)
        
        total_expense = sum(cat["total"] for cat in category_analysis.values())
        
        # Add percentage
        for category in category_analysis:
            category_analysis[category]["percentage"] = round(
                (category_analysis[category]["total"] / total_expense * 100) if total_expense > 0 else 0, 2
            )
        
        return {
            "period": f"{month_start.strftime('%B %Y')}",
            "total_expense": round(total_expense, 2),
            "categories": category_analysis
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/financial-health", response_model=Dict[str, Any])
async def get_financial_health(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive financial health score and metrics"""
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        today = datetime.now()
        month_start = today.replace(day=1)
        
        # Get transactions
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user.id,
            Transaction.date >= month_start
        ).all()
        
        total_income = sum(t.amount for t in transactions if t.type == "income")
        total_expense = sum(t.amount for t in transactions if t.type == "expense")
        
        # Get savings
        jars = db.query(Jar).filter(Jar.user_id == user.id).all()
        total_saved = sum(jar.current_amount for jar in jars)
        
        # Get goals
        goals = db.query(Goal).filter(Goal.user_id == user.id).all()
        completed_goals = sum(1 for g in goals if g.current_amount >= g.target_amount)
        
        # Calculate health score (0-100)
        health_score = 0
        
        # Savings rate (0-30 points)
        if total_income > 0:
            savings_rate = (total_saved / total_income) * 100
            health_score += min(30, (savings_rate / 20) * 30)
        
        # Expense ratio (0-30 points)
        if total_income > 0:
            expense_ratio = (total_expense / total_income) * 100
            if expense_ratio <= 50:
                health_score += 30
            elif expense_ratio <= 70:
                health_score += 20
            elif expense_ratio <= 90:
                health_score += 10
        
        # Goal achievement (0-20 points)
        if goals:
            goal_completion_rate = (completed_goals / len(goals)) * 100
            health_score += (goal_completion_rate / 100) * 20
        
        # Jar diversity (0-20 points)
        if jars:
            health_score += min(20, len(jars) * 5)
        
        return {
            "health_score": round(health_score, 2),
            "health_status": "Excellent" if health_score >= 80 else "Good" if health_score >= 60 else "Fair" if health_score >= 40 else "Poor",
            "metrics": {
                "total_income": round(total_income, 2),
                "total_expense": round(total_expense, 2),
                "savings_rate": round((total_saved / total_income * 100) if total_income > 0 else 0, 2),
                "expense_ratio": round((total_expense / total_income * 100) if total_income > 0 else 0, 2),
                "total_saved": round(total_saved, 2),
                "goals_completed": completed_goals,
                "total_goals": len(goals),
                "jars_count": len(jars)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
