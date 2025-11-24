"""Prediction Agent - Forecasts financial trends"""
from typing import Dict, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.models.user import User

class PredictionAgent:
    """AI Agent for predicting financial trends"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def predict_monthly_expenses(self, user_id: int, months_ahead: int = 3) -> Dict:
        """Predict future monthly expenses"""
        # Get last 6 months of data
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        historical_expenses = self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.transaction_date >= six_months_ago
        ).all()
        
        if len(historical_expenses) < 20:
            return {
                "status": "warning",
                "message": "Insufficient historical data for accurate prediction",
                "recommendation": "Track expenses for at least 6 months"
            }
        
        # Calculate monthly totals
        monthly_totals = {}
        for expense in historical_expenses:
            month_key = expense.transaction_date.strftime("%Y-%m")
            if month_key not in monthly_totals:
                monthly_totals[month_key] = 0
            monthly_totals[month_key] += expense.amount
        
        # Simple moving average prediction
        amounts = sorted(monthly_totals.values())
        average = sum(amounts) / len(amounts)
        
        # Generate predictions
        predictions = []
        current_date = datetime.utcnow()
        
        for i in range(1, months_ahead + 1):
            future_date = current_date + timedelta(days=30*i)
            # Add seasonal variation (simplified)
            seasonal_factor = 1.0 + (0.05 * (i % 3))
            predicted_amount = average * seasonal_factor
            
            predictions.append({
                "month": future_date.strftime("%B %Y"),
                "predicted_expense": round(predicted_amount, 2),
                "confidence": "medium"
            })
        
        return {
            "status": "success",
            "historical_average": round(average, 2),
            "predictions": predictions,
            "recommendation": "Use these predictions to plan your budget for upcoming months"
        }
    
    def predict_savings_potential(self, user_id: int) -> Dict:
        """Predict potential monthly savings"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"status": "error", "message": "User not found"}
        
        monthly_income = user.monthly_income
        
        # Get last 3 months expenses
        three_months_ago = datetime.utcnow() - timedelta(days=90)
        recent_expenses = self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.transaction_date >= three_months_ago
        ).all()
        
        if not recent_expenses:
            return {
                "status": "warning",
                "message": "No expense data available",
                "recommendation": "Track expenses to get savings predictions"
            }
        
        total_expenses = sum(t.amount for t in recent_expenses)
        average_monthly_expense = total_expenses / 3
        
        current_savings = monthly_income - average_monthly_expense
        
        # Predict potential savings with 10% reduction in expenses
        optimized_expense = average_monthly_expense * 0.9
        optimized_savings = monthly_income - optimized_expense
        
        savings_increase = optimized_savings - current_savings
        
        return {
            "status": "success",
            "monthly_income": monthly_income,
            "current_monthly_expense": round(average_monthly_expense, 2),
            "current_monthly_savings": round(current_savings, 2),
            "optimized_monthly_expense": round(optimized_expense, 2),
            "optimized_monthly_savings": round(optimized_savings, 2),
            "potential_savings_increase": round(savings_increase, 2),
            "recommendation": f"By reducing expenses by 10%, you could save an additional ${savings_increase:.2f} monthly"
        }
    
    def predict_goal_completion(self, user_id: int, goal_id: int) -> Dict:
        """Predict when a goal will be completed"""
        from app.models.goal import Goal
        
        goal = self.db.query(Goal).filter(
            Goal.id == goal_id,
            Goal.user_id == user_id
        ).first()
        
        if not goal:
            return {"status": "error", "message": "Goal not found"}
        
        # Get recent savings rate
        three_months_ago = datetime.utcnow() - timedelta(days=90)
        recent_income = self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.type == "income",
            Transaction.transaction_date >= three_months_ago
        ).all()
        
        recent_expenses = self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.transaction_date >= three_months_ago
        ).all()
        
        total_income = sum(t.amount for t in recent_income)
        total_expenses = sum(t.amount for t in recent_expenses)
        monthly_savings = (total_income - total_expenses) / 3 if total_income > 0 else 0
        
        if monthly_savings <= 0:
            return {
                "status": "warning",
                "message": "Negative or zero savings rate",
                "recommendation": "Increase income or reduce expenses to achieve this goal"
            }
        
        amount_remaining = goal.target_amount - goal.current_amount
        months_needed = amount_remaining / monthly_savings if monthly_savings > 0 else float('inf')
        
        # Calculate predicted completion date
        predicted_completion = datetime.utcnow() + timedelta(days=months_needed*30)
        
        # Compare with deadline
        days_until_deadline = (goal.deadline - datetime.utcnow()).days
        on_track = months_needed * 30 <= days_until_deadline
        
        return {
            "status": "success",
            "goal_title": goal.title,
            "target_amount": goal.target_amount,
            "current_amount": goal.current_amount,
            "amount_remaining": round(amount_remaining, 2),
            "monthly_savings_rate": round(monthly_savings, 2),
            "months_needed": round(months_needed, 2),
            "predicted_completion_date": predicted_completion.strftime("%B %d, %Y"),
            "deadline": goal.deadline.strftime("%B %d, %Y"),
            "on_track": on_track,
            "recommendation": self._get_completion_recommendation(on_track, months_needed)
        }
    
    def predict_spending_by_category(self, user_id: int) -> Dict:
        """Predict spending by category for next month"""
        # Get last 3 months by category
        three_months_ago = datetime.utcnow() - timedelta(days=90)
        expenses = self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.transaction_date >= three_months_ago
        ).all()
        
        if not expenses:
            return {
                "status": "warning",
                "message": "No expense data available",
                "recommendation": "Track expenses to get category predictions"
            }
        
        # Calculate category totals
        category_totals = {}
        for expense in expenses:
            category = expense.category
            if category not in category_totals:
                category_totals[category] = 0
            category_totals[category] += expense.amount
        
        # Calculate monthly averages
        category_predictions = {}
        for category, total in category_totals.items():
            monthly_avg = total / 3
            category_predictions[category] = round(monthly_avg, 2)
        
        # Sort by highest spending
        sorted_predictions = sorted(category_predictions.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "status": "success",
            "predicted_spending_by_category": dict(sorted_predictions),
            "total_predicted_spending": round(sum(category_predictions.values()), 2),
            "recommendation": "Use these predictions to set category budgets"
        }
    
    @staticmethod
    def _get_completion_recommendation(on_track: bool, months_needed: float) -> str:
        """Get goal completion recommendation"""
        if on_track:
            return f"On track! Goal will be completed in approximately {months_needed:.1f} months."
        else:
            return f"Behind schedule. Increase monthly savings to meet deadline."
