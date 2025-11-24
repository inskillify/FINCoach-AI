"""Risk Assessor Agent - Evaluates financial risks"""
from typing import Dict, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.transaction import Transaction
from app.models.goal import Goal

class RiskAssessor:
    """AI Agent for assessing financial risks"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def assess_emergency_fund(self, user_id: int) -> Dict:
        """Assess emergency fund adequacy"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"status": "error", "message": "User not found"}
        
        # Get last 3 months of expenses
        three_months_ago = datetime.utcnow() - timedelta(days=90)
        recent_expenses = self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.transaction_date >= three_months_ago
        ).all()
        
        if not recent_expenses:
            return {
                "status": "warning",
                "message": "Insufficient data to assess emergency fund",
                "recommendation": "Track expenses for 3 months"
            }
        
        total_expenses = sum(t.amount for t in recent_expenses)
        monthly_average = total_expenses / 3
        
        # Recommended emergency fund: 6 months of expenses
        recommended_fund = monthly_average * 6
        
        # Assess current savings (from jars)
        from app.models.jar import Jar
        jars = self.db.query(Jar).filter(Jar.user_id == user_id).all()
        current_savings = sum(j.current_amount for j in jars)
        
        coverage_months = (current_savings / monthly_average) if monthly_average > 0 else 0
        
        risk_level = "high"
        if coverage_months >= 6:
            risk_level = "low"
        elif coverage_months >= 3:
            risk_level = "medium"
        
        return {
            "status": "success",
            "monthly_average_expense": round(monthly_average, 2),
            "recommended_emergency_fund": round(recommended_fund, 2),
            "current_savings": round(current_savings, 2),
            "coverage_months": round(coverage_months, 2),
            "risk_level": risk_level,
            "recommendation": self._get_emergency_fund_recommendation(coverage_months)
        }
    
    def assess_debt_risk(self, user_id: int) -> Dict:
        """Assess debt and financial obligations risk"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"status": "error", "message": "User not found"}
        
        # Get monthly income and expenses
        monthly_income = user.monthly_income
        
        # Get last month expenses
        one_month_ago = datetime.utcnow() - timedelta(days=30)
        monthly_expenses = self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.transaction_date >= one_month_ago
        ).all()
        
        total_expenses = sum(t.amount for t in monthly_expenses)
        
        if monthly_income <= 0:
            return {
                "status": "warning",
                "message": "Income not set",
                "recommendation": "Set your monthly income for accurate assessment"
            }
        
        debt_to_income_ratio = (total_expenses / monthly_income) * 100
        
        risk_level = "low"
        if debt_to_income_ratio > 100:
            risk_level = "critical"
        elif debt_to_income_ratio > 80:
            risk_level = "high"
        elif debt_to_income_ratio > 60:
            risk_level = "medium"
        
        return {
            "status": "success",
            "monthly_income": monthly_income,
            "monthly_expenses": round(total_expenses, 2),
            "debt_to_income_ratio": round(debt_to_income_ratio, 2),
            "risk_level": risk_level,
            "recommendation": self._get_debt_risk_recommendation(debt_to_income_ratio)
        }
    
    def assess_goal_feasibility(self, user_id: int, goal_id: int) -> Dict:
        """Assess if a financial goal is feasible"""
        goal = self.db.query(Goal).filter(
            Goal.id == goal_id,
            Goal.user_id == user_id
        ).first()
        
        if not goal:
            return {"status": "error", "message": "Goal not found"}
        
        user = self.db.query(User).filter(User.id == user_id).first()
        
        # Calculate time remaining
        days_remaining = (goal.deadline - datetime.utcnow()).days
        months_remaining = days_remaining / 30
        
        if months_remaining <= 0:
            return {
                "status": "error",
                "message": "Goal deadline has passed",
                "feasibility": "impossible"
            }
        
        # Calculate required monthly savings
        amount_remaining = goal.target_amount - goal.current_amount
        required_monthly_savings = amount_remaining / months_remaining if months_remaining > 0 else 0
        
        # Get available monthly savings
        monthly_income = user.monthly_income
        one_month_ago = datetime.utcnow() - timedelta(days=30)
        monthly_expenses = sum(t.amount for t in self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.transaction_date >= one_month_ago
        ).all())
        
        available_monthly_savings = monthly_income - monthly_expenses
        
        # Assess feasibility
        if required_monthly_savings <= 0:
            feasibility = "achieved"
        elif required_monthly_savings <= available_monthly_savings:
            feasibility = "feasible"
        else:
            feasibility = "challenging"
        
        return {
            "status": "success",
            "goal_title": goal.title,
            "target_amount": goal.target_amount,
            "current_amount": goal.current_amount,
            "amount_remaining": round(amount_remaining, 2),
            "days_remaining": days_remaining,
            "months_remaining": round(months_remaining, 2),
            "required_monthly_savings": round(required_monthly_savings, 2),
            "available_monthly_savings": round(available_monthly_savings, 2),
            "feasibility": feasibility,
            "recommendation": self._get_feasibility_recommendation(feasibility, required_monthly_savings, available_monthly_savings)
        }
    
    def assess_spending_volatility(self, user_id: int) -> Dict:
        """Assess spending volatility and consistency"""
        # Get last 3 months of expenses
        three_months_ago = datetime.utcnow() - timedelta(days=90)
        expenses = self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.transaction_date >= three_months_ago
        ).all()
        
        if len(expenses) < 10:
            return {
                "status": "warning",
                "message": "Insufficient data for volatility assessment",
                "recommendation": "Track more transactions for accurate analysis"
            }
        
        # Calculate monthly totals
        monthly_totals = {}
        for expense in expenses:
            month_key = expense.transaction_date.strftime("%Y-%m")
            if month_key not in monthly_totals:
                monthly_totals[month_key] = 0
            monthly_totals[month_key] += expense.amount
        
        if len(monthly_totals) < 2:
            return {
                "status": "warning",
                "message": "Need at least 2 months of data",
                "recommendation": "Continue tracking expenses"
            }
        
        # Calculate standard deviation
        amounts = list(monthly_totals.values())
        average = sum(amounts) / len(amounts)
        variance = sum((x - average) ** 2 for x in amounts) / len(amounts)
        std_dev = variance ** 0.5
        
        volatility_percentage = (std_dev / average * 100) if average > 0 else 0
        
        volatility_level = "low"
        if volatility_percentage > 30:
            volatility_level = "high"
        elif volatility_percentage > 15:
            volatility_level = "medium"
        
        return {
            "status": "success",
            "average_monthly_spending": round(average, 2),
            "standard_deviation": round(std_dev, 2),
            "volatility_percentage": round(volatility_percentage, 2),
            "volatility_level": volatility_level,
            "recommendation": self._get_volatility_recommendation(volatility_level)
        }
    
    @staticmethod
    def _get_emergency_fund_recommendation(coverage_months: float) -> str:
        """Get emergency fund recommendation"""
        if coverage_months < 1:
            return "Critical: Build emergency fund immediately. Aim for 6 months of expenses."
        elif coverage_months < 3:
            return "Warning: Emergency fund is below recommended level. Target 6 months of expenses."
        elif coverage_months < 6:
            return "Good: Continue building emergency fund to reach 6 months."
        else:
            return "Excellent: Your emergency fund is well-established."
    
    @staticmethod
    def _get_debt_risk_recommendation(ratio: float) -> str:
        """Get debt risk recommendation"""
        if ratio > 100:
            return "Critical: You are spending more than you earn. Reduce expenses immediately."
        elif ratio > 80:
            return "High Risk: Your expenses are too high relative to income. Cut discretionary spending."
        elif ratio > 60:
            return "Medium Risk: Consider reducing expenses to improve financial health."
        else:
            return "Low Risk: Your expense-to-income ratio is healthy."
    
    @staticmethod
    def _get_feasibility_recommendation(feasibility: str, required: float, available: float) -> str:
        """Get goal feasibility recommendation"""
        if feasibility == "achieved":
            return "Goal target already reached!"
        elif feasibility == "feasible":
            return f"Goal is achievable. Save ${required:.2f} monthly."
        else:
            shortfall = required - available
            return f"Challenging: Need ${shortfall:.2f} more monthly. Consider extending deadline or reducing target."
    
    @staticmethod
    def _get_volatility_recommendation(level: str) -> str:
        """Get spending volatility recommendation"""
        if level == "high":
            return "Your spending is highly variable. Create a budget to stabilize expenses."
        elif level == "medium":
            return "Moderate spending variation. Track categories to identify patterns."
        else:
            return "Excellent: Your spending is consistent and predictable."
