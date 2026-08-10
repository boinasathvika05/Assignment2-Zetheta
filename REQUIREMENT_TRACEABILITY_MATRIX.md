# NexBank Agentic AI - Requirement Traceability Matrix (RTM)

This matrix maps every functional requirement, non-functional requirement, safety guardrail, NLU taxonomy code, and architectural constraint from the official NexBank project specification (`463548C_Agentic-AI_Customer_Service_Agent.docx.pdf`) to its exact code implementation and test verification.

---

## 1. Project Requirements & Implementation Mapping

| Req ID | Requirement Category | Specification Description | Implementation Location | Verification Status |
| :--- | :--- | :--- | :--- | :--- |
| **REQ-001** | Core Architecture | Clean Architecture with SOLID principles, 0 TODOs | Root repository codebase | ✅ VERIFIED (100% Complete) |
| **REQ-002** | Authentication | JWT Access (30 min) & Refresh Token (7 days) rotation | `backend/app/core/security.py` | ✅ VERIFIED (`test_auth.py`) |
| **REQ-003** | Security Lockout | 5 failed attempts locks account for 15 minutes | `backend/app/services/auth_service.py` | ✅ VERIFIED (`test_auth.py`) |
| **REQ-004** | RBAC Roles | Customer, Support Agent, Supervisor, Risk Officer, Admin | `backend/app/api/deps.py` | ✅ VERIFIED (`test_auth.py`) |
| **REQ-005** | Database Models | 11 PostgreSQL domain models with UUID & Alembic DDL | `backend/app/models/` | ✅ VERIFIED (All 11 Models) |
| **REQ-006** | State Persistence | Dual Redis (<10ms cache) + Postgres state tracking | `backend/app/services/conversation_service.py` | ✅ VERIFIED (`test_conversation.py`) |
| **REQ-007** | Dialogue State | DialogueState object with 20-turn history buffer | `backend/app/schemas/dialogue.py` | ✅ VERIFIED (`test_conversation.py`) |
| **REQ-008** | Streaming Chat | WebSocket streaming endpoint `WS /chat/ws/{id}` | `backend/app/api/v1/endpoints/chat_ws.py` | ✅ VERIFIED |
| **REQ-009** | NLU Taxonomy | 30+ intent taxonomy across 6 domains with Out-of-Scope | `backend/app/services/nlu/intent_classifier.py` | ✅ VERIFIED (`test_nlu.py`) |
| **REQ-010** | Entity Extraction | PAN format, UPI handle, Luhn card check, Card last 4 | `backend/app/services/nlu/entity_extractor.py` | ✅ VERIFIED (`test_nlu.py`) |
| **REQ-011** | Disambiguation | Resolves 6 specified confused intent pairs | `backend/app/services/nlu/disambiguator.py` | ✅ VERIFIED (`test_nlu.py`) |
| **REQ-012** | Sentiment & Hinglish| Continuous sentiment [-1, +1] & Hinglish detection | `backend/app/services/nlu/sentiment_language.py` | ✅ VERIFIED (`test_nlu.py`) |
| **REQ-013** | Hybrid RAG | Dense Vector (0.6) + Sparse BM25 (0.4) + Re-Ranking | `backend/app/services/rag/hybrid_retriever.py` | ✅ VERIFIED (`test_rag.py`) |
| **REQ-014** | KB Seeding | 50+ banking product, policy & regulatory entries | `backend/app/services/knowledge_service.py` | ✅ VERIFIED (`POST /knowledge/seed`) |
| **REQ-015** | Agent Workflow | Multi-turn reasoning, clarification & confirmation flow | `backend/app/services/agent_workflow.py` | ✅ VERIFIED (`test_conversation.py`) |
| **REQ-016** | Banking Actions | 10 secure core banking API workflows | `backend/app/services/banking_service.py` | ✅ VERIFIED (`test_banking_actions.py`) |
| **REQ-017** | Prompt Injection | Scanner for DAN mode, system prompt extraction | `backend/app/services/guardrails_service.py` | ✅ VERIFIED (`test_governance.py`) |
| **REQ-018** | SEBI Compliance | Intercepts financial advice & appends disclaimer | `backend/app/services/guardrails_service.py` | ✅ VERIFIED (`test_governance.py`) |
| **REQ-019** | PII Scrubber | Redacts PAN, Aadhaar, 16-digit cards in text & logs | `backend/app/services/guardrails_service.py` | ✅ VERIFIED (`test_governance.py`) |
| **REQ-020** | Escalation Router | 15 Escalation Triggers with SLA Queue Routing | `backend/app/services/escalation_service.py` | ✅ VERIFIED (`test_governance.py`) |
| **REQ-021** | Continuous Learn | CSAT feedback collection & Supervisor corrections | `backend/app/services/continuous_learning_service.py`| ✅ VERIFIED |
| **REQ-022** | Dashboards | Multi-portal glassmorphic Web UI | `frontend/public/` | ✅ VERIFIED (5 Dashboards) |
| **REQ-023** | Prometheus | `/metrics` endpoint with latency histograms | `backend/app/core/middleware.py` | ✅ VERIFIED |
| **REQ-024** | Performance | Sub-100ms NLU & Sub-200ms P95 RAG Latency Budget | `backend/tests/test_performance.py` | ✅ VERIFIED (`test_performance.py`) |
| **REQ-025** | Load Testing | Locust 500-user load testing script | `load_test_locust.py` | ✅ VERIFIED |
