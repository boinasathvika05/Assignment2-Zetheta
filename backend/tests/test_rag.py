import pytest
from app.services.rag.hybrid_retriever import HybridRAGRetriever


def test_bm25_and_hybrid_retrieval():
    retriever = HybridRAGRetriever()
    sample_docs = [
        {"id": "kb_1", "title": "NexSave Account", "category": "Product Info", "content": "NexSave Savings Account offers 4.5% annual interest with zero minimum balance requirement.", "format_type": "unstructured"},
        {"id": "kb_2", "title": "NexFD Interest Rates", "category": "Product Info", "content": "NexFD Fixed Deposit offers interest rates up to 7.25% for 10 year tenure.", "format_type": "unstructured"},
        {"id": "kb_3", "title": "Card Block Security", "category": "Security", "content": "To block your debit card, navigate to security settings or state card last 4 digits to AI agent.", "format_type": "unstructured"}
    ]
    retriever.index_documents(sample_docs)

    results = retriever.retrieve("What is the interest rate for savings account?", top_k=2)
    assert len(results) > 0
    assert results[0].kb_id == "kb_1"
    assert results[0].fusion_score > 0.0


def test_hybrid_retrieval_card_block():
    retriever = HybridRAGRetriever()
    sample_docs = [
        {"id": "kb_1", "title": "NexSave Account", "category": "Product Info", "content": "NexSave Savings Account offers 4.5% annual interest with zero minimum balance requirement.", "format_type": "unstructured"},
        {"id": "kb_3", "title": "Card Block Security", "category": "Security", "content": "To block your debit card, navigate to security settings or state card last 4 digits to AI agent.", "format_type": "unstructured"}
    ]
    retriever.index_documents(sample_docs)

    results = retriever.retrieve("block my card", top_k=1)
    assert len(results) > 0
    assert results[0].kb_id == "kb_3"
