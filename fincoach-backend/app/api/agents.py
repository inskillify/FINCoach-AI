"""API routes for AI Agents"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.agents.financial_advisor import FinancialAdvisor
from app.agents.risk_assessor import RiskAssessor
from app.agents.prediction_agent import PredictionAgent
from app.agents.coaching_agent import CoachingAgent
from app.security import get_current_user

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])

@router.get("/financial-advisor/spending-analysis")
def get_spending_analysis(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get spending pattern analysis"""
    advisor = FinancialAdvisor(db)
    return advisor.analyze_spending_patterns(current_user.id)

@router.get("/financial-advisor/budget-recommendations")
def get_budget_recommendations(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get personalized budget recommendations"""
    advisor = FinancialAdvisor(db)
    return advisor.get_budget_recommendations(current_user.id)

@router.get("/financial-advisor/savings-allocation")
def get_savings_allocation(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get optimal savings allocation (50-30-20 rule)"""
    advisor = FinancialAdvisor(db)
    return advisor.suggest_savings_allocation(current_user.id)

@router.get("/financial-advisor/health-score")
def get_financial_health_score(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get financial health score (0-100)"""
    advisor = FinancialAdvisor(db)
    return advisor.get_financial_health_score(current_user.id)

@router.get("/risk-assessor/emergency-fund")
def assess_emergency_fund(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Assess emergency fund adequacy"""
    assessor = RiskAssessor(db)
    return assessor.assess_emergency_fund(current_user.id)

@router.get("/risk-assessor/debt-risk")
def assess_debt_risk(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Assess debt and financial obligations risk"""
    assessor = RiskAssessor(db)
    return assessor.assess_debt_risk(current_user.id)

@router.get("/risk-assessor/goal-feasibility/{goal_id}")
def assess_goal_feasibility(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Assess if a financial goal is feasible"""
    assessor = RiskAssessor(db)
    return assessor.assess_goal_feasibility(current_user.id, goal_id)

@router.get("/risk-assessor/spending-volatility")
def assess_spending_volatility(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Assess spending volatility and consistency"""
    assessor = RiskAssessor(db)
    return assessor.assess_spending_volatility(current_user.id)

@router.get("/prediction/monthly-expenses")
def predict_monthly_expenses(
    months_ahead: int = 3,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Predict future monthly expenses"""
    predictor = PredictionAgent(db)
    return predictor.predict_monthly_expenses(current_user.id, months_ahead)

@router.get("/prediction/savings-potential")
def predict_savings_potential(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Predict potential monthly savings"""
    predictor = PredictionAgent(db)
    return predictor.predict_savings_potential(current_user.id)

@router.get("/prediction/goal-completion/{goal_id}")
def predict_goal_completion(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Predict when a goal will be completed"""
    predictor = PredictionAgent(db)
    return predictor.predict_goal_completion(current_user.id, goal_id)

@router.get("/prediction/spending-by-category")
def predict_spending_by_category(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Predict spending by category for next month"""
    predictor = PredictionAgent(db)
    return predictor.predict_spending_by_category(current_user.id)

@router.get("/coaching/daily-tip")
def get_daily_coaching_tip(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get personalized daily coaching tip"""
    coach = CoachingAgent(db)
    return coach.get_daily_coaching_tip(current_user.id)

@router.get("/coaching/weekly-summary")
def get_weekly_summary(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get weekly financial summary and coaching"""
    coach = CoachingAgent(db)
    return coach.get_weekly_summary(current_user.id)

@router.get("/coaching/action-plan")
def get_personalized_action_plan(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get personalized action plan for financial improvement"""
    coach = CoachingAgent(db)
    return coach.get_personalized_action_plan(current_user.id)

@router.get("/coaching/motivation")
def get_motivation_message(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get motivational message based on progress"""
    coach = CoachingAgent(db)
    return coach.get_motivation_message(current_user.id)
