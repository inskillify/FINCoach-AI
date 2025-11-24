"""Prediction Engine - ML module for financial predictions"""
from typing import Dict, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.transaction import Transaction

class PredictionEngine:
    """Machine Learning engine for financial predictions"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def predict_next_month_spending(self, user_id: int) -> Dict:
        """Predict next month's spending using historical data"""
        # Get last 6 months of data
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        historical_data = self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.transaction_date >= six_months_ago
        ).all()
        
        if len(historical_data) < 20:
            return {"status": "insufficient_data", "message": "Need at least 6 months of data"}
        
        # Calculate monthly totals
        monthly_data = {}
        for transaction in historical_data:
            month_key = transaction.transaction_date.strftime("%Y-%m")
            if month_key not in monthly_data:
                monthly_data[month_key] = 0
            monthly_data[month_key] += transaction.amount
        
        # Simple exponential smoothing
        values = sorted(monthly_data.values())
        alpha = 0.3  # Smoothing factor
        
        if len(values) < 2:
            return {"status": "insufficient_data"}
        
        # Calculate forecast
        forecast = values[-1]
        for i in range(len(values) - 2, -1, -1):
            forecast = alpha * values[i] + (1 - alpha) * forecast
        
        return {
            "status": "success",
            "predicted_spending": round(forecast, 2),
            "confidence": 0.75,
            "method": "exponential_smoothing"
        }
    
    def predict_category_spending(self, user_id: int, category: str) -> Dict:
        """Predict spending for a specific category"""
        three_months_ago = datetime.utcnow() - timedelta(days=90)
        category_expenses = self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.category == category,
            Transaction.transaction_date >= three_months_ago
        ).all()
        
        if not category_expenses:
            return {"status": "no_data", "category": category}
        
        total = sum(t.amount for t in category_expenses)
        average = total / 3
        
        return {
            "status": "success",
            "category": category,
            "predicted_monthly_spending": round(average, 2),
            "transaction_count": len(category_expenses)
        }
    
    def predict_income_trend(self, user_id: int) -> Dict:
        """Predict income trend"""
        three_months_ago = datetime.utcnow() - timedelta(days=90)
        income_transactions = self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.type == "income",
            Transaction.transaction_date >= three_months_ago
        ).all()
        
        if not income_transactions:
            return {"status": "no_data"}
        
        # Calculate monthly income
        monthly_income = {}
        for transaction in income_transactions:
            month_key = transaction.transaction_date.strftime("%Y-%m")
            if month_key not in monthly_income:
                monthly_income[month_key] = 0
            monthly_income[month_key] += transaction.amount
        
        values = sorted(monthly_income.values())
        average = sum(values) / len(values)
        
        # Detect trend
        if len(values) >= 2:
            trend = "increasing" if values[-1] > values[0] else "decreasing"
        else:
            trend = "stable"
        
        return {
            "status": "success",
            "average_monthly_income": round(average, 2),
            "trend": trend,
            "months_analyzed": len(values)
        }
