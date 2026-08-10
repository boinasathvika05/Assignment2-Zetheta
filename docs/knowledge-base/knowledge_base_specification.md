# 📚 Knowledge Base & Hybrid RAG Retrieval Specification

**Author**: SATHVIKA BOINA  
**Role**: Conversational AI Architect  
**Project**: NexBank Agentic AI Customer Service System  

---

## 1. Knowledge Base Architecture

The NexBank Knowledge Base manages authoritative banking documents, DICGC insurance guidelines, RBI regulatory circulars, and product terms.

```
Knowledge Base Architecture
├── Dense Vector Index (ChromaDB) ── Weight 0.6
├── Sparse Term Index (BM25) ──────── Weight 0.4
└── Cross-Encoder Re-Ranker ──────── Max Candidates: 5 (Score Threshold: 0.72)
```

---

## 2. Sample Ingested Knowledge Base Entries

### KB Entry 1: DICGC Deposit Insurance Coverage
- **Category**: `REGULATORY`
- **Topic**: Deposit Protection Rules
- **Content**: All savings accounts, fixed deposits, current accounts, and recurring deposits at NexBank are insured up to ₹5,00,000 (Rupees Five Lakhs) per depositor under the Deposit Insurance and Credit Guarantee Corporation (DICGC) Act.
- **Reference**: RBI/2020-21/11 DICGC Guidelines.

### KB Entry 2: Zero-Liability Fraud Dispute Policy
- **Category**: `SECURITY`
- **Topic**: Unauthorized Card Transactions
- **Content**: Per RBI circular on Limited Liability of Customers in Unauthorized Electronic Banking Transactions, a customer has ZERO liability if unauthorized fraud is reported within 3 working days of receiving the SMS/email alert.
- **Reference**: RBI/2017-18/15 DBR.No.Leg.BC.78/09.07.005/2017-18.

### KB Entry 3: Senior Citizen FD Rates
- **Category**: `PRODUCTS`
- **Topic**: Fixed Deposit Interest Rates
- **Content**: NexBank offers 7.75% p.a. for Senior Citizens (60 years and above) on Fixed Deposits of 1-year to 3-year tenures, providing an additional 0.50% premium over standard rates.

---

## 3. Knowledge Maintenance & RBI Circular Ingestion Workflow

1. **Upload & Chunking**: Regulatory circulars ingested as Markdown and split into 512-token chunks with 50-token overlap.
2. **Review Chain**: Draft entries assigned `PENDING_REVIEW` until validated by a `RISK_OFFICER`.
3. **Approval & Embedding**: Approved documents embedded via SentenceTransformers and indexed into ChromaDB.
