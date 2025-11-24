"""Custom validators for the application"""
from pydantic import field_validator
from datetime import datetime

class TransactionValidator:
    """Validators for transaction data"""
    
    @staticmethod
    def validate_amount(amount: float) -> float:
        """Validate transaction amount"""
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")
        if amount > 10000000:  # 1 crore limit
            raise ValueError("Amount exceeds maximum limit")
        return amount
    
    @staticmethod
    def validate_transaction_date(date: datetime) -> datetime:
        """Validate transaction date"""
        if date > datetime.utcnow():
            raise ValueError("Transaction date cannot be in the future")
        return date

class GoalValidator:
    """Validators for goal data"""
    
    @staticmethod
    def validate_deadline(deadline: datetime) -> datetime:
        """Validate goal deadline"""
        if deadline <= datetime.utcnow():
            raise ValueError("Deadline must be in the future")
        return deadline
    
    @staticmethod
    def validate_target_amount(amount: float) -> float:
        """Validate goal target amount"""
        if amount <= 0:
            raise ValueError("Target amount must be greater than 0")
        return amount

class BudgetValidator:
    """Validators for budget data"""
    
    @staticmethod
    def validate_budget_amount(amount: float) -> float:
        """Validate budget amount"""
        if amount < 0:
            raise ValueError("Budget amount cannot be negative")
        return amount
