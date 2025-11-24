"""Anomaly Detector - ML module for detecting unusual transactions"""
from typing import Dict, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.transaction import Transaction

class AnomalyDetector:
    """Machine Learning module for detecting anomalous transactions"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def detect_unusual_spending(self, user_id: int, transaction_amount: float, category: str) -> Dict:
        """Detect if a transaction is unusual for the user"""
        # Get last 3 months of transactions in same category
        three_months_ago = datetime.utcnow() - timedelta(days=90)
        category_transactions = self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.category == category,
            Transaction.transaction_date >= three_months_ago
        ).all()
        
        if len(category_transactions) < 5:
            return {
                "status": "insufficient_data",
                "is_anomaly": False,
                "message": "Need more transaction history"
            }
        
        # Calculate statistics
        amounts = [t.amount for t in category_transactions]
        average = sum(amounts) / len(amounts)
        
        # Calculate standard deviation
        variance = sum((x - average) ** 2 for x in amounts) / len(amounts)
        std_dev = variance ** 0.5
        
        # Check if transaction is more than 2 standard deviations from mean
        z_score = (transaction_amount - average) / std_dev if std_dev > 0 else 0
        
        is_anomaly = abs(z_score) > 2
        
        return {
            "status": "success",
            "is_anomaly": is_anomaly,
            "transaction_amount": transaction_amount,
            "category_average": round(average, 2),
            "category_std_dev": round(std_dev, 2),
            "z_score": round(z_score, 2),
            "severity": self._get_severity(z_score),
            "recommendation": self._get_anomaly_recommendation(is_anomaly, z_score, average)
        }
    
    def detect_spending_spike(self, user_id: int) -> Dict:
        """Detect if there's a spending spike this month"""
        # Get current month spending
        current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        current_month_expenses = self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.transaction_date >= current_month_start
        ).all()
        
        current_month_total = sum(t.amount for t in current_month_expenses)
        
        # Get last 3 months average
        three_months_ago = datetime.utcnow() - timedelta(days=90)
        historical_expenses = self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.transaction_date >= three_months_ago,
            Transaction.transaction_date < current_month_start
        ).all()
        
        if not historical_expenses:
            return {
                "status": "insufficient_data",
                "is_spike": False,
                "message": "Need historical data"
            }
        
        historical_average = sum(t.amount for t in historical_expenses) / 3
        
        # Calculate percentage increase
        percentage_increase = ((current_month_total - historical_average) / historical_average * 100) if historical_average > 0 else 0
        
        is_spike = percentage_increase > 20  # More than 20% increase
        
        return {
            "status": "success",
            "is_spike": is_spike,
            "current_month_spending": round(current_month_total, 2),
            "historical_average": round(historical_average, 2),
            "percentage_increase": round(percentage_increase, 2),
            "recommendation": self._get_spike_recommendation(is_spike, percentage_increase)
        }
    
    def detect_unusual_pattern(self, user_id: int) -> Dict:
        """Detect unusual spending patterns"""
        # Get last 30 days transactions
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_transactions = self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.transaction_date >= thirty_days_ago
        ).all()
        
        if len(recent_transactions) < 10:
            return {
                "status": "insufficient_data",
                "patterns": []
            }
        
        patterns = []
        
        # Check for frequent small transactions
        small_transactions = [t for t in recent_transactions if t.amount < 100]
        if len(small_transactions) > len(recent_transactions) * 0.7:
            patterns.append({
                "pattern": "frequent_small_transactions",
                "description": "Many small transactions detected",
                "severity": "medium",
                "recommendation": "Consider consolidating purchases"
            })
        
        # Check for late night transactions
        late_night_transactions = [t for t in recent_transactions if t.transaction_date.hour >= 22 or t.transaction_date.hour <= 5]
        if len(late_night_transactions) > len(recent_transactions) * 0.3:
            patterns.append({
                "pattern": "late_night_spending",
                "description": "Significant late night spending detected",
                "severity": "low",
                "recommendation": "Review late night purchases"
            })
        
        # Check for weekend vs weekday spending
        weekend_transactions = [t for t in recent_transactions if t.transaction_date.weekday() >= 5]
        if len(weekend_transactions) > len(recent_transactions) * 0.6:
            patterns.append({
                "pattern": "weekend_heavy_spending",
                "description": "Most spending occurs on weekends",
                "severity": "low",
                "recommendation": "Plan weekend budget carefully"
            })
        
        return {
            "status": "success",
            "patterns": patterns,
            "total_patterns_detected": len(patterns)
        }
    
    def detect_duplicate_transactions(self, user_id: int, transaction_amount: float, category: str, description: str) -> Dict:
        """Detect potential duplicate transactions"""
        # Get transactions from last 24 hours
        one_day_ago = datetime.utcnow() - timedelta(hours=24)
        recent_transactions = self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.amount == transaction_amount,
            Transaction.category == category,
            Transaction.transaction_date >= one_day_ago
        ).all()
        
        if recent_transactions:
            return {
                "status": "success",
                "is_duplicate": True,
                "similar_transactions": len(recent_transactions),
                "recommendation": "This transaction appears to be a duplicate. Please verify."
            }
        
        return {
            "status": "success",
            "is_duplicate": False,
            "similar_transactions": 0
        }
    
    @staticmethod
    def _get_severity(z_score: float) -> str:
        """Get severity level based on z-score"""
        abs_z = abs(z_score)
        if abs_z > 3:
            return "critical"
        elif abs_z > 2:
            return "high"
        elif abs_z > 1:
            return "medium"
        else:
            return "low"
    
    @staticmethod
    def _get_anomaly_recommendation(is_anomaly: bool, z_score: float, average: float) -> str:
        """Get recommendation for anomalous transaction"""
        if not is_anomaly:
            return "Transaction is within normal range"
        
        if z_score > 0:
            return f"This transaction is significantly higher than your average of ${average:.2f}. Verify if this is intentional."
        else:
            return f"This transaction is significantly lower than your average of ${average:.2f}."
    
    @staticmethod
    def _get_spike_recommendation(is_spike: bool, percentage_increase: float) -> str:
        """Get recommendation for spending spike"""
        if not is_spike:
            return "Spending is within normal range"
        
        return f"Your spending has increased by {percentage_increase:.1f}% this month. Review your expenses to identify the cause."
