# MindCare AI - Quick Start Guide

Get MindCare AI running in under 5 minutes!

## Prerequisites

- Docker & Docker Compose installed
- Anthropic API key OR OpenAI API key

## Step 1: Get Your API Key

### Option A: Anthropic Claude (Recommended)
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys
4. Create a new API key
5. Copy the key

### Option B: OpenAI
1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to API Keys
4. Create a new API key
5. Copy the key

## Step 2: Configure Environment

```bash
cd mindcare-ai/backend
cp .env.example .env
```

Edit the `.env` file and add your API key:

```bash
# For Anthropic Claude
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_api_key_here

# OR for OpenAI
AI_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here
```

## Step 3: Start the Application

From the root directory:

```bash
docker-compose up --build
```

This will:
- Start PostgreSQL database
- Initialize the database schema
- Start the FastAPI backend on port 8000
- Start the React frontend on port 3000

## Step 4: Access the Application

Open your browser and visit:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Step 5: Try It Out!

### Patient Intake
1. Go to http://localhost:3000
2. Click "Get Started" on the Patient Intake page
3. Chat with the AI assistant
4. Complete the questionnaire
5. Submit the intake

### Admin Dashboard
1. Navigate to "Admin Dashboard" from the menu
2. View metrics, high-risk patients, and alerts
3. See therapist caseloads and utilization

### Therapist Portal
1. Navigate to "Therapist Portal"
2. Select a therapist from the dropdown
3. View caseload details and capacity

## Troubleshooting

### Database Connection Issues
```bash
# Check if database is running
docker ps

# View database logs
docker logs mindcare_db

# Restart services
docker-compose restart
```

### API Key Not Working
- Verify your API key is correct in `.env`
- Check that you've set the right `AI_PROVIDER` (anthropic or openai)
- Ensure you have API credits available

### Frontend Not Loading
```bash
# Check frontend logs
docker logs mindcare_frontend

# Rebuild frontend
docker-compose up --build frontend
```

### Port Already in Use
If ports 3000, 5432, or 8000 are already in use:

Edit `docker-compose.yml` and change the port mappings:
```yaml
ports:
  - "3001:3000"  # Frontend (change 3001 to any available port)
  - "8001:8000"  # Backend (change 8001 to any available port)
  - "5433:5432"  # Database (change 5433 to any available port)
```

## Default Data

The database is initialized with 5 sample therapists:
- Sarah Johnson - Trauma, Anxiety
- Michael Chen - Depression, Anxiety
- Emily Rodriguez - Couples, Family
- David Thompson - Addiction, Trauma
- Jessica Kim - Child, Anxiety

## Next Steps

1. **Add More Therapists**: Use the admin API endpoints
2. **Customize Risk Scoring**: Edit `backend/app/services/risk_scorer.py`
3. **Train Dropout Model**: Use real data to train the ML model
4. **Enable Production Features**: Configure AWS services (RDS, S3)

## Development Mode

To run without Docker for development:

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Database
```bash
# Using local PostgreSQL
createdb mindcare_db
psql mindcare_db < database/schema.sql
```

## Support

For issues:
- Check the logs: `docker-compose logs`
- See full README.md for detailed documentation
- Report bugs via GitHub Issues

---

**Happy triaging! 🧠💙**
