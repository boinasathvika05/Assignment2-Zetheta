import time
import pytest
from app.services.nlu_service import NLUPipelineService
from app.services.rag.hybrid_retriever import HybridRAGRetriever


@pytest.mark.asyncio
async def test_nlu_processing_latency_budget():
    nlu = NLUPipelineService()
    # Warmup
    nlu.process("Warmup query")
    start = time.time()
    res = nlu.process("Check my savings account balance for ending 4521")
    latency_ms = (time.time() - start) * 1000

    assert res.intent.intent_id == "ACC-001"
    assert latency_ms < 200.0  # Sub-200ms NLU budget


@pytest.mark.asyncio
async def test_rag_retrieval_latency_budget():
    retriever = HybridRAGRetriever()
    sample_docs = [
        {"id": f"kb_{i}", "title": f"Doc {i}", "category": "Product Info", "content": f"NexBank product guidelines detailing feature #{i}", "format_type": "unstructured"}
        for i in range(50)
    ]
    retriever.index_documents(sample_docs)

    # Warmup query to exclude cold-start vector model loading
    retriever.retrieve("Warmup query", top_k=1)

    start = time.time()
    results = retriever.retrieve("NexBank product guidelines", top_k=5)
    latency_ms = (time.time() - start) * 1000

    assert len(results) > 0
    assert latency_ms < 15000.0  # CPU Hybrid RAG budget in test environment
