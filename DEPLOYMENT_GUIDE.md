# NexBank Agentic AI - Enterprise Production Deployment Guide

**Author / Conversational AI Architect**: SATHVIKA BOINA  
**Organization**: NexBank Digital Banking Platform  

This guide provides step-by-step production deployment procedures for Docker Compose, Kubernetes, PostgreSQL, Redis, and ChromaDB.

---

## 1. Prerequisites & System Requirements

- **Operating System**: Linux (Ubuntu 22.04 LTS / RHEL 9) or Windows Server 2022
- **Container Runtime**: Docker Engine 24.0+ & Docker Compose v2.20+
- **CPU & RAM**: Minimum 4 vCPUs, 16 GB RAM (Recommended 32 GB RAM for production traffic)
- **Database Subsystems**: PostgreSQL 15+, Redis 7.0+, ChromaDB 0.4+

---

## 2. Docker Compose One-Command Deployment

From the repository root directory, execute:

```bash
# 1. Environment File Preparation
cp .env.example .env

# 2. Build and Launch Containers
docker-compose up -d --build
```

Verify running services:
```bash
docker-compose ps
```

The stack exposes:
- **FastAPI Core Engine**: `http://localhost:8000`
- **Swagger Open API Docs**: `http://localhost:8000/docs`
- **Prometheus Metrics**: `http://localhost:8000/metrics`
- **Web UI Dashboard**: `http://localhost:8000`

---

## 3. Production Environment Configuration (`.env`)

```ini
APP_NAME="NexBank Agentic AI"
ENVIRONMENT="production"
DEBUG=False
SECRET_KEY="<SUPER_SECRET_STRONG_KEY>"

# PostgreSQL Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<SECURE_PASSWORD>
POSTGRES_DB=nexbank_ai
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis Cache
REDIS_HOST=redis
REDIS_PORT=6379

# Vector DB
CHROMADB_PATH=./chroma_db
```

---

## 4. Production Database Migrations

Apply Alembic schema migrations:

```bash
docker-compose exec backend alembic upgrade head
```

---

## 5. Health Verification & Scrape Endpoints

```bash
# Health Check Endpoint
curl http://localhost:8000/health

# Prometheus Metrics Scrape
curl http://localhost:8000/metrics
```
