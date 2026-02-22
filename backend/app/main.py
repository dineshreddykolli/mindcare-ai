"""
MindCare AI - Main FastAPI Application
Mental health triage and therapist matching platform
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.config import settings
from app.database import engine, Base
from app.routers import intake, admin, matching, auth

# Create database tables
# In production, use Alembic migrations instead
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="AI-powered mental health triage and therapist matching platform",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.on_event("startup")
async def startup_event():
    """Create database tables on startup"""
    Base.metadata.create_all(bind=engine)
# Include routers
app.include_router(auth.router)
app.include_router(intake.router)
app.include_router(admin.router)
app.include_router(matching.router)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": "2026-02-14T12:00:00Z"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "An internal error occurred",
            "detail": str(exc) if settings.DEBUG else "Please contact support"
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
