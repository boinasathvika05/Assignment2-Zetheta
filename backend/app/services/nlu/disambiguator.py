from typing import Dict, Any, Optional
from pydantic import BaseModel


class DisambiguationResult(BaseModel):
    is_disambiguated: bool
    resolved_intent_id: Optional[str] = None
    clarifying_question: Optional[str] = None
    probe_type: Optional[str] = None


CONFUSED_PAIRS: Dict[str, Dict[str, Any]] = {
    "TXN-001_vs_TXN-002": {
        "intents": ["TXN-001", "TXN-002"],
        "description": "Status check vs Transaction dispute",
        "probe": "Are you checking the processing status of a payment, or do you want to report an incorrect/unauthorized debit?",
        "keywords_a": ["status", "where is", "pending", "track"],
        "keywords_b": ["dispute", "wrong charge", "refund", "stolen", "unauthorized"]
    },
    "PRD-001_vs_PRD-005": {
        "intents": ["PRD-001", "PRD-005"],
        "description": "Product information vs Personalised financial advice",
        "probe": "I can share factual details about our Fixed Deposit rates and Mutual Fund options. Are you looking for product features, or would you like to speak with an advisor for investment advice?",
        "keywords_a": ["rate", "interest rate", "features", "tenure"],
        "keywords_b": ["should i", "which is better", "recommend", "where to invest"]
    },
    "ACC-003_vs_ACC-004": {
        "intents": ["ACC-003", "ACC-004"],
        "description": "Contact details update vs Mailing address update",
        "probe": "Would you like to update your registered mobile number/email, or change your postal mailing address?",
        "keywords_a": ["mobile", "phone", "email"],
        "keywords_b": ["address", "house", "street", "city", "pincode"]
    },
    "CMP-001_vs_CMP-003": {
        "intents": ["CMP-001", "CMP-003"],
        "description": "New complaint registration vs Escalating existing complaint",
        "probe": "Are you registering a new complaint, or escalating an existing open complaint reference number?",
        "keywords_a": ["new complaint", "file complaint", "bad service"],
        "keywords_b": ["escalate", "existing complaint", "pending for days", "cmp-"]
    },
    "SEC-001_vs_TXN-002": {
        "intents": ["SEC-001", "TXN-002"],
        "description": "Fraud report vs Merchant billing dispute",
        "probe": "Did someone steal your card details without your knowledge (Fraud), or is this a wrong billing amount with a merchant you transacted with (Dispute)?",
        "keywords_a": ["stolen card", "fraud", "never transacted", "hacked"],
        "keywords_b": ["merchant", "charged twice", "wrong amount", "swiggy", "amazon"]
    },
    "CRD-001_vs_SEC-001": {
        "intents": ["CRD-001", "SEC-001"],
        "description": "Routine card block vs Fraud incident report",
        "probe": "Would you like to temporarily block your card for safety, or report an active fraudulent transaction?",
        "keywords_a": ["temp block", "misplaced card", "freeze card"],
        "keywords_b": ["fraud", "unauthorized", "money stolen"]
    }
}


class IntentDisambiguator:
    """
    Disambiguation Engine resolving overlapping intent pairs with targeted probe sequences.
    """
    def resolve_or_probe(self, intent_a: str, intent_b: str, text: str) -> DisambiguationResult:
        lower_text = text.lower()
        pair_key = None

        for key, meta in CONFUSED_PAIRS.items():
            if intent_a in meta["intents"] and intent_b in meta["intents"]:
                pair_key = key
                break

        if not pair_key:
            return DisambiguationResult(
                is_disambiguated=True,
                resolved_intent_id=intent_a
            )

        meta = CONFUSED_PAIRS[pair_key]

        # Try resolving using exact intent-specific keywords
        matches_a = sum(1 for kw in meta["keywords_a"] if kw in lower_text)
        matches_b = sum(1 for kw in meta["keywords_b"] if kw in lower_text)

        if matches_a > matches_b:
            return DisambiguationResult(is_disambiguated=True, resolved_intent_id=meta["intents"][0])
        elif matches_b > matches_a:
            return DisambiguationResult(is_disambiguated=True, resolved_intent_id=meta["intents"][1])
        else:
            # Need to issue a clarifying probe to the customer
            return DisambiguationResult(
                is_disambiguated=False,
                clarifying_question=meta["probe"],
                probe_type=pair_key
            )
