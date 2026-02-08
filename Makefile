# ================================================================
# Terra Pravah - Makefile
# Common development and deployment commands
# ================================================================

.PHONY: help install dev build test lint clean docker-build docker-up docker-down docker-logs migrate

# Default target
help:
	@echo "Terra Pravah - Development Commands"
	@echo "===================================="
	@echo ""
	@echo "Development:"
	@echo "  make install      Install all dependencies"
	@echo "  make dev          Start development servers"
	@echo "  make dev-backend  Start backend only"
	@echo "  make dev-frontend Start frontend only"
	@echo ""
	@echo "Building:"
	@echo "  make build        Build for production"
	@echo "  make build-frontend Build frontend only"
	@echo ""
	@echo "Testing:"
	@echo "  make test         Run all tests"
	@echo "  make lint         Run linters"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build Build Docker images"
	@echo "  make docker-up    Start Docker containers"
	@echo "  make docker-down  Stop Docker containers"
	@echo "  make docker-logs  View container logs"
	@echo "  make docker-prod  Start production stack"
	@echo ""
	@echo "Database:"
	@echo "  make migrate      Run database migrations"
	@echo "  make init-db      Initialize database"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean        Clean build artifacts"
	@echo "  make ssl-dev      Generate dev SSL certificates"

# ==================== Installation ====================

install: install-backend install-frontend

install-backend:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt

install-frontend:
	@echo "Installing Node.js dependencies..."
	cd frontend && npm install

# ==================== Development ====================

dev:
	@echo "Starting development servers..."
	@make -j2 dev-backend dev-frontend

dev-backend:
	@echo "Starting Flask development server..."
	python run.py

dev-frontend:
	@echo "Starting Vite development server..."
	cd frontend && npm run dev

# ==================== Building ====================

build: build-frontend
	@echo "Build complete!"

build-frontend:
	@echo "Building frontend for production..."
	cd frontend && npm run build

# ==================== Testing ====================

test: test-backend test-frontend

test-backend:
	@echo "Running Python tests..."
	python -m pytest tests/ -v

test-frontend:
	@echo "Running frontend tests..."
	cd frontend && npm test

lint: lint-backend lint-frontend

lint-backend:
	@echo "Linting Python code..."
	flake8 backend/ --max-line-length=120

lint-frontend:
	@echo "Linting frontend code..."
	cd frontend && npm run lint

# ==================== Docker ====================

docker-build:
	@echo "Building Docker images..."
	docker-compose build

docker-up:
	@echo "Starting Docker containers..."
	docker-compose up -d

docker-down:
	@echo "Stopping Docker containers..."
	docker-compose down

docker-logs:
	@echo "Viewing container logs..."
	docker-compose logs -f

docker-prod:
	@echo "Starting production Docker stack..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

docker-prod-down:
	@echo "Stopping production Docker stack..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

# ==================== Database ====================

migrate:
	@echo "Running database migrations..."
	flask db upgrade

init-db:
	@echo "Initializing database..."
	python init_db.py

migrate-create:
	@echo "Creating new migration..."
	flask db migrate -m "$(MSG)"

# ==================== Utilities ====================

clean:
	@echo "Cleaning build artifacts..."
	rm -rf frontend/dist
	rm -rf frontend/node_modules/.cache
	rm -rf __pycache__
	rm -rf backend/__pycache__
	rm -rf backend/**/__pycache__
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

ssl-dev:
	@echo "Generating development SSL certificates..."
	mkdir -p nginx/ssl
	openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
		-keyout nginx/ssl/privkey.pem \
		-out nginx/ssl/fullchain.pem \
		-subj "/C=IN/ST=State/L=City/O=Development/CN=localhost"
	@echo "Development SSL certificates generated in nginx/ssl/"

# ==================== Production Deployment ====================

deploy-check:
	@echo "Checking deployment requirements..."
	@echo "✓ Checking Docker..."
	@docker --version
	@echo "✓ Checking Docker Compose..."
	@docker-compose --version
	@echo "✓ Checking .env file..."
	@test -f .env || (echo "ERROR: .env file not found. Copy .env.example to .env" && exit 1)
	@echo "✓ All checks passed!"

deploy: deploy-check docker-prod
	@echo "Deployment complete!"
	@echo "Application running at https://localhost"
