# 🎨 Architecture Diagrams & Visual Specifications

**Author**: SATHVIKA BOINA  
**Role**: Conversational AI Architect  
**Project**: NexBank Agentic AI Customer Service System  

---

## 1. NLU Intent Classification & Entity Extraction Pipeline

```mermaid
flowchart LR
    A[Raw Customer Input] --> B[PII & PCI Redaction Scrubber]
    B --> C[Language & Sentiment Analyzer]
    C --> D[Regex & Keyword Rule Heuristic]
    D --> E[Semantic Vector Cosine Classifier]
    E --> F[Hierarchical Intent Mapper]
    F --> G{Confidence >= 0.60?}
    G -- Yes --> H[Dialogue State Tracker]
    G -- No --> I[Disambiguation Clarification Probe]
```

---

## 2. Hybrid RAG Retrieval Engine

```mermaid
flowchart TD
    A[Query Intent & Keywords] --> B[ChromaDB Dense Search 0.6]
    A --> C[BM25 Sparse Term Search 0.4]
    B --> D[Candidate Score Aggregator]
    C --> D
    D --> E[Cross-Encoder Re-Ranker]
    E --> F[Context Ingestion to Workflow]
```

---

## 3. Human Escalation Handoff State Machine

```mermaid
stateDiagram-v2
    [*] --> MonitoringTurn
    MonitoringTurn --> EvaluateTriggers
    EvaluateTriggers --> NormalTurn: No Trigger Hit
    EvaluateTriggers --> TriggerHit: Trigger TRG-001..015
    TriggerHit --> DetermineSLA: P1/P2/P3 Priority
    DetermineSLA --> SerializeHandoffPackage
    SerializeHandoffPackage --> RouteToSupportQueue
    RouteToSupportQueue --> HumanAgentAssigned
    HumanAgentAssigned --> ResolutionComplete
    ResolutionComplete --> [*]
```
