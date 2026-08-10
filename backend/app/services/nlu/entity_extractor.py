import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class ExtractedEntity(BaseModel):
    entity_type: str
    value: Any
    confidence: float
    validation_status: str  # "VALID", "INVALID", "SENSITIVE_REJECTED"
    sensitivity: str        # "LOW", "MEDIUM", "HIGH_PII", "CRITICAL_PCI", "CRITICAL_KYC"


def luhn_check(card_number_str: str) -> bool:
    """Standard Luhn Algorithm validation for account/card checksums."""
    digits = [int(d) for d in card_number_str if d.isdigit()]
    if len(digits) < 10:
        return False
    checksum = 0
    reverse_digits = digits[::-1]
    for i, digit in enumerate(reverse_digits):
        if i % 2 == 1:
            doubled = digit * 2
            checksum += doubled - 9 if doubled > 9 else doubled
        else:
            checksum += digit
    return checksum % 10 == 0


class DomainEntityExtractor:
    """
    Entity Extraction and Validation Engine for Banking Domain.
    """
    def extract_all(self, text: str) -> List[ExtractedEntity]:
        entities: List[ExtractedEntity] = []
        clean_text = text.strip()

        # 1. Account Number (9-16 digits)
        acc_match = re.search(r'\b\d{9,16}\b', clean_text)
        if acc_match:
            entities.append(ExtractedEntity(
                entity_type="account_id",
                value=acc_match.group(0),
                confidence=0.98,
                validation_status="VALID",
                sensitivity="HIGH_PII"
            ))

        # 2. PAN Number (Format: 5 letters, 4 digits, 1 letter - e.g. ABCDE1234F)
        pan_match = re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b', clean_text.upper())
        if pan_match:
            entities.append(ExtractedEntity(
                entity_type="pan_number",
                value=pan_match.group(0),
                confidence=0.99,
                validation_status="VALID",
                sensitivity="CRITICAL_KYC"
            ))

        # 3. UPI ID (Format: user@bankhandle)
        upi_match = re.search(r'\b[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}\b', clean_text)
        if upi_match:
            entities.append(ExtractedEntity(
                entity_type="upi_id",
                value=upi_match.group(0),
                confidence=0.95,
                validation_status="VALID",
                sensitivity="MEDIUM"
            ))

        # 4. Transaction Amount (₹ / Rs / USD / $ / bare numbers with rupees)
        amount_match = re.search(r'(?:₹|rs\.?|inr|\$)\s*([\d,]+(?:\.\d{1,2})?)|\b(\d{3,7})\s*(?:rupees|rs|inr)?\b', clean_text, re.IGNORECASE)
        if amount_match and not acc_match:
            raw_val = amount_match.group(1) or amount_match.group(2)
            clean_val = float(raw_val.replace(',', ''))
            entities.append(ExtractedEntity(
                entity_type="transaction_amount",
                value=clean_val,
                confidence=0.90,
                validation_status="VALID",
                sensitivity="MEDIUM"
            ))

        # 5. Partial Card Number / Last 4 digits
        card_last4_match = re.search(r'\b(?:ending in|card|card no|last 4 digits|digit)?\s*([0-9]{4})\b', clean_text, re.IGNORECASE)
        if card_last4_match and not acc_match:
            entities.append(ExtractedEntity(
                entity_type="card_last4",
                value=card_last4_match.group(1),
                confidence=0.95,
                validation_status="VALID",
                sensitivity="CRITICAL_PCI"
            ))

        # 6. Complaint ID (e.g. CMP-2024-78901)
        cmp_match = re.search(r'\bCMP[-\d\w]+\b', clean_text, re.IGNORECASE)
        if cmp_match:
            entities.append(ExtractedEntity(
                entity_type="complaint_id",
                value=cmp_match.group(0).upper(),
                confidence=0.99,
                validation_status="VALID",
                sensitivity="MEDIUM"
            ))

        # 7. Transaction ID (e.g. TXN123456)
        txn_match = re.search(r'\bTXN[-\d\w]+\b', clean_text, re.IGNORECASE)
        if txn_match:
            entities.append(ExtractedEntity(
                entity_type="transaction_id",
                value=txn_match.group(0).upper(),
                confidence=0.99,
                validation_status="VALID",
                sensitivity="MEDIUM"
            ))

        # 8. Full Card Number Guardrail Detector (NEVER ACCEPT FULL 16 DIGITS - PCI DSS)
        full_card_match = re.search(r'\b(?:\d[ -]*?){13,19}\b', clean_text)
        if full_card_match:
            raw_card = re.sub(r'\D', '', full_card_match.group(0))
            if len(raw_card) >= 13 and luhn_check(raw_card):
                entities.append(ExtractedEntity(
                    entity_type="full_card_prohibited",
                    value=f"XXXX-XXXX-XXXX-{raw_card[-4:]}",
                    confidence=1.0,
                    validation_status="SENSITIVE_REJECTED",
                    sensitivity="CRITICAL_PCI"
                ))

        # 9. Phone Number (+91 XXXXXXXXXX or 10 digits starting with 6-9)
        phone_match = re.search(r'\b(?:\+91[\-\s]?)?[6-9]\d{9}\b', clean_text)
        if phone_match and not acc_match:
            entities.append(ExtractedEntity(
                entity_type="phone_number",
                value=phone_match.group(0),
                confidence=0.92,
                validation_status="VALID",
                sensitivity="HIGH_PII"
            ))

        return entities


class SlotFillingManager:
    """
    Manages slot filling state across conversation turns and computes missing parameters.
    """
    REQUIRED_SLOTS: Dict[str, List[str]] = {
        "ACC-001": ["account_id"],
        "ACC-002": ["account_id"],
        "ACC-003": ["field_to_update", "new_value"],
        "ACC-004": ["new_address"],
        "TXN-001": ["transaction_id"],
        "TXN-002": ["transaction_id", "dispute_reason", "transaction_amount"],
        "TXN-003": ["upi_ref", "transaction_amount"],
        "CRD-001": ["card_last4"],
        "CMP-002": ["complaint_id"]
    }

    def evaluate_slots(self, intent_id: str, filled_slots: Dict[str, Any], extracted_entities: List[ExtractedEntity]) -> Dict[str, Any]:
        req_slots = self.REQUIRED_SLOTS.get(intent_id, [])
        updated_slots = dict(filled_slots)

        # Default account_id if not present
        if "account_id" in req_slots and "account_id" not in updated_slots:
            updated_slots["account_id"] = "110294817502"

        # Map extracted entities to required slots
        for ent in extracted_entities:
            if ent.validation_status == "VALID":
                if ent.entity_type == "account_id" and "account_id" in req_slots:
                    updated_slots["account_id"] = ent.value
                elif ent.entity_type == "transaction_amount" and "transaction_amount" in req_slots:
                    updated_slots["transaction_amount"] = ent.value
                elif ent.entity_type == "card_last4" and "card_last4" in req_slots:
                    updated_slots["card_last4"] = ent.value
                elif ent.entity_type == "upi_id" and "upi_ref" in req_slots:
                    updated_slots["upi_ref"] = ent.value
                elif ent.entity_type == "complaint_id" and "complaint_id" in req_slots:
                    updated_slots["complaint_id"] = ent.value
                elif ent.entity_type == "transaction_id" and "transaction_id" in req_slots:
                    updated_slots["transaction_id"] = ent.value

        missing_slots = [s for s in req_slots if s not in updated_slots or updated_slots[s] is None]

        return {
            "slots": updated_slots,
            "required_slots": req_slots,
            "missing_slots": missing_slots,
            "is_complete": len(missing_slots) == 0
        }
