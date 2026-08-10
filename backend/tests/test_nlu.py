import pytest
from app.services.nlu_service import NLUPipelineService


@pytest.mark.asyncio
async def test_nlu_intent_classification_balance():
    pipeline = NLUPipelineService()
    res = pipeline.process("Hi, I want to check my savings account balance")
    assert res.intent.intent_id == "ACC-001"
    assert res.intent.primary_category == "account"
    assert res.intent.confidence >= 0.70


@pytest.mark.asyncio
async def test_nlu_intent_classification_fraud():
    pipeline = NLUPipelineService()
    res = pipeline.process("I see an unauthorized charge of 15000 on my card, someone stole my details!")
    assert res.intent.intent_id == "SEC-001"
    assert res.intent.primary_category == "security"
    assert res.sentiment_language.primary_emotion in ["anger", "frustration", "urgency"]


@pytest.mark.asyncio
async def test_nlu_entity_extraction_pan_and_upi():
    pipeline = NLUPipelineService()
    res = pipeline.process("My PAN is ABCDE1234F and UPI ID is user@okaxis")
    entity_types = [e.entity_type for e in res.entities]
    assert "pan_number" in entity_types
    assert "upi_id" in entity_types


@pytest.mark.asyncio
async def test_nlu_entity_extraction_card_last4():
    pipeline = NLUPipelineService()
    res = pipeline.process("Please block my debit card ending in 4521")
    entity_types = [e.entity_type for e in res.entities]
    assert "card_last4" in entity_types
    card_ent = next(e for e in res.entities if e.entity_type == "card_last4")
    assert card_ent.value == "4521"


@pytest.mark.asyncio
async def test_nlu_hinglish_code_switching():
    pipeline = NLUPipelineService()
    res = pipeline.process("Hello, mera kal ka UPI payment abhi tak process nahi hua. Kya hua iske saath?")
    assert res.sentiment_language.detected_language == "Hinglish"
    assert res.sentiment_language.is_code_switching is True
    assert res.intent.intent_id == "TXN-003"


@pytest.mark.asyncio
async def test_nlu_disambiguation_info_vs_advisory():
    pipeline = NLUPipelineService()
    res = pipeline.process("Should I put my 5 lakhs in FD or mutual funds?")
    assert res.intent.intent_id == "PRD-005"
    assert res.intent.primary_category == "product"
