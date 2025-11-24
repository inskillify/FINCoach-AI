"""Main FastAPI Application for FINCoach AI Backend"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.api import auth, users, transactions, jars, goals, alerts, agents, ml_modules
from app.core.config import settings
from app.core.database import engine, Base

# Create tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 FINCoach AI Backend Starting...")
    yield
    # Shutdown
    print("🛑 FINCoach AI Backend Shutting Down...")

app = FastAPI(
    title="FINCoach AI Backend",
    description="AI-powered personal finance management system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["Transactions"])
app.include_router(jars.router, prefix="/api/v1/jars", tags=["Jars"])
app.include_router(goals.router, prefix="/api/v1/goals", tags=["Goals"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])
app.include_router(agents.router, tags=["AI Agents"])
app.include_router(ml_modules.router, tags=["ML Modules"])

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "FINCoach AI Backend"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to FINCoach AI Backend",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "features": {
            "core": ["Authentication", "Users", "Transactions", "Jars", "Goals", "Alerts"],
            "ai_agents": ["Financial Advisor", "Risk Assessor", "Prediction Agent", "Coaching Agent"],
            "ml_modules": ["Prediction Engine", "Transaction Categorizer", "Anomaly Detector"]
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
