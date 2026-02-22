# MindCare AI - Enhanced Edition

## 🎉 New Features & Enhancements

This enhanced version includes **6 core production features** that make MindCare AI enterprise-ready:

### ✅ 1. User Authentication System

**What's Included:**
- Complete JWT-based authentication
- Secure password hashing (bcrypt)
- Refresh token rotation
- Role-based access control (RBAC)
- Session management
- Account lockout after failed attempts
- Password strength validation

**Database Tables:**
- `users` - User accounts with roles
- `refresh_tokens` - Session management
- `auth_audit_log` - Security logging

**API Endpoints:**
```
POST /api/auth/register      - Register new user
POST /api/auth/login         - Login with email/password
POST /api/auth/logout        - Logout and revoke tokens
POST /api/auth/refresh       - Refresh access token
GET  /api/auth/me            - Get current user
POST /api/auth/change-password - Change password
```

**User Roles:**
- **Admin** - Full system access
- **Therapist** - Patient management, caseload view
- **Staff** - Limited administrative access
- **Patient** - Personal data access only

**Frontend Components:**
- `LoginPage.jsx` - Comprehensive login with validation
- `AuthContext.jsx` - Global auth state management
- `ProtectedRoute` - Route-level access control

---

### ✅ 2. Comprehensive Input Validation

**Backend Validation (Pydantic):**
- Email format validation
- Phone number normalization
- Date validation (age checks)
- US state code validation
- Text length constraints
- PHQ-9 / GAD-7 score validation (0-3 range)
- UUID format validation
- XSS prevention

**Frontend Validation:**
- Real-time field validation
- Password strength meter
- Email format checking
- Required field enforcement
- Character count limits
- Error message display

**Validation Schemas:**
```python
PatientInfoSchema       - Demographics
PHQ9ResponseSchema      - Depression screening
GAD7ResponseSchema      - Anxiety screening
TextResponsesSchema     - Free-text inputs
IntakeSubmissionSchema  - Complete intake
ChatMessageSchema       - Chatbot messages
```

**Error Handling:**
- Field-level error messages
- Form-level validation
- Server-side validation
- Client-side pre-validation
- Helpful error messages
- Validation error aggregation

---

### ✅ 3. Error Handling & Loading States

**Backend Error Handling:**
```python
try:
    # Operation
except HTTPException:
    raise  # Re-raise HTTP errors
except Exception as e:
    raise HTTPException(
        status_code=500,
        detail=f"Operation failed: {str(e)}"
    )
```

**Frontend Error Handling:**
- Global error boundary
- API error interceptors
- Automatic token refresh on 401
- Network error detection
- Retry logic with exponential backoff
- User-friendly error messages

**Loading States:**
- Global loading indicator
- Button loading states
- Skeleton screens
- Progress indicators
- Disabled states during operations
- Loading state subscription system

**Error Display:**
- Toast notifications
- Inline field errors
- Alert banners
- Modal dialogs for critical errors
- Error recovery suggestions

---

### ✅ 4. Mobile Responsive Design

**Responsive Breakpoints:**
```css
sm: 640px   /* Mobile landscape */
md: 768px   /* Tablets */
lg: 1024px  /* Desktop */
xl: 1280px  /* Large desktop */
2xl: 1536px /* Extra large */
```

**Mobile Features:**
- Touch-optimized buttons (min 44px)
- Collapsible navigation
- Stacked layouts on mobile
- Swipe gestures
- Mobile-optimized forms
- Readable typography (16px minimum)
- Proper viewport meta tags

**Tailwind Responsive Classes:**
```jsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4">
  {/* 1 col mobile, 2 col tablet, 4 col desktop */}
</div>
```

**Mobile Optimizations:**
- Reduced padding on small screens
- Hidden decorative elements
- Simplified navigation
- Full-width inputs on mobile
- Bottom-sheet modals
- Fixed position elements

---

### ✅ 5. Enhanced AI Integration

**Already Implemented:**
- Anthropic Claude integration
- OpenAI GPT integration
- Configurable AI provider
- Sentiment analysis
- Crisis keyword detection
- Chatbot conversations
- Risk assessment AI
- Therapist match reasoning

**Error Handling:**
```javascript
try {
  const response = await ai_service.analyze_intake_text(text);
  return response;
} catch (error) {
  // Fallback to rule-based analysis
  return fallbackAnalysis(text);
}
```

**Rate Limiting:**
- Request throttling
- Queue management
- Retry logic
- Timeout handling

**API Configuration:**
```env
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_key
LLM_MODEL=claude-sonnet-4-20250514
LLM_MAX_TOKENS=2000
LLM_TEMPERATURE=0.3
```

---

### ✅ 6. Database & Data Models

**Complete Schema:**
- ✅ 13 tables (10 original + 3 auth tables)
- ✅ ENUM types for type safety
- ✅ Foreign key constraints
- ✅ Indexes for performance
- ✅ Triggers for timestamps
- ✅ Views for common queries
- ✅ Sample data included

**New Tables:**
```sql
users               - User authentication
refresh_tokens      - Session management
auth_audit_log      - Security logging
```

**Enhanced Tables:**
```sql
patients     - Linked to users
therapists   - Linked to users
```

**Data Integrity:**
- NOT NULL constraints
- CHECK constraints for valid ranges
- UNIQUE constraints
- CASCADE deletes
- Transaction support

---

## 🛠 Technical Enhancements

### Security Improvements

**Authentication:**
- JWT tokens with expiration
- Refresh token rotation
- Account lockout (5 failed attempts)
- Password requirements (8+ chars, uppercase, digit)
- Secure password hashing (bcrypt)
- CSRF protection ready

