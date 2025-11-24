"""API routes for ML Modules"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.ml_modules.prediction_engine import PredictionEngine
from app.ml_modules.categorizer import TransactionCategorizer
from app.ml_modules.anomaly_detector import AnomalyDetector
from app.security import get_current_user

router = APIRouter(prefix="/api/v1/ml", tags=["ml_modules"])

class TransactionInput(BaseModel):
    description: str
    amount: float = None

class AnomalyCheckInput(BaseModel):
    transaction_amount: float
    category: str

@router.post("/categorize")
def categorize_transaction(
    transaction: TransactionInput,
    current_user = Depends(get_current_user)
):
    """Automatically categorize a transaction"""
    categorizer = TransactionCategorizer()
    return categorizer.categorize_transaction(transaction.description, transaction.amount)

@router.post("/categorize-suggestions")
def get_category_suggestions(
    transaction: TransactionInput,
    current_user = Depends(get_current_user)
):
    """Get multiple category suggestions for a transaction"""
    categorizer = TransactionCategorizer()
    return {
        "status": "success",
        "suggestions": categorizer.get_category_suggestions(transaction.description)
    }

@router.get("/prediction/next-month-spending")
def predict_next_month_spending(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Predict next month's spending using ML"""
    engine = PredictionEngine(db)
    return engine.predict_next_month_spending(current_user.id)

@router.get("/prediction/category-spending/{category}")
def predict_category_spending(
    category: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Predict spending for a specific category"""
    engine = PredictionEngine(db)
    return engine.predict_category_spending(current_user.id, category)

@router.get("/prediction/income-trend")
def predict_income_trend(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Predict income trend"""
    engine = PredictionEngine(db)
    return engine.predict_income_trend(current_user.id)

@router.post("/anomaly/detect-unusual-spending")
def detect_unusual_spending(
    anomaly_check: AnomalyCheckInput,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Detect if a transaction is unusual"""
    detector = AnomalyDetector(db)
    return detector.detect_unusual_spending(
        current_user.id,
        anomaly_check.transaction_amount,
        anomaly_check.category
    )

@router.get("/anomaly/spending-spike")
def detect_spending_spike(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Detect if there's a spending spike this month"""
    detector = AnomalyDetector(db)
    return detector.detect_spending_spike(current_user.id)

@router.get("/anomaly/unusual-patterns")
def detect_unusual_patterns(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Detect unusual spending patterns"""
    detector = AnomalyDetector(db)
    return detector.detect_unusual_pattern(current_user.id)

@router.post("/anomaly/detect-duplicate")
def detect_duplicate_transaction(
    anomaly_check: AnomalyCheckInput,
    description: str = "",
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Detect potential duplicate transactions"""
    detector = AnomalyDetector(db)
    return detector.detect_duplicate_transactions(
        current_user.id,
        anomaly_check.transaction_amount,
        anomaly_check.category,
        description
    )
