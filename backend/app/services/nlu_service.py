from typing import Dict, Any, List
from pydantic import BaseModel

from app.services.nlu.intent_classifier import HierarchicalIntentClassifier, ClassifiedIntent
from app.services.nlu.entity_extractor import DomainEntityExtractor, SlotFillingManager, ExtractedEntity
from app.services.nlu.disambiguator import IntentDisambiguator, DisambiguationResult
from app.services.nlu.sentiment_language import SentimentAndLanguageEngine, SentimentAnalysisResult


class NLUPipelineResult(BaseModel):
    text: str
    intent: ClassifiedIntent
    entities: List[ExtractedEntity]
    slot_status: Dict[str, Any]
    disambiguation: DisambiguationResult
    sentiment_language: SentimentAnalysisResult


class NLUPipelineService:
    """
    Unified NLU Pipeline orchestrating intent classification, entity extraction, slot filling,
    disambiguation, sentiment trajectory tracking, and Hinglish language detection.
    """
    def __init__(self):
        self.classifier = HierarchicalIntentClassifier()
        self.extractor = DomainEntityExtractor()
        self.slot_manager = SlotFillingManager()
        self.disambiguator = IntentDisambiguator()
        self.sentiment_engine = SentimentAndLanguageEngine()

    def process(self, text: str, current_slots: Dict[str, Any] = None) -> NLUPipelineResult:
        current_slots = current_slots or {}

        # 1. Intent Classification
        classified_intent = self.classifier.classify(text)

        # 2. Entity Extraction
        entities = self.extractor.extract_all(text)

        # 3. Slot Filling Check
        slot_status = self.slot_manager.evaluate_slots(
            intent_id=classified_intent.intent_id,
            filled_slots=current_slots,
            extracted_entities=entities
        )

        # 4. Disambiguation Check (if ambiguous or top alternatives exist)
        if classified_intent.is_ambiguous and classified_intent.alternative_intents:
            alt_id = classified_intent.alternative_intents[0]["intent_id"]
            disamb_res = self.disambiguator.resolve_or_probe(
                intent_a=classified_intent.intent_id,
                intent_b=alt_id,
                text=text
            )
        else:
            disamb_res = DisambiguationResult(
                is_disambiguated=True,
                resolved_intent_id=classified_intent.intent_id
            )

        # 5. Sentiment & Language Detection
        sentiment_res = self.sentiment_engine.analyze(text)

        return NLUPipelineResult(
            text=text,
            intent=classified_intent,
            entities=entities,
            slot_status=slot_status,
            disambiguation=disamb_res,
            sentiment_language=sentiment_res
        )