**Data Protection:**
- Input sanitization
- SQL injection prevention (ORM)
- XSS protection
- Rate limiting ready
- Audit logging

**HIPAA Compliance:**
- Encryption at rest (PostgreSQL)
- Encryption in transit (HTTPS)
- Access control (RBAC)
- Audit trails
- Data retention policies ready

---

### Performance Optimizations

**Backend:**
- Database connection pooling
- Query optimization with indexes
- Async/await for I/O operations
- Request caching ready
- Lazy loading

**Frontend:**
- Code splitting ready
- Image optimization
- Debounced API calls
- Memoized components
- Virtual scrolling for large lists

**Database:**
- Indexed columns
- Materialized views ready
- Query performance monitoring
- Connection pooling (SQLAlchemy)

---

## 📱 Mobile Responsive Examples

### Dashboard (Mobile vs Desktop)

**Mobile (< 768px):**
```
┌─────────────────────┐
│  ☰ MindCare AI      │
├─────────────────────┤
│  Active Patients    │
│        124          │
├─────────────────────┤
│  Intake Queue       │
│         18          │
├─────────────────────┤
│  High Risk          │
│          7          │
└─────────────────────┘
```

**Desktop (> 1024px):**
```
┌─────────────────────────────────────────┐
│  MindCare AI    🏠 Admin 👤 Therapist   │
├─────────┬─────────┬─────────┬──────────┤
│ Active  │ Intake  │ High    │ Alerts   │
│  124    │   18    │ Risk 7  │   3      │
├─────────┴─────────┴─────────┴──────────┤
│          Dashboard Content              │
│          [Charts & Tables]              │
└─────────────────────────────────────────┘
```

---

## 🚀 Setup Instructions

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)
- PostgreSQL 14+ (for local development)

### Quick Start

```bash
# 1. Clone/extract the project
cd mindcare-ai-enhanced

# 2. Configure environment
cd backend
cp .env.example .env
# Edit .env and add your API keys

# 3. Start with Docker
cd ..
docker-compose up --build

# 4. Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs

# 5. Login with demo account
# Email: admin@mindcare.com
# Password: admin123
```

### Manual Setup (Development)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run migrations
python scripts/run_migrations.py

# Start server
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Database:**
```bash
# Create database
createdb mindcare_enhanced_db

# Run schema
psql mindcare_enhanced_db < database/schema.sql

# Run migrations
psql mindcare_enhanced_db < database/migrations/001_add_authentication.sql
```

---

## 🔐 Default Accounts

For testing purposes, the following accounts are created:

| Email | Password | Role | Access |
|-------|----------|------|--------|
| admin@mindcare.com | admin123 | Admin | Full system access |
| therapist@mindcare.com | admin123 | Therapist | Patient management |
| staff@mindcare.com | admin123 | Staff | Limited access |

**⚠️ Change these passwords in production!**

---

## 📝 API Examples

### Authentication

**Register:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123",
    "first_name": "John",
    "last_name": "Doe",
    "role": "staff"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@mindcare.com&password=admin123"
```

**Protected Endpoint:**
```bash
curl -X GET http://localhost:8000/api/admin/dashboard \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🧪 Testing

### Unit Tests (Backend)
```bash
cd backend
pytest tests/ -v
```

### Integration Tests
```bash
pytest tests/integration/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

---

## 📊 Monitoring & Logging

**Backend Logging:**
```python
import logging
logger = logging.getLogger(__name__)
logger.info("User logged in", extra={"user_id": user.id})
```

**Audit Log:**
```sql
SELECT * FROM auth_audit_log 
WHERE user_id = 'xxx' 
ORDER BY created_at DESC;
```

**Error Tracking:**
- Console logs (development)
- File logs (production)
- Sentry integration ready
- CloudWatch integration ready

---

## 🔄 Migration from Original Version

If you have the original MindCare AI running:

```bash
# 1. Backup existing database
pg_dump mindcare_db > backup.sql

# 2. Apply new migrations
psql mindcare_db < database/migrations/001_add_authentication.sql

# 3. Create default users
# Run the INSERT statements from migration file

# 4. Update application code
# Replace old files with enhanced versions

# 5. Restart application
docker-compose restart
```

---

## 🎯 Feature Comparison

| Feature | Original | Enhanced |
|---------|----------|----------|
| Authentication | ❌ | ✅ JWT + Refresh |
| Input Validation | Basic | ✅ Comprehensive |
| Error Handling | Basic | ✅ Advanced |
| Mobile Responsive | Partial | ✅ Full |
| Loading States | None | ✅ Global + Local |
| Role-Based Access | ❌ | ✅ 4 roles |
| Security Audit | ❌ | ✅ Full logging |
| Password Policies | ❌ | ✅ Enforced |
| Session Management | ❌ | ✅ Refresh tokens |
| API Rate Limiting | ❌ | ✅ Ready |

---

## 📚 Additional Documentation

- `API_DOCUMENTATION.md` - Complete API reference
- `SECURITY.md` - Security best practices
- `DEPLOYMENT_ENHANCED.md` - Production deployment
- `MOBILE_GUIDELINES.md` - Mobile design patterns

---

## 🤝 Contributing

See `CONTRIBUTING.md` for guidelines on:
- Code style
- Testing requirements
- Pull request process
- Security reporting

---

## 📄 License

MIT License - see `LICENSE` file

---

## 🆘 Support

- **Documentation**: Check the `/docs` folder
- **Issues**: GitHub Issues
- **Security**: security@mindcareai.com
- **General**: support@mindcareai.com

---

**Built with ❤️ for production-ready mental healthcare**
