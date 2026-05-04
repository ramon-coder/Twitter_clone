"""
Main Application File for Subscription and Recurring Payments Management System

This file serves as the entry point to the FastAPI application, setting up
the core configurations, database connection, authentication, and global
error handling middleware.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from dotenv import load_dotenv
from middleware.rate_limit import RateLimitMiddleware

# Load environment variables
load_dotenv()

# Global scheduler reference
_scheduler = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.getenv('LOG_FILE', 'app.log'))
    ]
)
logger = logging.getLogger(__name__)

# Application configuration
APP_TITLE = "Subscription and Recurring Payments Management System"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = """
API for managing subscriptions and recurring payments.
Supports user authentication, plan management, subscription lifecycle,
and payment processing with Stripe integration.
"""

# Environment configuration
APP_ENV = os.getenv("APP_ENV", "development")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Validate critical environment variables
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    logger.error("SECRET_KEY environment variable is not set!")
    if APP_ENV == "production":
        raise ValueError("SECRET_KEY must be set in production environment")
    SECRET_KEY = "dev-secret-key-change-in-production-minimum-32-chars"
elif len(SECRET_KEY) < 32 and APP_ENV == "production":
    logger.warning("SECRET_KEY is less than 32 characters - not recommended for production")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./subscriptions.db")
if 'postgresql' in DATABASE_URL and APP_ENV == "production":
    # Production PostgreSQL settings
    engine = create_engine(
        DATABASE_URL,
        pool_size=20,
        max_overflow=30,
        pool_pre_ping=True,
        pool_recycle=3600
    )
else:
    # Development/Test settings
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Import all models to register them with SQLAlchemy
from models import User, Plan, Subscription, Payment, Invoice  # noqa: F401

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Initialize FastAPI application
app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
if APP_ENV == "production":
    origins = [
        "https://yourdomain.com",
        "https://www.yourdomain.com",
    ]
else:
    origins = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-RateLimit-Remaining", "X-RateLimit-Window"]
)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Dependency to get the database session
def get_db():
    """Get database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency to get current user
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Query the database for the user
    from models import User
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Get current authenticated and active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint with detailed status"""
    from sqlalchemy import text

    # Check database connection
    db_status = "healthy"
    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db.close()
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    # Check Redis (optional)
    redis_status = "not_configured"
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0, socket_timeout=1)
        r.ping()
        redis_status = "healthy"
    except:
        pass

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.now().isoformat(),
        "version": APP_VERSION,
        "environment": APP_ENV,
        "checks": {
            "database": db_status,
            "redis": redis_status,
            "scheduler": "running" if (_scheduler and _scheduler.running) else "stopped"
        }
    }

# Global error handling
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP exception handler"""
    from fastapi.responses import JSONResponse
    logger.warning(f"HTTP {exc.status_code}: {exc.detail} - Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status_code": exc.status_code,
            "detail": exc.detail,
            "timestamp": datetime.now().isoformat(),
            "path": request.url.path
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    from fastapi.responses import JSONResponse
    logger.error(f"Unhandled exception: {str(exc)} - Path: {request.url.path}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "detail": "Internal server error",
            "timestamp": datetime.now().isoformat(),
            "path": request.url.path
        }
    )

# Include routers
from routers import auth, plans, users, subscriptions, payments, webhooks

app.include_router(auth.router, tags=["Authentication"])
app.include_router(plans.router, prefix="/plans", tags=["Plans"], dependencies=[Depends(get_current_user)])
app.include_router(users.router, prefix="/users", tags=["Users"], dependencies=[Depends(get_current_user)])
app.include_router(subscriptions.router, prefix="/subscriptions", tags=["Subscriptions"], dependencies=[Depends(get_current_user)])
app.include_router(payments.router, prefix="/payments", tags=["Payments"], dependencies=[Depends(get_current_user)])
app.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])

# Create database tables and start scheduled tasks
@app.on_event("startup")
def startup_event():
    """Create database tables and start scheduled tasks on application startup"""
    global _scheduler

    logger.info("Starting application...")

    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise

    # Validate critical configuration
    if not SECRET_KEY or SECRET_KEY == "dev-secret-key-change-in-production-minimum-32-chars":
        logger.warning("SECRET_KEY is not properly configured! Using development key.")
    else:
        logger.info("SECRET_KEY is properly configured")

    # Initialize scheduler only if enabled and not in testing
    if os.getenv("SCHEDULER_ENABLED", "True").lower() == "true" and not DEBUG:
        try:
            from services.scheduled_tasks import ScheduledTasks
            _scheduler = ScheduledTasks.start_scheduler()
        except Exception as e:
            logger.error(f"Failed to start scheduler: {str(e)}")
    else:
        logger.info("Scheduled tasks disabled in development/testing mode")

    logger.info(f"Application started in {APP_ENV} mode")