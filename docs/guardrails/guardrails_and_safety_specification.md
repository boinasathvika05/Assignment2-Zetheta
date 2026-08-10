# 🛡️ Safety Guardrails & Security Boundary Specification

**Author**: SATHVIKA BOINA  
**Role**: Conversational AI Architect  
**Project**: NexBank Agentic AI Customer Service System  

---

## 1. Safety Guardrails Architecture

The Guardrail Safety Engine enforces 8 security boundaries and compliance rules prior to response generation and execution.

---

## 2. Mandatory Security Boundaries

1. **SEBI Financial Advice Boundary**: The bot cannot recommend individual stocks, equity funds, or guarantee investment returns. It MUST attach the mandatory disclaimer:
   > *"Disclaimer: Information provided is for educational purposes only. NexBank does not offer direct equity investment advice. Please consult a SEBI-registered financial advisor before making investment decisions."*

2. **PII & PCI-DSS Redaction Engine**: Masks sensitive data before logging or response rendering:
   - **PAN**: `ABCDE1234F` $\rightarrow$ `[REDACTED PAN]`
   - **Aadhaar**: `1234 5678 9012` $\rightarrow$ `[REDACTED AADHAAR]`
   - **Card Number**: `4532 1111 2222 4521` $\rightarrow$ `•••• •••• •••• 4521`
   - **Email**: `customer@nexbank.in` $\rightarrow$ `c***r@nexbank.in`

3. **Prompt Injection & Jailbreak Defense**: Blocks instructions attempting DAN mode, system prompt extraction, or instruction overrides (`"Ignore previous instructions"`).

4. **Account Lockdown Protocol**: Blocks state modifications (card block, PIN reset, transfer) unless customer identity is authenticated via JWT token.

5. **Confirmation-Before-Action Gate**: Enforces affirmative turn verification (`"YES"`, `"CONFIRM"`) before modifying account or card status.

---

## 3. False Positive Mitigation Strategy

- **Context Sensitivity**: Security patterns require instruction override syntax, preventing false triggers on normal customer queries like `"Can you show me the system instructions for opening an FD?"`.
- **Latency Impact**: Guardrail evaluation overhead is capped under $10\text{ ms}$ using parallel regex string scanners.
