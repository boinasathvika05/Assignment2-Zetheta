# NexBank Agentic AI - System Architecture & Technical Specifications

This document details the architectural design, clean architecture patterns, 3-tier NLU taxonomy, hybrid RAG engine, safety guardrails, and human escalation matrix for the NexBank Agentic AI platform.

---

## 1. System Architecture Overview

```
                           +-------------------------------------+
                           |      Web Browser / Mobile App       |
                           +------------------+------------------+
                                              |
                                              v (HTTPS / WS)
                           +------------------+------------------+
                           |  Production Infrastructure Layer   |
                           |  - CORS / Security Headers (OWASP)  |
                           |  - Prometheus Latency Metrics       |
                           |  - Rate Limiting & Correlation ID   |
                           +------------------+------------------+
                                              |
                                              v
                           +------------------+------------------+
                           |    FastAPI Application Core Engine  |
                           +------------------+------------------+
                                              |
        +-------------------------------------+-------------------------------------+
        |                                     |                                     |
        v                                     v                                     v
+-------+-------+                     +-------+-------+                     +-------+-------+
|  Module 8     |                     |  Module 4     |                     |  Module 5     |
| Safety        |                     | Hierarchical  |                     | Hybrid RAG    |
| Guardrails    |                     | NLU Engine    |                     | Engine        |
| - Prompt Inj  |                     | - 3-Tier Tax  |                     | - Dense Vector|
| - PII Scrubber|                     | - Entity Ext  |                     | - Sparse BM25 |
| - SEBI Advice |                     | - Disambig    |                     | - Re-Ranking  |
+-------+-------+                     +-------+-------+                     +-------+-------+
        |                                     |                                     |
        +-------------------------------------+-------------------------------------+
                                              |
                                              v
                           +------------------+------------------+
                           |  Module 6: Agentic Workflow Engine  |
                           |  - Multi-Turn Reasoning & State     |
                           |  - Confirmation-Before-Action       |
                           |  - Module 7 Banking Actions         |
                           +------------------+------------------+
                                              |
        +-------------------------------------+-------------------------------------+
        |                                     |                                     |
        v                                     v                                     v
+-------+-------+                     +-------+-------+                     +-------+-------+
|  Module 2/3   |                     |  Module 9     |                     |  Module 10    |
| PostgreSQL    |                     | Human         |                     | Continuous    |
| & Redis       |                     | Escalation    |                     | Learning      |
| State Cache   |                     | (15 Triggers) |                     | Pipeline      |
+---------------+                     +---------------+                     +---------------+
```

---

## 2. Core Architectural Pillars

### Clean Architecture & SOLID Principles
- **Domain Layer (`app/models/`)**: Pure SQLAlchemy 2.0 entities decoupled from business rules.
- **Repository Layer (`app/repositories/`)**: Abstract data access interfaces (`UserRepository`, `SessionRepository`).
- **Service Layer (`app/services/`)**: High-level domain logic (`AuthService`, `ConversationService`, `KnowledgeService`).
- **API Layer (`app/api/`)**: Thin REST controller wrappers mapping HTTP requests to schemas.

### 3-Tier Hierarchical NLU Engine
- **Primary Level**: 6 core banking domains (`account`, `transaction`, `card`, `product`, `complaint`, `security`).
- **Secondary Level**: 32 specific intent codes (`ACC-001`, `CRD-001`, `TXN-002`, `PRD-001`, etc.).
- **Tertiary Level**: Slot parameters and entity extraction with Luhn check, PAN validation, and PCI DSS compliance.

### Hybrid RAG Engine
- **Dense Vector Search (0.6)**: Cosine similarity via ChromaDB persistent store.
- **Sparse BM25 Search (0.4)**: Term frequency-inverse document frequency matching.
- **Cross-Encoder Re-Ranking**: Sub-200ms P95 re-scoring.
