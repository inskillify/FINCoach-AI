"""API routes for FINCoach AI Backend"""
from . import auth
from . import users
from . import transactions
from . import jars
from . import goals
from . import alerts
from . import agents
from . import ml_modules
from . import analytics
from . import mobile
from . import notifications
from . import social

__all__ = [
    "auth",
    "users",
    "transactions",
    "jars",
    "goals",
    "alerts",
    "agents",
    "ml_modules",
    "analytics",
    "mobile",
    "notifications",
    "social"
]
