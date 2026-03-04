"""
Main Application File for Subscription and Recurring Payments Management System

This file serves as the entry point to the FastAPI application, setting up
the core configurations, database connection, authentication, and global
error handling middleware.
"""

import os
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Application configuration
APP_TITLE = "Subscription and Recurring Payments Management System"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = """
API for managing subscriptions and recurring payments.
Supports user authentication, plan management, subscription lifecycle,
and payment processing with Stripe integration.
"""

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./subscriptions.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Global error handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    return {
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "detail": "Internal server error",
        "timestamp": datetime.now().isoformat(),
        "path": request.url.path
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": APP_VERSION
    }

# Include routers
from routers import auth, plans, users, subscriptions, payments
app.include_router(auth.router, tags=["Authentication"])
app.include_router(plans.router, prefix="/plans", tags=["Plans"], dependencies=[Depends(get_current_user)])
app.include_router(users.router, prefix="/users", tags=["Users"], dependencies=[Depends(get_current_user)])
app.include_router(subscriptions.router, prefix="/subscriptions", tags=["Subscriptions"], dependencies=[Depends(get_current_user)])
app.include_router(payments.router, prefix="/payments", tags=["Payments"], dependencies=[Depends(get_current_user)])

# Create database tables and start scheduled tasks
@app.on_event("startup")
def startup_event():
    """Create database tables and start scheduled tasks on application startup"""
    Base.metadata.create_all(bind=engine)
    # Start scheduled tasks
    from services.scheduled_tasks import ScheduledTasks
    ScheduledTasks.start_scheduler()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)