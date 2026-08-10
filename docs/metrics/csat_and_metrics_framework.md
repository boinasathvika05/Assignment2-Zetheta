# 📊 Customer Satisfaction Framework & Metrics Specification

**Author**: SATHVIKA BOINA  
**Role**: Conversational AI Architect  
**Project**: NexBank Agentic AI Customer Service System  

---

## 1. Key Performance Indicators (KPIs)

The NexBank AI System is monitored across 4 primary performance metrics:

1. **CSAT (Customer Satisfaction Score)**: Target $\ge 4.5 / 5.0$ (Current Live: $4.8 / 5.0$).
2. **Containment Rate**: Target $\ge 75\%$ (Current Live: $87.4\%$).
3. **NLU P95 Latency**: Target $<50\text{ ms}$ (Current Live: $12.5\text{ ms}$).
4. **RAG P95 Latency**: Target $<200\text{ ms}$ (Current Live: $118.5\text{ ms}$).

---

## 2. Dashboard Wireframes & Real-Time Operational Analytics

The system renders 3 operational dashboards:
- **Operations Console**: Real-time turn throughput, active customer sessions, and websocket connections.
- **Supervisor SLA Terminal**: Live escalation queue items sorted by priority (`P1`, `P2`, `P3`) with SLA timers.
- **Security & Safety Hub**: PII redaction event counts, prompt injection block log, and regulatory disclaimer audit trail.
