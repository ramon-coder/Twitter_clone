# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2024-01-15 (Optimized Version)

### Added

- **Rate limiting middleware** - Protection against brute force attacks on auth endpoints
- **Comprehensive logging** system with file and console handlers
- **Configuration validation script** (`check_config.py`) - Validates environment variables on startup
- **Database seeding script** (`seed.py`) - Populates DB with test data for development
- **Makefile** with common development commands (install, run, test, lint, migrate, etc.)
- **Docker health checks** for web and database services
- **Alembic migrations** for database schema versioning
- **.env.example** template with all required environment variables
- **pyproject.toml** with Ruff linter configuration
- **.dockerignore** for optimized Docker builds
- **Webhook router** converted from Flask to FastAPI (previously using mixed frameworks)
- **Individual model files** separated from monolithic `models/__init__.py`
- **Missing files**: `models/invoice.py`, `models/user.py`, `models/plan.py`, `models/subscription.py`, `models/payment.py`

### Changed

- **Updated dependencies** to latest stable versions:
  - FastAPI: 0.104.1 → 0.109.0
  - Uvicorn: 0.24.0 → 0.27.0
  - SQLAlchemy: 2.0.23 → 2.0.25
  - Pydantic: 2.5.2 → 2.6.1
  - Added: Alembic (1.13.1), SlowAPI (0.1.9), Ruff
- **Improved CORS** configuration:
  - Restricted origins in production (only specific domains)
  - Explicit HTTP methods instead of wildcard
  - Added rate limit headers to CORS exposed headers
- **Enhanced security**:
  - SECRET_KEY validation on startup (rejects shorts keys in production)
  - Rate limiting on authentication endpoints (5 attempts per 60s)
  - Removed hardcoded insecure default secrets
- **Better error handling**:
  - Added HTTP exception handler with proper logging
  - Global exception handler logs stack traces
  - Webhook endpoints now use proper FastAPI exception handling
- **Scheduler improvements** (`services/scheduled_tasks.py`):
  - Prevents multiple scheduler instances in multi-process deployments
  - Uses SQLAlchemy job store for persistence
  - Added graceful shutdown method
  - Comprehensive error logging per task
  - Fixed month calculation bug in monthly report
- **Database connection pooling**:
  - Uses proper pooling for PostgreSQL in production
  - `check_same_thread=False` for SQLite in dev
- **Code organization**:
  - Models split into individual files per entity
  - Middleware moved to dedicated package
  - Custom exceptions module (`exceptions.py`)
- **Docker Compose improvements**:
  - Added health checks for all services
  - Added Redis service (optional, for future distributed features)
  - Added pgAdmin (optional, profile 'tools')
  - Database initialization with Alembic migrations
  - Better service dependency ordering

### Fixed

- **Critical**: `webhooks.py` was using Flask instead of FastAPI - completely rewritten
- `models/__init__.py` had all models in one file - now properly separated
- Scheduler would start multiple instances in Gunicorn/uWSGI deployments
- CORS was dangerously permissive (`allow_methods=["*"]`)
- No validation of required environment variables
- No rate limiting on auth endpoints (vulnerable to brute force)
- Webhook handlers used placeholder Database class - now use proper SQLAlchemy sessions
- Missing imports in several files
- Scheduled tasks used `datetime.utcnow()` mixed with naive/aware datetime issues
- Payment webhook handlers had incorrect type hints
- Subscription renewal incorrectly calculated dates
- Invoices table missing payment_id foreign key reference

### Security

- [x] All endpoints behind authentication middleware where appropriate
- [x] Password hashing with bcrypt (passlib)
- [x] JWT tokens with configurable expiration
- [x] SECRET_KEY validation (min 32 chars in production)
- [x] Rate limiting on sensitive endpoints
- [x] CORS properly configured per environment
- [x] No hardcoded secrets in code (all via environment variables)
- [x] SQL injection protection via ORM
- [x] XSS protection via proper headers (CORS)

### Developer Experience

- [x] Single command setup: `make install && make run`
- [x] Automatic database seeding for development
- [x] Comprehensive test configuration with pytest
- [x] Code formatting with Black (via Makefile)
- [x] Linting with Ruff (configurable via pyproject.toml)
- [x] Detailed logging to console and file
- [x] Health check endpoint with system status
- [x] Clear error messages in development modes
- [x] Auto-reload in development mode

### Production Readiness

- [x] Docker multi-stage builds (optimized image size)
- [x] PostgreSQL recommended for production
- [x] Database connection pooling configured
- [x] Alembic migrations for zero-downtime deployments
- [x] Structured logging ready for ELK/Loki integration
- [x] Graceful shutdown handling (scheduler)
- [x] Health checks for container orchestration (Kubernetes)

### Documentation

- [x] Comprehensive README with architecture overview
- [x] Configuration guide with examples
- [x] Docker deployment instructions
- [x] API endpoint documentation (Swagger/ReDoc auto-generated)
- [x] Environment variables reference
- [x] Database schema documentation in model docstrings
- [x] Security best practices documented
- [x] Contributing guidelines

## [1.0.0] - 2023-XX-XX (Original Version)

### Added

- Initial project scaffold
- Basic CRUD for users, plans, subscriptions, payments
- Stripe integration for payment processing
- Email notifications via SendGrid
- Scheduled tasks with APScheduler
- Basic authentication with JWT
- SQLite/PostgreSQL support

### Security

- ⚠️ Flask webhooks (mixed framework issue)
- ⚠️ No rate limiting
- ⚠️ Permissive CORS (`*` for all methods)
- ⚠️ Hardcoded fallback secrets
- ⚠️ Models in single file (poor organization)

[1.1.0]: https://github.com/yourusername/your-repo/compare/v1.0.0...v1.1.0
