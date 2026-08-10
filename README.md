# NexBank Agentic AI - Customer Service Platform with Feedback Loops

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB.svg?style=flat&logo=python)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1.svg?style=flat&logo=postgresql)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7.0-DC382D.svg?style=flat&logo=redis)](https://redis.io/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-0.4.24-FF6F00.svg?style=flat)](https://www.trychroma.com/)
[![License](https://img.shields.io/badge/License-Proprietary-blue.svg)](#)

**Author / Conversational AI Architect**: SATHVIKA BOINA  
**Organization**: NexBank Digital Banking Platform  

---

## 🌟 Key Architecture & Highlights

- **Clean Architecture & SOLID Design**: Fully decoupled Domain, Repository, Service, and Controller layers with Pydantic v2 schemas and SQLAlchemy 2.0 async ORM models.
- **Authentication & RBAC**: JWT Access Tokens (30 min) & Refresh Token Rotation (7 days) with 5-attempt security lockout and 5 role levels (`CUSTOMER`, `SUPPORT_AGENT`, `SUPERVISOR`, `RISK_OFFICER`, `SYSTEM_ADMIN`).
- **3-Tier Hierarchical NLU**: 32 intents across 6 primary banking domains (`account`, `transaction`, `card`, `product`, `complaint`, `security`), domain entity extraction (PAN, Aadhaar, Luhn card check), disambiguation probes for 6 confused intent pairs, sentiment analysis ($[-1, +1]$), and Hinglish code-switching detection.
- **Hybrid RAG Engine**: Dense Vector Search (ChromaDB, weight 0.6) + Sparse BM25 Search (weight 0.4) with Cross-Encoder Re-Ranking under sub-200ms P95 latency budget.
- **Agentic Workflow Engine**: Multi-turn dialogue state tracking (`DialogueState` with 20-turn history buffer), Redis cache + Postgres state persistence, streaming WebSocket endpoint, and confirmation-before-action protocols.
- **10 Core Banking Workflows**: Integrated mock services for Balance Enquiry, Statement Request, Card Blocking, Card Replacement, Complaint Registration, Complaint Tracking, Transaction Dispute, UPI Failure Resolution, Loan Eligibility, and Product Information.
- **Safety Guardrails**: Prompt Injection & Jailbreak Scanner, SEBI Financial Advice Prohibition & Disclaimer, automated PII Scrubber (PAN, Aadhaar, 16-digit cards), and PCI DSS output sanitization.
- **Human Escalation Matrix**: 15 automated escalation triggers with SLA queue routing (`FRAUD_OPERATIONS`, `SECURITY_DESK`, `SUPERVISOR_QUEUE`, etc.) and priority timers (`P1`: 5m, `P2`: 15m, `P3`: 60m).
- **Continuous Learning & Governance**: Customer CSAT feedback collection, supervisor review correction queue, model version tracking (`v1.0.0`), and A/B testing infrastructure (`v1.1.0-candidate`).
- **Production Infrastructure & UI**: Glassmorphic multi-portal Web UI (5 Dashboards), Prometheus metrics (`/metrics`), OWASP security headers, and Locust 500-user load testing.

---

## 🚀 Quick Start (Docker Compose)

```bash
# 1. Clone & prepare environment
git clone https://github.com/nexbank/agentic-ai-platform.git
cd agentic-ai-platform
cp .env.example .env

# 2. Build and launch services via Docker Compose
docker-compose up -d --build

# 3. Apply database migrations & seed Knowledge Base
docker-compose exec backend alembic upgrade head
curl -X POST http://localhost:8000/api/v1/knowledge/seed
```

Access the platform:
- **Web App & Glassmorphic UI**: `http://localhost:8000`
- **Interactive OpenAPI Docs**: `http://localhost:8000/docs`
- **Prometheus Metrics Endpoint**: `http://localhost:8000/metrics`

---

## 🧪 Automated Testing & Benchmarks

Run the complete test suite across all 15 modules:

```bash
pytest backend/tests/ -v
```

Execute Locust load test (500 concurrent users):
```bash
locust -f load_test_locust.py --host=http://localhost:8000
```

---

## 📚 Documentation Index

- [Architecture Guide](ARCHITECTURE.md) - Deep-dive design specifications & system diagrams
- [User Manual](USER_GUIDE.md) - Role-based operational guide for Customers, Support Agents & Supervisors
- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Production deployment procedures for Docker & Kubernetes
- [Requirement Traceability Matrix](REQUIREMENT_TRACEABILITY_MATRIX.md) - Complete mapping of all specification requirements
- [Changelog](CHANGELOG.md) - Chronological milestone development history
