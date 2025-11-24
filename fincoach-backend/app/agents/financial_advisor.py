"""Financial Advisor Agent - Provides personalized financial advice"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.transaction import Transaction
from app.models.goal import Goal
from app.models.jar import Jar

class FinancialAdvisor:
    """AI Agent for providing financial advice"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def analyze_spending_patterns(self, user_id: int) -> Dict:
        """Analyze user spending patterns"""
        transactions = self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense"
        ).all()
        
        if not transactions:
            return {"status": "no_data", "message": "No expense data available"}
        
        # Calculate spending by category
        category_spending = {}
        for transaction in transactions:
            category = transaction.category
            if category not in category_spending:
                category_spending[category] = 0
            category_spending[category] += transaction.amount
        
        # Sort by highest spending
        sorted_categories = sorted(category_spending.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "status": "success",
            "total_expenses": sum(t.amount for t in transactions),
            "transaction_count": len(transactions),
            "category_breakdown": dict(sorted_categories),
            "top_spending_category": sorted_categories[0][0] if sorted_categories else None,
            "top_spending_amount": sorted_categories[0][1] if sorted_categories else 0
        }
    
    def get_budget_recommendations(self, user_id: int) -> Dict:
        """Get budget recommendations based on spending"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"status": "error", "message": "User not found"}
        
        spending_analysis = self.analyze_spending_patterns(user_id)
        
        if spending_analysis["status"] != "success":
            return spending_analysis
        
        monthly_income = user.monthly_income
        total_expenses = spending_analysis["total_expenses"]
        
        # Calculate savings rate
        savings_rate = ((monthly_income - total_expenses) / monthly_income * 100) if monthly_income > 0 else 0
        
        recommendations = []
        
        if savings_rate < 10:
            recommendations.append({
                "priority": "high",
                "message": "Your savings rate is below 10%. Consider reducing discretionary spending.",
                "action": "Review entertainment and shopping expenses"
            })
        
        if spending_analysis["top_spending_category"] == "food":
            recommendations.append({
                "priority": "medium",
                "message": "Food expenses are your highest spending category.",
                "action": "Consider meal planning and cooking at home"
            })
        
        if total_expenses > monthly_income:
            recommendations.append({
                "priority": "critical",
                "message": "You are spending more than your income!",
                "action": "Immediately reduce expenses or increase income"
            })
        
        return {
            "status": "success",
            "monthly_income": monthly_income,
            "total_expenses": total_expenses,
            "savings_rate": round(savings_rate, 2),
            "recommendations": recommendations
        }
    
    def suggest_savings_allocation(self, user_id: int) -> Dict:
        """Suggest optimal savings allocation"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"status": "error", "message": "User not found"}
        
        monthly_income = user.monthly_income
        if monthly_income <= 0:
            return {"status": "error", "message": "Invalid monthly income"}
        
        # 50-30-20 rule: 50% needs, 30% wants, 20% savings
        needs = monthly_income * 0.50
        wants = monthly_income * 0.30
        savings = monthly_income * 0.20
        
        return {
            "status": "success",
            "allocation_rule": "50-30-20",
            "needs": round(needs, 2),
            "wants": round(wants, 2),
            "savings": round(savings, 2),
            "description": {
                "needs": "Essential expenses (food, utilities, rent)",
                "wants": "Discretionary spending (entertainment, dining out)",
                "savings": "Emergency fund, investments, goals"
            }
        }
    
    def get_financial_health_score(self, user_id: int) -> Dict:
        """Calculate financial health score (0-100)"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"status": "error", "message": "User not found"}
        
        score = 0
        factors = {}
        
        # Factor 1: Budget tracking (20 points)
        if user.monthly_budget > 0:
            score += 20
            factors["budget_tracking"] = 20
        
        # Factor 2: Income stability (20 points)
        if user.monthly_income > 0:
            score += 20
            factors["income_stability"] = 20
        
        # Factor 3: Active goals (20 points)
        goals = self.db.query(Goal).filter(
            Goal.user_id == user_id,
            Goal.status == "active"
        ).all()
        if len(goals) > 0:
            score += 20
            factors["active_goals"] = 20
        
        # Factor 4: Savings jars (20 points)
        jars = self.db.query(Jar).filter(
            Jar.user_id == user_id,
            Jar.is_active == 1
        ).all()
        if len(jars) > 0:
            score += 20
            factors["savings_jars"] = 20
        
        # Factor 5: Spending discipline (20 points)
        spending_analysis = self.analyze_spending_patterns(user_id)
        if spending_analysis["status"] == "success":
            total_expenses = spending_analysis["total_expenses"]
            if user.monthly_budget > 0 and total_expenses <= user.monthly_budget:
                score += 20
                factors["spending_discipline"] = 20
        
        return {
            "status": "success",
            "financial_health_score": min(score, 100),
            "factors": factors,
            "rating": self._get_rating(score),
            "recommendations": self._get_score_recommendations(score)
        }
    
    @staticmethod
    def _get_rating(score: int) -> str:
        """Get rating based on score"""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        else:
            return "Poor"
    
    @staticmethod
    def _get_score_recommendations(score: int) -> List[str]:
        """Get recommendations based on score"""
        recommendations = []
        
        if score < 40:
            recommendations.append("Start tracking your budget immediately")
            recommendations.append("Set up at least one financial goal")
        elif score < 60:
            recommendations.append("Increase your savings rate")
            recommendations.append("Create more savings jars for different goals")
        elif score < 80:
            recommendations.append("Maintain your current financial discipline")
            recommendations.append("Consider increasing your savings goals")
        else:
            recommendations.append("Excellent financial management!")
            recommendations.append("Consider investing for long-term growth")
        
        return recommendations
