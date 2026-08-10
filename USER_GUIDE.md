# NexBank Agentic AI - Operational User Guide

This user guide provides operational instructions for all 5 authorized user roles operating the NexBank Agentic AI Customer Service & Governance Platform.

---

## 1. Role-Based Access Control (RBAC) Matrix

| User Role | Accessible Features & Dashboards | Security Authorization Level |
| :--- | :--- | :--- |
| `CUSTOMER` | Interactive Chat, Balance Enquiry, Statement Request, Card Controls, Dispute raising | JWT Bearer (Scope: `customer`) |
| `SUPPORT_AGENT` | Live Escalation Queue, Human Handoff, Chat History, Customer Context | JWT Bearer (Scope: `support_agent`) |
| `SUPERVISOR` | Supervisor Review Console, SLA Monitors, Model Fine-Tuning Queue, CSAT Metrics | JWT Bearer (Scope: `supervisor`) |
| `RISK_OFFICER` | Guardrails Log, Prompt Injection Stream, SAR High-Value Transaction Alerts | JWT Bearer (Scope: `risk_officer`) |
| `SYSTEM_ADMIN` | Microservices Diagnostics, Knowledge Base Seeding, Model Versioning / A/B Toggles | JWT Bearer (Scope: `system_admin`) |

---

## 2. Customer Operations Manual

### Initiating a Banking Chat Session
1. Open the Web Application at `http://localhost:8000` (or production URL).
2. The AI assistant **NexAssistant** will automatically initialize your session.
3. Select any Quick Action chip (e.g., *Balance Enquiry*, *Statement Request*, *Block Card*) or type a natural language prompt in English or Hinglish.

### High-Stakes Account Actions (Confirmation-Before-Action)
For sensitive operations like **Card Blocking** or **Account Disclosures**, the AI agent will trigger a safety confirmation:
> ⚠️ **Confirmation Required:** Are you sure you want to block your debit card ending in 4521? Please reply 'YES' to proceed.
Reply **'YES'** to execute the banking action.

---

## 3. Supervisor & Support Agent Manual

### Managing Escalations & SLA Queue
1. Navigate to the **Supervisor Console** tab in the top navigation menu.
2. The table displays open escalations sorted by Priority (`P1`: 5 min, `P2`: 15 min, `P3`: 60 min).
3. Click **Take Handoff** to claim the conversation and engage directly with the customer.

### Submitting Model Corrections
1. Review flagged AI responses in the review queue.
2. Provide the corrected response text and severity rating (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
3. Submit to push the correction directly to the **Continuous Learning Pipeline**.

---

## 4. Administrator Operations Manual

### Knowledge Base Management
1. Navigate to the **Admin & RAG DB** tab.
2. Click **🌱 Seed Knowledge Base** to populate 50+ banking product, policy, and regulatory guidelines into PostgreSQL and ChromaDB vector store.
3. View real-time diagnostic checks for Database, Cache, and Vector DB.
