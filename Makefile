.PHONY: help install run test lint format clean migrate upgrade downgrade seed docker-up docker-down logs

help:
	@echo "🚀 Subscription & Payment API - Available commands:"
	@echo ""
	@echo "  make install      Install dependencies"
	@echo "  make run          Run development server"
	@echo "  make test         Run tests with coverage"
	@echo "  make test-unit    Run unit tests only"
	@echo "  make lint         Run linter (ruff)"
	@echo "  make format       Format code with black"
	@echo "  make clean        Clean cache and temporary files"
	@echo "  make seed         Seed database with test data"
	@echo "  make check        Validate configuration"
	@echo ""
	@echo "Database migrations:"
	@echo "  make migrate      Create new migration"
	@echo "  make upgrade      Apply migrations"
	@echo "  make downgrade    Rollback last migration"
	@echo "  make history      Show migration history"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up    Start all services"
	@echo "  make docker-down  Stop all services"
	@echo "  make docker-logs  Show service logs"
	@echo "  make docker-build Build Docker images"

install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt

run:
	@echo "🚀 Starting development server..."
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

test:
	@echo "🧪 Running tests..."
	pytest --cov=. --cov-report=html

test-unit:
	@echo "🧪 Running unit tests..."
	pytest -m unit

test-integration:
	@echo "🧪 Running integration tests..."
	pytest -m integration

lint:
	@echo "🔍 Running linter..."
	ruff check .

format:
	@echo "✨ Formatting code..."
	black .

clean:
	@echo "🧹 Cleaning temporary files..."
	rm -rf __pycache__ .pytest_cache .coverage htmlcov .ruff_cache
	rm -rf *.db *.sqlite3
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

check:
	@echo "🔍 Validating configuration..."
	python check_config.py

# Database commands
migrate:
	@echo "🗃️  Creating new migration..."
	alembic revision --autogenerate -m "update"

upgrade:
	@echo "⬆️  Applying migrations..."
	alembic upgrade head

downgrade:
	@echo "⬇️  Rolling back last migration..."
	alembic downgrade -1

history:
	@echo "📜 Migration history..."
	alembic history

seed:
	@echo "🌱 Seeding database..."
	python seed.py

# Docker commands
docker-up:
	@echo "🐳 Starting Docker services..."
	docker-compose up -d
	@echo "⏳ Waiting for services..."
	sleep 10
	@echo "✅ Services started. Web app: http://localhost:8000"

docker-down:
	@echo "🐳 Stopping Docker services..."
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-build:
	@echo "🐳 Building Docker images..."
	docker-compose build

docker-tools:
	@echo "🛠️  Starting tooling services (pgadmin, redis)..."
	docker-compose --profile tools up -d

# Development helpers
serve-static:
	@echo "📁 Serving static files..."
	python -m http.server 8080

show-urls:
	@echo "🔗 API Endpoints:"
	@echo "  Docs:     http://localhost:8000/docs"
	@echo "  Redoc:    http://localhost:8000/redoc"
	@echo "  Health:   http://localhost:8000/health"
	@echo "  API:      http://localhost:8000/api/v1"

create-admin:
	@echo "👤 Creating admin user..."
	python -c "
	from main import engine, SessionLocal
	from models import User
	from passlib.context import CryptContext

	pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
	db = SessionLocal()
	hashed = pwd_context.hash('admin123')
	admin = User(
		username='admin',
		email='admin@example.com',
		hashed_password=hashed,
		full_name='Admin',
		is_active=True,
		is_admin=True
	)
	db.add(admin)
	db.commit()
	print('✅ Admin user created: admin / admin123')
	db.close()
	"
