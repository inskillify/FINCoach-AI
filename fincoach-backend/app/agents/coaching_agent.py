"""Coaching Agent - Provides personalized financial coaching"""
from typing import Dict, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.transaction import Transaction
from app.models.goal import Goal
from app.models.jar import Jar

class CoachingAgent:
    """AI Agent for personalized financial coaching"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_daily_coaching_tip(self, user_id: int) -> Dict:
        """Get personalized daily coaching tip"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"status": "error", "message": "User not found"}
        
        # Analyze user's financial situation
        tips = []
        
        # Check budget adherence
        one_month_ago = datetime.utcnow() - timedelta(days=30)
        monthly_expenses = sum(t.amount for t in self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.transaction_date >= one_month_ago
        ).all())
        
        if user.monthly_budget > 0:
            budget_usage = (monthly_expenses / user.monthly_budget) * 100
            if budget_usage > 80:
                tips.append({
                    "category": "Budget",
                    "tip": "You're approaching your monthly budget limit. Be mindful of remaining spending.",
                    "priority": "high"
                })
            elif budget_usage < 50:
                tips.append({
                    "category": "Savings",
                    "tip": "Great job! You're well under budget. Consider increasing your savings goals.",
                    "priority": "medium"
                })
        
        # Check for active goals
        active_goals = self.db.query(Goal).filter(
            Goal.user_id == user_id,
            Goal.status == "active"
        ).all()
        
        if not active_goals:
            tips.append({
                "category": "Goals",
                "tip": "You don't have any active financial goals. Setting goals helps you stay motivated!",
                "priority": "medium"
            })
        
        # Check savings jars
        jars = self.db.query(Jar).filter(
            Jar.user_id == user_id,
            Jar.is_active == 1
        ).all()
        
        if not jars:
            tips.append({
                "category": "Savings",
                "tip": "Create savings jars to organize your money for different purposes.",
                "priority": "medium"
            })
        
        # Default tip if no specific issues
        if not tips:
            tips.append({
                "category": "General",
                "tip": "You're doing great! Keep tracking your expenses and working towards your goals.",
                "priority": "low"
            })
        
        return {
            "status": "success",
            "tips": tips,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_weekly_summary(self, user_id: int) -> Dict:
        """Get weekly financial summary and coaching"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"status": "error", "message": "User not found"}
        
        # Get last 7 days data
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        weekly_income = sum(t.amount for t in self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.type == "income",
            Transaction.transaction_date >= seven_days_ago
        ).all())
        
        weekly_expenses = sum(t.amount for t in self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.transaction_date >= seven_days_ago
        ).all())
        
        weekly_savings = weekly_income - weekly_expenses
        
        # Get top spending categories
        weekly_transactions = self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.transaction_date >= seven_days_ago
        ).all()
        
        category_spending = {}
        for transaction in weekly_transactions:
            category = transaction.category
            if category not in category_spending:
                category_spending[category] = 0
            category_spending[category] += transaction.amount
        
        top_categories = sorted(category_spending.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Generate insights
        insights = []
        
        if weekly_savings > 0:
            insights.append(f"Great week! You saved ${weekly_savings:.2f}")
        elif weekly_savings < 0:
            insights.append(f"You spent ${abs(weekly_savings):.2f} more than you earned this week")
        
        if top_categories:
            top_category = top_categories[0][0]
            insights.append(f"Your highest spending category this week was {top_category}")
        
        return {
            "status": "success",
            "week_ending": datetime.utcnow().strftime("%Y-%m-%d"),
            "weekly_income": round(weekly_income, 2),
            "weekly_expenses": round(weekly_expenses, 2),
            "weekly_savings": round(weekly_savings, 2),
            "top_spending_categories": [{"category": cat, "amount": round(amt, 2)} for cat, amt in top_categories],
            "insights": insights
        }
    
    def get_personalized_action_plan(self, user_id: int) -> Dict:
        """Get personalized action plan for financial improvement"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"status": "error", "message": "User not found"}
        
        action_plan = {
            "immediate_actions": [],
            "short_term_actions": [],
            "long_term_actions": []
        }
        
        # Analyze current situation
        monthly_income = user.monthly_income
        monthly_budget = user.monthly_budget
        
        one_month_ago = datetime.utcnow() - timedelta(days=30)
        monthly_expenses = sum(t.amount for t in self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.transaction_date >= one_month_ago
        ).all())
        
        # Immediate actions
        if monthly_expenses > monthly_income:
            action_plan["immediate_actions"].append({
                "action": "Reduce monthly expenses",
                "reason": "You're spending more than you earn",
                "target": f"Reduce expenses by ${monthly_expenses - monthly_income:.2f}"
            })
        
        if not user.monthly_budget:
            action_plan["immediate_actions"].append({
                "action": "Set a monthly budget",
                "reason": "Budget helps track and control spending",
                "target": f"Set budget to ${monthly_income * 0.8:.2f}"
            })
        
        # Short-term actions (1-3 months)
        active_goals = self.db.query(Goal).filter(
            Goal.user_id == user_id,
            Goal.status == "active"
        ).all()
        
        if len(active_goals) < 2:
            action_plan["short_term_actions"].append({
                "action": "Create financial goals",
                "reason": "Goals provide direction and motivation",
                "target": "Create at least 2 financial goals"
            })
        
        jars = self.db.query(Jar).filter(
            Jar.user_id == user_id,
            Jar.is_active == 1
        ).all()
        
        if len(jars) < 3:
            action_plan["short_term_actions"].append({
                "action": "Create savings jars",
                "reason": "Jars help organize savings for different purposes",
                "target": "Create 3-5 savings jars"
            })
        
        # Long-term actions (3-12 months)
        action_plan["long_term_actions"].append({
            "action": "Build emergency fund",
            "reason": "Emergency fund provides financial security",
            "target": "Save 6 months of expenses"
        })
        
        action_plan["long_term_actions"].append({
            "action": "Increase income",
            "reason": "Higher income accelerates financial goals",
            "target": "Increase monthly income by 10-20%"
        })
        
        return {
            "status": "success",
            "action_plan": action_plan,
            "total_actions": len(action_plan["immediate_actions"]) + len(action_plan["short_term_actions"]) + len(action_plan["long_term_actions"])
        }
    
    def get_motivation_message(self, user_id: int) -> Dict:
        """Get motivational message based on progress"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"status": "error", "message": "User not found"}
        
        # Calculate progress metrics
        goals = self.db.query(Goal).filter(Goal.user_id == user_id).all()
        completed_goals = len([g for g in goals if g.status == "completed"])
        total_goals = len(goals)
        
        jars = self.db.query(Jar).filter(Jar.user_id == user_id).all()
        total_saved = sum(j.current_amount for j in jars)
        
        # Generate message
        messages = []
        
        if completed_goals > 0:
            messages.append(f"🎉 Congratulations! You've completed {completed_goals} financial goal(s)!")
        
        if total_saved > 0:
            messages.append(f"💰 You've saved ${total_saved:.2f} towards your goals!")
        
        if user.monthly_budget > 0:
            messages.append("📊 You're actively tracking your budget - great discipline!")
        
        if not messages:
            messages.append("🚀 Start your financial journey today! Set a goal and begin tracking your progress.")
        
        return {
            "status": "success",
            "message": " ".join(messages),
            "motivation_level": "high" if completed_goals > 0 else "medium" if total_saved > 0 else "low"
        }
