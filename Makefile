.PHONY: help build up down logs shell test clean db-only backend-only frontend-only

help:
	@echo "Contoso Bookings - Development Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make build          - Build Docker containers"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make logs           - View all container logs"
	@echo "  make logs-backend   - View backend logs"
	@echo "  make logs-frontend  - View frontend logs"
	@echo "  make logs-db        - View DocumentDB logs"
	@echo "  make shell          - Open a shell in the backend container"
	@echo "  make db-connect     - Connect to DocumentDB with mongosh"
	@echo "  make db-only        - Start only DocumentDB"
	@echo "  make backend-only   - Start only backend + DocumentDB"
	@echo "  make clean          - Clean up containers and volumes"
	@echo ""
	@echo "Development (without Docker):"
	@echo "  make dev-backend    - Run backend locally"
	@echo "  make dev-frontend   - Run frontend locally"
	@echo "  make install        - Install all dependencies"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo ""
	@echo "✅ Services started!"
	@echo "   - Frontend:    http://localhost:3000"
	@echo "   - Backend API: http://localhost:8000/docs"
	@echo "   - DocumentDB:  mongodb://admin:password123@localhost:10260"
	@echo ""

down:
	docker-compose down

logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

logs-db:
	docker-compose logs -f documentdb

shell:
	docker-compose exec backend /bin/bash

db-connect:
	mongosh "mongodb://admin:password123@localhost:10260/?tls=true&tlsAllowInvalidCertificates=true"

db-only:
	docker-compose up -d documentdb
	@echo "✅ DocumentDB started on port 10260"

backend-only:
	docker-compose up -d documentdb backend
	@echo "✅ Backend + DocumentDB started"
	@echo "   - Backend API: http://localhost:8000/docs"

clean:
	docker-compose down -v
	@echo "✅ Containers and volumes removed"

# Development commands (run locally without Docker)
dev-backend:
	cd src/api && uvicorn main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd src/frontend && npm start

install:
	pip install -r requirements.txt
	cd src/frontend && npm install
	@echo "✅ All dependencies installed"
