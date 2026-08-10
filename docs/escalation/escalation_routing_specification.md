# 🚨 Human Escalation Routing Logic & Handoff Specification

**Author**: SATHVIKA BOINA  
**Role**: Conversational AI Architect  
**Project**: NexBank Agentic AI Customer Service System  

---

## 1. Escalation Trigger Matrix (15 Conditions)

| Trigger ID | Condition Name | Priority | Assigned Queue | Target SLA |
| :--- | :--- | :---: | :--- | :---: |
| `TRG-001` | Unauthorized Transaction Fraud Alert | `P1` | `FRAUD_OPERATIONS` | $5\text{ mins}$ |
| `TRG-002` | High Negative Sentiment Score ($<-0.70$) | `P2` | `SUPERVISOR_QUEUE` | $15\text{ mins}$ |
| `TRG-003` | Low NLU Confidence ($<0.40$) 2 Consecutive Turns | `P3` | `CUSTOMER_SUPPORT` | $60\text{ mins}$ |
| `TRG-004` | Explicit Human Agent Request | `P2` | `CUSTOMER_SUPPORT` | $15\text{ mins}$ |
| `TRG-005` | Account Lockout / Password Security Alert | `P1` | `SECURITY_DESK` | $5\text{ mins}$ |
| `TRG-006` | System Exception / Core API Error | `P2` | `TECH_SUPPORT` | $15\text{ mins}$ |
| `TRG-007` | Repeated Query Loop (3+ identical turns) | `P3` | `CUSTOMER_SUPPORT` | $60\text{ mins}$ |
| `TRG-008` | High Value Transaction Dispute ($>\text{₹}50,000$) | `P1` | `FRAUD_OPERATIONS` | $5\text{ mins}$ |
| `TRG-009` | AML / PEP Watchlist Name Match | `P1` | `COMPLIANCE_DESK` | Immediate |
| `TRG-010` | Verification Auth Failure (3 invalid attempts) | `P2` | `SECURITY_DESK` | $15\text{ mins}$ |
| `TRG-011` | Complex Custom Business Loan Request | `P3` | `LOAN_SPECIALISTS` | $60\text{ mins}$ |
| `TRG-012` | Legal / Ombudsman Threat Mention | `P1` | `LEGAL_COMPLIANCE` | $5\text{ mins}$ |
| `TRG-013` | VIP / High Net Worth Customer Account | `P1` | `VIP_CONCIERGE` | $5\text{ mins}$ |
| `TRG-014` | Long Unresolved Conversation ($>15$ turns) | `P2` | `SUPERVISOR_QUEUE` | $15\text{ mins}$ |
| `TRG-015` | Severe Profanity / Violent Threat | `P1` | `SECURITY_DESK` | $5\text{ mins}$ |

---

## 2. 8-Element Context Handoff Package

When an escalation triggers, the router serializes an 8-element payload to PostgreSQL `escalations`:
1. `conversation_id`: Unique session UUID.
2. `customer_id`: Authenticated customer identifier.
3. `trigger_id`: Primary trigger condition (`TRG-001` to `TRG-015`).
4. `priority`: Assigned SLA level (`P1`, `P2`, `P3`).
5. `queue_name`: Target support desk.
6. `dialogue_summary`: 3-sentence automated summary of customer query.
7. `slots_extracted`: Dictionary of collected entity values.
8. `full_turn_history`: Complete transcript up to escalation moment.
