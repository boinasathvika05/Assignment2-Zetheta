# 📜 Audit & Compliance Logging Specification

**Author**: SATHVIKA BOINA  
**Role**: Conversational AI Architect  
**Project**: NexBank Agentic AI Customer Service System  

---

## 1. Overview & Compliance Directives
This specification defines the audit and regulatory logging schemas for interaction-level and turn-level event tracking in accordance with **RBI Master Direction on Digital Payment Security Controls**, **PCI-DSS v4.0**, and **MeitY IT Rules 2011**.

---

## 2. Interaction-Level Log Schema

```json
{
  "interaction_id": "INT-8839210-2026",
  "conversation_id": "3b2a10f-8c91-419b-a110-99214a",
  "customer_id": "CUST-110294817502",
  "start_time": "2026-08-10T14:30:00.000Z",
  "end_time": "2026-08-10T14:32:15.000Z",
  "total_turns": 4,
  "primary_intent": "CRD-001",
  "containment_status": "CONTAINED_BY_AI",
  "csat_score": 5,
  "pii_redacted_count": 2,
  "escalated": false,
  "model_version": "v1.0.0"
}
```

---

## 3. Turn-Level Log Schema

```json
{
  "turn_id": "TURN-001",
  "conversation_id": "3b2a10f-8c91-419b-a110-99214a",
  "turn_number": 1,
  "timestamp": "2026-08-10T14:30:05.120Z",
  "raw_user_input": "I lost my debit card ending 4521, please block it",
  "sanitized_user_input": "I lost my debit card ending 4521, please block it",
  "nlu_intent": "CRD-001",
  "nlu_confidence": 0.95,
  "entities_extracted": {"card_last4": "4521"},
  "guardrails_evaluated": ["PII_SCRUBBER", "PROMPT_INJECTION", "CONFIRMATION_GATE"],
  "guardrail_status": "PASS",
  "action_taken": "PENDING_CONFIRMATION",
  "bot_response": "⚠️ CONFIRMATION REQUIRED: Are you sure you want to permanently block your NexBank Debit Card ending in 4521? Reply YES to confirm.",
  "latency_ms": {
    "nlu_ms": 12.4,
    "guardrail_ms": 8.1,
    "rag_ms": 0.0,
    "total_turn_ms": 24.5
  }
}
```
