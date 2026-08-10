import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.core.config import settings


class ClassifiedIntent(BaseModel):
    intent_id: str
    primary_category: str
    secondary_category: str
    tertiary_category: str
    confidence: float
    is_ambiguous: bool = False
    alternative_intents: List[Dict[str, Any]] = []


INTENT_TAXONOMY: Dict[str, Dict[str, Any]] = {
    # Account Management Intents
    "ACC-001": {
        "primary": "account",
        "secondary": "account_info",
        "tertiary": "balance_check",
        "keywords": ["balance", "account balance", "how much money", "kitna balance", "available balance", "savings balance", "kitna paisa", "savings account balance"],
        "required_auth": "OTP_VERIFIED"
    },
    "ACC-002": {
        "primary": "account",
        "secondary": "account_info",
        "tertiary": "statement_request",
        "keywords": ["statement", "account statement", "download statement", "bank statement", "e-statement", "passbook"],
        "required_auth": "OTP_VERIFIED"
    },
    "ACC-003": {
        "primary": "account",
        "secondary": "account_update",
        "tertiary": "update_contact",
        "keywords": ["change phone number", "update mobile", "update email", "change email", "contact details update"],
        "required_auth": "BIOMETRIC_VERIFIED"
    },
    "ACC-004": {
        "primary": "account",
        "secondary": "account_update",
        "tertiary": "update_address",
        "keywords": ["change address", "update address", "mailing address", "residential address update"],
        "required_auth": "BIOMETRIC_VERIFIED"
    },
    "ACC-005": {
        "primary": "account",
        "secondary": "account_closure",
        "tertiary": "closure_request",
        "keywords": ["close account", "close my account", "account closure", "terminate account"],
        "required_auth": "FULL_KYC"
    },
    "ACC-006": {
        "primary": "account",
        "secondary": "account_update",
        "tertiary": "nominee_update",
        "keywords": ["add nominee", "update nominee", "change nominee", "nomination details"],
        "required_auth": "FULL_KYC"
    },
    "ACC-007": {
        "primary": "account",
        "secondary": "account_update",
        "tertiary": "upgrade_downgrade",
        "keywords": ["upgrade account", "downgrade account", "change account type", "premium account upgrade"],
        "required_auth": "OTP_VERIFIED"
    },

    # Transaction & Payment Intents
    "TXN-001": {
        "primary": "transaction",
        "secondary": "transaction_status",
        "tertiary": "status_enquiry",
        "keywords": ["transaction status", "check payment", "did transaction go through", "status of transfer", "money sent status"],
        "required_auth": "OTP_VERIFIED"
    },
    "TXN-002": {
        "primary": "transaction",
        "secondary": "dispute",
        "tertiary": "raise_dispute",
        "keywords": ["dispute transaction", "wrong debit", "charged twice", "double deduction", "chargeback", "merchant error", "dispute charge", "unauthorized charge"],
        "required_auth": "OTP_VERIFIED"
    },
    "TXN-003": {
        "primary": "transaction",
        "secondary": "payment_issues",
        "tertiary": "upi_failure",
        "keywords": ["upi", "upi failed", "upi payment", "upi payment stuck", "upi transaction pending", "upi error", "gpay failed", "phonepe failed", "process nahi hua", "upi payment abhi tak"],
        "required_auth": "OTP_VERIFIED"
    },
    "TXN-004": {
        "primary": "transaction",
        "secondary": "payment_issues",
        "tertiary": "neft_rtgs_status",
        "keywords": ["neft status", "rtgs status", "neft delayed", "rtgs delayed", "imps pending"],
        "required_auth": "OTP_VERIFIED"
    },
    "TXN-005": {
        "primary": "transaction",
        "secondary": "recurring_payment",
        "tertiary": "auto_debit_setup",
        "keywords": ["auto debit", "cancel mandate", "setup recurring payment", "cancel auto debit", "e-mandate"],
        "required_auth": "BIOMETRIC_VERIFIED"
    },
    "TXN-006": {
        "primary": "transaction",
        "secondary": "international",
        "tertiary": "forex_enquiry",
        "keywords": ["international transfer", "send money abroad", "forex remittance", "swift transfer", "nre nro"],
        "required_auth": "FULL_KYC"
    },

    # Card Management Intents
    "CRD-001": {
        "primary": "card",
        "secondary": "card_action",
        "tertiary": "block_unblock",
        "keywords": ["block card", "unblock card", "lost debit card", "lost card", "block my card", "block my debit card", "stolen card", "freeze card", "lock card", "block it"],
        "required_auth": "OTP_VERIFIED"
    },
    "CRD-002": {
        "primary": "card",
        "secondary": "card_action",
        "tertiary": "replacement",
        "keywords": ["replace card", "card replacement", "damaged card", "reissue debit card"],
        "required_auth": "OTP_VERIFIED"
    },
    "CRD-003": {
        "primary": "card",
        "secondary": "credit_limit",
        "tertiary": "limit_change",
        "keywords": ["increase credit limit", "credit card limit", "limit enhancement", "decrease limit"],
        "required_auth": "BIOMETRIC_VERIFIED"
    },
    "CRD-004": {
        "primary": "card",
        "secondary": "emi",
        "tertiary": "emi_conversion",
        "keywords": ["convert to emi", "card emi", "transaction to emi", "split payment"],
        "required_auth": "OTP_VERIFIED"
    },
    "CRD-005": {
        "primary": "card",
        "secondary": "rewards",
        "tertiary": "points_enquiry",
        "keywords": ["reward points", "redeem rewards", "card cashback", "points balance"],
        "required_auth": "OTP_VERIFIED"
    },

    # Product & Advisory Intents
    "PRD-001": {
        "primary": "product",
        "secondary": "product_info",
        "tertiary": "general_info",
        "keywords": ["features", "benefits", "account types", "nexbank products"],
        "required_auth": "ANONYMOUS"
    },
    "PRD-002": {
        "primary": "product",
        "secondary": "loans",
        "tertiary": "eligibility_enquiry",
        "keywords": ["home loan eligibility", "personal loan interest rate", "loan emi calculator", "apply for loan"],
        "required_auth": "ANONYMOUS"
    },
    "PRD-003": {
        "primary": "product",
        "secondary": "deposits",
        "tertiary": "fd_rd_rates",
        "keywords": ["fd interest rates", "fixed deposit rates", "rd rates", "recurring deposit interest"],
        "required_auth": "ANONYMOUS"
    },
    "PRD-004": {
        "primary": "product",
        "secondary": "insurance",
        "tertiary": "policy_info",
        "keywords": ["term insurance", "health insurance cover", "insurance premium", "nexprotect"],
        "required_auth": "ANONYMOUS"
    },
    "PRD-005": {
        "primary": "product",
        "secondary": "advisory",
        "tertiary": "investment_recommendation",
        "keywords": ["where to invest", "should i invest", "should i put", "best investment option", "recommend investment", "which scheme is better", "fd or mutual funds", "invest in fd"],
        "required_auth": "ANONYMOUS"
    },

    # Complaint & Feedback Intents
    "CMP-001": {
        "primary": "complaint",
        "secondary": "grievance",
        "tertiary": "register_complaint",
        "keywords": ["register complaint", "file a complaint", "bad service", "raise grievance", "terrible bank"],
        "required_auth": "ANONYMOUS"
    },
    "CMP-002": {
        "primary": "complaint",
        "secondary": "grievance",
        "tertiary": "complaint_status",
        "keywords": ["complaint status", "check grievance status", "ticket status", "cmp-"],
        "required_auth": "ANONYMOUS"
    },
    "CMP-003": {
        "primary": "complaint",
        "secondary": "escalation",
        "tertiary": "escalate_issue",
        "keywords": ["escalate complaint", "speak to manager", "not resolved for weeks", "banking ombudsman"],
        "required_auth": "ANONYMOUS"
    },
    "CMP-004": {
        "primary": "complaint",
        "secondary": "feedback",
        "tertiary": "provide_feedback",
        "keywords": ["give feedback", "suggestion", "app feedback", "service review"],
        "required_auth": "ANONYMOUS"
    },
    "CMP-005": {
        "primary": "complaint",
        "secondary": "escalation",
        "tertiary": "supervisor_callback",
        "keywords": ["call me back", "supervisor callback", "manager call", "talk to human"],
        "required_auth": "ANONYMOUS"
    },

    # Security & Fraud Intents
    "SEC-001": {
        "primary": "security",
        "secondary": "fraud",
        "tertiary": "report_fraud",
        "keywords": ["unauthorized charge", "unauthorized transaction", "stole my details", "fraud", "stole my money", "money stolen", "hacked", "card stolen", "fraudulent charge", "someone stole"],
        "required_auth": "ANONYMOUS"
    },
    "SEC-002": {
        "primary": "security",
        "secondary": "phishing",
        "tertiary": "report_phishing",
        "keywords": ["phishing", "fake message", "scam call", "suspicious email", "otp scam"],
        "required_auth": "ANONYMOUS"
    },
    "SEC-003": {
        "primary": "security",
        "secondary": "credentials",
        "tertiary": "reset_credentials",
        "keywords": ["forgot password", "reset pin", "forgot netbanking password", "change pin"],
        "required_auth": "OTP_VERIFIED"
    },
    "SEC-004": {
        "primary": "security",
        "secondary": "suspicious_activity",
        "tertiary": "suspicious_response",
        "keywords": ["suspicious login", "unknown device", "unrecognized login alert"],
        "required_auth": "ANONYMOUS"
    }
}


