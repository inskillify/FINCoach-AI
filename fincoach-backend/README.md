# FINCoach AI Backend

AI-powered personal finance management system with intelligent financial coaching.

## 🎯 Project Status

**Status**: 70% Complete  
**Version**: 1.0.0  
**Last Updated**: November 24, 2025

## ✨ Features

### Core Features (Completed)
- ✅ User Authentication & Authorization
- ✅ Transaction Management (Income/Expense tracking)
- ✅ Savings Jar System (Goal-based savings)
- ✅ Financial Goals Management
- ✅ Alert System (Real-time notifications)
- ✅ UPI SMS Parsing (Indian banks)
- ✅ Budget Tracking

### Upcoming Features (30% Remaining)
- 🔄 Multi-Agent AI System
- 🔄 Machine Learning Modules
- 🔄 Advanced Analytics
- 🔄 Predictive Insights

## 🏗️ Architecture

### Technology Stack
- **Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL with SQLAlchemy 2.0.23
- **Authentication**: JWT with python-jose
- **Validation**: Pydantic 2.5.0
- **Migrations**: Alembic 1.12.1

### Database Schema
```
Users (1) ──┬─→ (Many) Transactions
            ├─→ (Many) Jars
            ├─→ (Many) Goals
            └─→ (Many) Alerts
```

## 📦 Installation

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- pip or poetry

### Setup Steps

1. **Clone the repository**
```bash
git clone https://github.com/inskillify/FINCoach-AI.git
cd FINCoach-AI/fincoach-backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Create database**
```bash
createdb -h localhost fincoach_db
```

6. **Run migrations**
```bash
alembic upgrade head
```

7. **Start the server**
```bash
python -m uvicorn app.main:app --reload
```

## 🚀 API Documentation

### Access Points
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### API Endpoints

#### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/refresh` - Refresh access token

#### Users
- `GET /api/v1/users/me` - Get current user profile
- `GET /api/v1/users/{user_id}` - Get user by ID
- `PUT /api/v1/users/me` - Update user profile
- `DELETE /api/v1/users/me` - Delete user account

#### Transactions
- `POST /api/v1/transactions` - Create transaction
- `GET /api/v1/transactions` - List transactions
- `GET /api/v1/transactions/{id}` - Get transaction
- `PUT /api/v1/transactions/{id}` - Update transaction
- `DELETE /api/v1/transactions/{id}` - Delete transaction
- `GET /api/v1/transactions/stats/summary` - Get summary

#### Jars
- `POST /api/v1/jars` - Create jar
- `GET /api/v1/jars` - List jars
- `GET /api/v1/jars/{id}` - Get jar
- `PUT /api/v1/jars/{id}` - Update jar
- `DELETE /api/v1/jars/{id}` - Delete jar
- `POST /api/v1/jars/{id}/add-funds` - Add funds
- `GET /api/v1/jars/{id}/progress` - Get progress

#### Goals
- `POST /api/v1/goals` - Create goal
- `GET /api/v1/goals` - List goals
- `GET /api/v1/goals/{id}` - Get goal
- `PUT /api/v1/goals/{id}` - Update goal
- `DELETE /api/v1/goals/{id}` - Delete goal
- `POST /api/v1/goals/{id}/add-progress` - Add progress
- `GET /api/v1/goals/{id}/progress` - Get progress

#### Alerts
- `POST /api/v1/alerts` - Create alert
- `GET /api/v1/alerts` - List alerts
- `GET /api/v1/alerts/{id}` - Get alert
- `PUT /api/v1/alerts/{id}/mark-as-read` - Mark as read
- `DELETE /api/v1/alerts/{id}` - Delete alert
- `GET /api/v1/alerts/stats/summary` - Get summary

## 📊 Database Models

### User
```python
- id: Integer (Primary Key)
- email: String (Unique)
- username: String (Unique)
- full_name: String
- hashed_password: String
- phone: String
- monthly_income: Float
- monthly_budget: Float
- is_active: Boolean
- is_verified: Boolean
- created_at: DateTime
- updated_at: DateTime
```

### Transaction
```python
- id: Integer (Primary Key)
- user_id: Integer (Foreign Key)
- amount: Float
- type: Enum (income, expense)
- category: Enum (11 categories)
- description: String
- transaction_date: DateTime
- created_at: DateTime
- updated_at: DateTime
```

### Jar
```python
- id: Integer (Primary Key)
- user_id: Integer (Foreign Key)
- name: String
- description: String
- target_amount: Float
- current_amount: Float
- priority: Enum (low, medium, high)
- color: String
- is_active: Integer
- created_at: DateTime
- updated_at: DateTime
```

### Goal
```python
- id: Integer (Primary Key)
- user_id: Integer (Foreign Key)
- title: String
- description: String
- target_amount: Float
- current_amount: Float
- deadline: DateTime
- status: Enum (active, completed, abandoned)
- category: String
- created_at: DateTime
- updated_at: DateTime
```

### Alert
```python
- id: Integer (Primary Key)
- user_id: Integer (Foreign Key)
- title: String
- message: String
- severity: Enum (info, warning, critical, error)
- is_read: Boolean
- created_at: DateTime
- updated_at: DateTime
```

## 🔐 Security

- JWT-based authentication
- bcrypt password hashing
- CORS protection
- SQL injection prevention
- Environment variable management
- HTTPS ready

## 📝 Example Requests

### Register User
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "john_doe",
    "password": "secure_password",
    "full_name": "John Doe",
    "monthly_income": 50000,
    "monthly_budget": 40000
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure_password"
  }'
```

### Create Transaction
```bash
curl -X POST "http://localhost:8000/api/v1/transactions" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 500,
    "type": "expense",
    "category": "food",
    "description": "Lunch",
    "transaction_date": "2025-11-24T12:00:00"
  }'
```

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test
pytest tests/test_auth.py
```

## 📚 Documentation Files

- `README.md` - This file
- `PROJECT_SUMMARY.md` - Detailed project overview
- `COMPLETION_REPORT.md` - Project completion status
- `DEPLOYMENT_GUIDE.md` - Deployment instructions
- `EXECUTIVE_SUMMARY.txt` - Quick overview
- `INDEX.md` - File structure and navigation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👥 Authors

- **Suchita Nigam** - Initial development
- **FINCoach Team** - Ongoing development

## 📞 Support

For support, email support@fincoach.ai or open an issue on GitHub.

## 🗺️ Roadmap

### Phase 1 (Current - 70%)
- ✅ Core API infrastructure
- ✅ Authentication system
- ✅ Transaction management
- ✅ Savings jars
- ✅ Goals tracking
- ✅ Alert system

### Phase 2 (30% Remaining)
- 🔄 Multi-Agent AI System
- 🔄 ML prediction models
- 🔄 Advanced analytics
- 🔄 Mobile app integration

### Phase 3 (Future)
- 📅 Real-time notifications
- 📅 Social features
- 📅 Investment tracking
- 📅 Tax optimization

---

**Last Updated**: November 24, 2025  
**Version**: 1.0.0  
**Status**: Production Ready (70% Complete)
