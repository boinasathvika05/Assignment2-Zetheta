# 🏷️ Intent Taxonomy & Entity Disambiguation Specification

**Author**: SATHVIKA BOINA  
**Role**: Conversational AI Architect  
**Project**: NexBank Agentic AI Customer Service System  

---

## 1. Intent Taxonomy Overview (32 Intents)

The NLU engine supports 32 intent categories organized under 6 primary banking domains.

### 1.1 Account Domain (`ACC`)
- `ACC-001`: `balance_enquiry` — Check savings/current account balance.
- `ACC-002`: `statement_request` — Request 30-day/90-day bank statement via email/PDF.
- `ACC-003`: `account_details` — View IFSC code, branch address, or account number.
- `ACC-004`: `cheque_book_request` — Order new cheque book.
- `ACC-005`: `account_closure` — Initiate account closure request (Requires Escalation / Confirmation).

### 1.2 Transaction Domain (`TXN`)
- `TXN-001`: `transaction_history` — View recent credits/debits.
- `TXN-002`: `dispute_transaction` — Report unauthorized debit or payment failure.
- `TXN-003`: `upi_issue` — UPI payment pending, failed, or money debited.
- `TXN-004`: `fund_transfer_enquiry` — NEFT/RTGS/IMPS status check.

### 1.3 Card Domain (`CRD`)
- `CRD-001`: `block_card` — Block lost/stolen debit or credit card (Confirmation Required).
- `CRD-002`: `unblock_card` — Temp unblock debit card (Auth Required).
- `CRD-003`: `reissue_card` — Request new physical debit card replacement.
- `CRD-004`: `pin_reset` — Generate or reset debit card Green PIN.
- `CRD-005`: `card_limit_change` — Modify daily ATM/POS transaction limit.

### 1.4 Product Domain (`PRD`)
- `PRD-001`: `fixed_deposit_enquiry` — Interest rates and tenure for FDs/RDs.
- `PRD-002`: `loan_eligibility` — Home loan, personal loan, auto loan rates & eligibility.
- `PRD-003`: `credit_card_apply` — Features, eligibility, and application for credit cards.
- `PRD-004`: `insurance_query` — Health & life insurance partner coverage.
- `PRD-005`: `investment_advice` — Mutual funds, stocks, wealth advice (Triggers SEBI Guardrail).

### 1.5 Complaint Domain (`CMP`)
- `CMP-001`: `register_complaint` — Log formal grievance with Ombudsman SLA tracking.
- `CMP-002`: `track_complaint` — Check status of existing complaint ticket.
- `CMP-003`: `agent_escalation` — Request direct human supervisor handoff.

### 1.6 Security Domain (`SEC`)
- `SEC-001`: `report_fraud` — Urgent cyber fraud or unauthorized phishing alert (Immediate P1 Escalation).
- `SEC-002`: `change_password` — NetBanking or Mobile Banking credentials update.
- `SEC-003`: `kyc_update` — Video KYC, PAN linkage, or address update procedures.

---

## 2. Hinglish & Code-Switching Heuristics

To support India's multilingual population, the NLU engine processes Hinglish queries:
- `"Mera balance kitna hai"` $\rightarrow$ `ACC-001` (`balance_enquiry`)
- `"Card block karo urgent"` $\rightarrow$ `CRD-001` (`block_card`)
- `"Paise kat gaye par receiver ko nahi mile"` $\rightarrow$ `TXN-003` (`upi_issue`)
- `"Kahan invest karun bataye"` $\rightarrow$ `PRD-005` (`investment_advice`)
- `"Insaan se baat karwao"` $\rightarrow$ `CMP-003` (`agent_escalation`)

---

## 3. Disambiguation Policies

When NLU confidence gap between top-2 candidate intents is $<0.15$:
1. System triggers a clarification probe offering quick-selection options.
2. Example: Prompting user to clarify whether they wish to block card (`CRD-001`) or report unauthorized transaction fraud (`SEC-001`).
