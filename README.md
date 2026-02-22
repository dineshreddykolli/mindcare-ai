# MindCare AI - Intelligent Mental Health Triage Platform 

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18-blue.svg)](https://reactjs.org/)

## Overview

MindCare AI is an AI-powered patient triage and therapist-matching platform designed for mental health clinics. It reduces wait times, improves resource allocation, and identifies high-risk patients requiring urgent intervention.

### Key Features

- **AI Intake Chatbot** - Automated patient intake with natural language processing
- **Risk Scoring Engine** - Real-time assessment of patient risk levels
- **Smart Therapist Matching** - AI-powered patient-therapist pairing based on specialty, availability, and outcomes
- **Dropout Prediction** - Early identification of patients at risk of disengagement
- **Crisis Detection** - Automated flagging of concerning keywords and phrases
- **Administrative Dashboard** - Real-time visibility into patient risk, caseloads, and metrics

## Architecture

```
┌─────────────────┐
│  React Frontend │
│  (Port 3000)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│  FastAPI Backend│◄────►│ PostgreSQL DB│
│  (Port 8000)    │      │  (Port 5432) │
└────────┬────────┘      └──────────────┘
         │
         ▼
┌─────────────────┐
│   AI Services   │
│ - OpenAI/Claude │
│ - ML Models     │
└─────────────────┘
```

## Technology Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Primary database
- **Scikit-learn** - Machine learning models
- **Anthropic Claude / OpenAI** - LLM integration for NLP tasks

### Frontend
- **React 18** - UI framework
- **Tailwind CSS** - Utility-first styling
- **Recharts** - Data visualization
- **Axios** - HTTP client

### Infrastructure
- **Docker** - Containerization
- **AWS App Runner** - Deployment (production)
- **Amazon RDS** - Managed PostgreSQL (production)
- **Amazon S3** - Document storage (production)

## Prerequisites

- Docker & Docker Compose
- Node.js 18+ and npm
- Python 3.11+
- API key for Anthropic Claude or OpenAI

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd mindcare-ai
```

### 2. Environment Setup

Create `.env` file in the backend directory:

```bash
# Database
DATABASE_URL=postgresql://mindcare:mindcare123@db:5432/mindcare_db

# API Keys
ANTHROPIC_API_KEY=your_anthropic_key_here
# OR
OPENAI_API_KEY=your_openai_key_here

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=development
```

### 3. Start with Docker Compose

```bash
docker-compose up --build
```

This will start:
- PostgreSQL database (port 5432)
- FastAPI backend (port 8000)
- React frontend (port 3000)

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Manual Setup (Development)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run migrations
python -m alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

### Database Setup

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE mindcare_db;

# Run schema
psql -U postgres -d mindcare_db -f database/schema.sql
```

## Project Structure

```
mindcare-ai/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── config.py            # Configuration management
│   │   ├── database.py          # Database connection
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── patient.py
│   │   │   ├── therapist.py
│   │   │   └── session.py
│   │   ├── schemas/             # Pydantic schemas
│   │   │   ├── patient.py
│   │   │   └── therapist.py
│   │   ├── routers/             # API endpoints
│   │   │   ├── intake.py
│   │   │   ├── risk.py
│   │   │   ├── matching.py
│   │   │   └── admin.py
│   │   ├── services/            # Business logic
│   │   │   ├── ai_service.py
│   │   │   └── matching_service.py
│   │   └── ml/                  # ML models
│   │       ├── risk_scorer.py
│   │       └── dropout_predictor.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   │   ├── IntakeChatbot.jsx
│   │   │   ├── RiskDashboard.jsx
│   │   │   └── TherapistPanel.jsx
│   │   ├── pages/               # Page components
│   │   │   ├── PatientIntake.jsx
│   │   │   ├── AdminDashboard.jsx
│   │   │   └── TherapistDashboard.jsx
│   │   ├── services/            # API client
│   │   │   └── api.js
│   │   └── App.jsx
│   ├── package.json
│   └── tailwind.config.js
├── database/
│   └── schema.sql               # Database schema
├── docker-compose.yml
└── README.md
```

## API Endpoints

### Intake & Analysis
- `POST /api/intake/submit` - Submit patient intake form
- `POST /api/intake/chat` - Chatbot interaction
- `POST /api/intake/analyze` - Analyze intake responses

### Risk Assessment
- `GET /api/risk/score/{patient_id}` - Get patient risk score
- `GET /api/risk/high-risk` - List all high-risk patients
- `POST /api/risk/update/{patient_id}` - Update risk assessment

### Therapist Matching
- `POST /api/matching/recommend` - Get therapist recommendations
- `GET /api/matching/availability` - Check therapist availability

### Admin & Analytics
- `GET /api/admin/dashboard` - Dashboard metrics
- `GET /api/admin/therapists` - Therapist caseload statistics
- `POST /api/admin/assign` - Manual patient assignment

## AI/ML Features

### Risk Scoring Algorithm

The risk scoring model uses multiple factors:
- **PHQ-9 Depression Score** (0-27 scale)
- **GAD-7 Anxiety Score** (0-21 scale)
- **Sentiment Analysis** of free-text responses
- **Crisis Keywords** detection (self-harm, suicidal ideation)
- **Historical Session Data** (if available)

Risk levels:
- **Critical** (80-100): Immediate intervention required
- **High** (60-79): Priority scheduling within 48 hours
- **Moderate** (40-59): Standard scheduling
- **Low** (0-39): Regular intake process

### Dropout Prediction

Machine learning model trained on:
- Session attendance patterns
- Response time to appointment requests
- Sentiment trends across sessions
- Demographic factors
- Distance from clinic
- Insurance type

### Therapist Matching

Matching algorithm considers:
- **Specialization** (trauma, anxiety, depression, etc.)
- **Language preference**
- **Availability** and current caseload
- **Past success rates** with similar cases
- **Risk level compatibility**

## Success Metrics

Target improvements:
- ✅ 25% reduction in high-risk patient wait time
- ✅ 15% reduction in patient dropout rate
- ✅ 20% faster intake processing time
- ✅ Improved therapist utilization balance

## Security & Compliance

### HIPAA Compliance Considerations
- All patient data encrypted at rest and in transit
- Access logging for all sensitive operations
- Role-based access control (RBAC)
- Regular security audits
- BAA (Business Associate Agreement) required for cloud providers

### Data Protection
- PostgreSQL with encryption
- S3 with server-side encryption for documents
- API authentication via JWT tokens
- HTTPS/TLS for all communications

⚠️ **Note**: This MVP requires additional hardening for production HIPAA compliance, including:
- Comprehensive audit logging
- PHI de-identification for ML training
- Enhanced access controls
- Regular penetration testing
- Disaster recovery procedures

## Testing

```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend
npm test
```

## Deployment

### AWS Deployment

1. **Database**: Amazon RDS PostgreSQL
2. **Backend**: AWS App Runner with Docker
3. **Frontend**: AWS Amplify or S3 + CloudFront
4. **Storage**: Amazon S3 for intake transcripts

See `deployment/` directory for detailed instructions.

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

For issues and questions:
- 📧 Email: support@mindcareai.com
- 📝 Issues: GitHub Issues
- 📚 Documentation: [docs.mindcareai.com](https://docs.mindcareai.com)

## Acknowledgments

- Mental health professionals who provided domain expertise
- Open source community for excellent tooling
- Research on AI in healthcare triage systems

---

**Built with ❤️ for better mental healthcare access**