class HierarchicalIntentClassifier:
    """
    3-Tier Hierarchical NLU Classifier enforcing confidence thresholds and disambiguation detection.
    """
    def classify(self, text: str) -> ClassifiedIntent:
        lower_text = text.lower().strip()

        scores: Dict[str, float] = {}
        for intent_id, meta in INTENT_TAXONOMY.items():
            score = 0.0
            for kw in meta["keywords"]:
                if kw in lower_text:
                    score += 0.45 + (len(kw) / 100.0)
            
            # Additional heuristic combinations for Card Actions
            if intent_id == "CRD-001" and ("block" in lower_text or "lost" in lower_text) and ("card" in lower_text or "debit" in lower_text):
                score += 0.50
            if intent_id == "SEC-001" and ("stole" in lower_text or "unauthorized" in lower_text or "fraud" in lower_text):
                score += 0.50

            scores[intent_id] = round(min(score, 0.98), 2)

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_intent_id, top_score = sorted_scores[0]

        if top_score < 0.25:
            return ClassifiedIntent(
                intent_id="OUT_OF_SCOPE",
                primary_category="general",
                secondary_category="out_of_scope",
                tertiary_category="unrecognized",
                confidence=0.10,
                is_ambiguous=False,
                alternative_intents=[]
            )

        meta = INTENT_TAXONOMY[top_intent_id]
        second_intent_id, second_score = sorted_scores[1]

        is_ambiguous = (top_score - second_score) < 0.15 and second_score > 0.40
        alternative_intents = [
            {"intent_id": k, "score": v, "primary": INTENT_TAXONOMY[k]["primary"]}
            for k, v in sorted_scores[1:4] if v > 0.30
        ]

        return ClassifiedIntent(
            intent_id=top_intent_id,
            primary_category=meta["primary"],
            secondary_category=meta["secondary"],
            tertiary_category=meta["tertiary"],
            confidence=top_score,
            is_ambiguous=is_ambiguous,
            alternative_intents=alternative_intents
        )
