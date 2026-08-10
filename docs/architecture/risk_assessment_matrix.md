# ⚠️ Risk Assessment Matrix (Technical, Business & Ethical)

**Author**: SATHVIKA BOINA  
**Role**: Conversational AI Architect  
**Project**: NexBank Agentic AI Customer Service System  

---

## 1. Overview
This matrix provides a comprehensive risk assessment covering technical infrastructure vulnerabilities, financial/business operational risks, and ethical AI governance in financial services.

---

## 2. Risk Matrix Table

| Risk ID | Category | Risk Description | Likelihood | Impact | Severity | Mitigation Strategy | Residual Risk |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- | :---: |
| `RSK-001` | Technical | Vector DB cold-start latency exceeding RAG 200ms budget | Low | High | **Medium** | Pre-warm embeddings into CPU RAM at startup | Low |
| `RSK-002` | Security | Prompt injection or jailbreak extracting system rules | Medium | High | **High** | Rule-based pre-scanner & immutable safety layer | Very Low |
| `RSK-003` | Regulatory | Unintended equity advice violating SEBI Robo-Advisory rules | Medium | Critical | **High** | Mandate SEBI disclaimer & block direct stock recommendations | Very Low |
| `RSK-004` | Compliance | PCI-DSS card number leakage in turn history logs | Low | Critical | **High** | Automated 16-digit Luhn card scrubber & output masking | Very Low |
| `RSK-005` | Business | High escalation volume overloading support call center | Medium | Medium | **Medium** | Automated SLA queue rebalancing & self-service links | Low |
| `RSK-006` | Ethical | Algorithmic bias in loan pre-approval calculations | Low | High | **Medium** | Human-in-the-loop validation for custom loan approvals | Low |
