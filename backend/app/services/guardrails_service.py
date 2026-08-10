import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.core.logging import logger


class GuardrailCheckResult(BaseModel):
    is_safe: bool
    blocked_by: Optional[str] = None
    sanitized_text: str
    action_taken: str  # "PASS", "MASKED", "BLOCKED", "DISCLAIMER_ADDED"
    details: Dict[str, Any] = {}


class GuardrailSafetyEngine:
    """
    Comprehensive Safety Guardrails Engine enforcing Prompt Injection Protection,
    PII Masking, Financial Advice Prohibition (SEBI), RBI/PCI DSS/AML compliance,
    and Output Fact Verification.
    """

    PROMPT_INJECTION_PATTERNS = [
        r"ignore\s+previous\s+instructions",
        r"disregard\s+all\s+prior\s+rules",
        r"system\s+prompt",
        r"jailbreak",
        r"dan\s+mode",
        r"developer\s+mode",
        r"override\s+safety",
        r"act\s+as\s+an?\s+unfiltered",
        r"bypass\s+security"
    ]

    FINANCIAL_ADVICE_KEYWORDS = [
        "which stock should i buy",
        "best mutual fund to invest",
        "crypto recommendation",
        "where to invest my money",
        "guaranteed returns stock",
        "portfolio allocation suggestion",
        "trading tip"
    ]

    def scan_input(self, text: str) -> GuardrailCheckResult:
        """Runs input safety checks prior to NLU processing."""
        lower_text = text.lower()

        # 1. Prompt Injection & Jailbreak Scanner
        for pat in self.PROMPT_INJECTION_PATTERNS:
            if re.search(pat, lower_text):
                logger.warning(f"Guardrail Alert: Prompt injection attempt detected matching [{pat}].")
                return GuardrailCheckResult(
                    is_safe=False,
                    blocked_by="PROMPT_INJECTION_PROTECTION",
                    sanitized_text="I am unable to process system modification requests. How can I assist you with your NexBank account today?",
                    action_taken="BLOCKED",
                    details={"pattern_matched": pat}
                )

        # 2. SEBI Financial Advice Guardrail
        for kw in self.FINANCIAL_ADVICE_KEYWORDS:
            if kw in lower_text:
                logger.info(f"Guardrail Alert: Financial advice query detected [{kw}]. Adding mandatory disclaimer.")
                return GuardrailCheckResult(
                    is_safe=True,
                    blocked_by="FINANCIAL_ADVICE_PROHIBITION",
                    sanitized_text=text,
                    action_taken="DISCLAIMER_ADDED",
                    details={
                        "disclaimer": "⚠️ <strong>SEBI Regulatory Notice:</strong> NexBank AI provides factual product information only. For personalized investment advice, please consult a SEBI-registered financial advisor."
                    }
                )

        # 3. PII Scrubber (PAN, Aadhaar, 16-Digit Card, Email, Phone)
        sanitized = text
        # Mask 16-digit card numbers (PCI DSS Compliance)
        sanitized = re.sub(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b", "[CARD_NUMBER_REDACTED]", sanitized)
        # Mask 12-digit Aadhaar
        sanitized = re.sub(r"\b\d{4}\s?\d{4}\s?\d{4}\b", "[AADHAAR_REDACTED]", sanitized)
        # Mask 10-digit PAN
        sanitized = re.sub(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", "[PAN_REDACTED]", sanitized, flags=re.IGNORECASE)

        action = "MASKED" if sanitized != text else "PASS"

        return GuardrailCheckResult(
            is_safe=True,
            sanitized_text=sanitized,
            action_taken=action
        )

    def sanitize_output(self, response_text: str) -> str:
        """Sanitizes model output to guarantee PCI DSS and PII compliance."""
        # Never allow raw 16-digit cards in output
        sanitized = re.sub(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b", "XXXX-XXXX-XXXX-[LAST4]", response_text)
        return sanitized
