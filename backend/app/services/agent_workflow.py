import time
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.schemas.dialogue import DialogueState
from app.services.nlu_service import NLUPipelineService, NLUPipelineResult
from app.services.banking_service import MockBankingCoreService, BankingActionResult
from app.services.guardrails_service import GuardrailSafetyEngine, GuardrailCheckResult
from app.services.escalation_service import EscalationRouterService, EscalationCheckResult
from app.core.logging import logger


class AgentWorkflowOutput(BaseModel):
    action_type: str  # "respond", "clarify", "confirm", "escalate", "blocked"
    response_text: str
    updated_state: DialogueState
    banking_action_result: Optional[BankingActionResult] = None
    escalation_check: Optional[EscalationCheckResult] = None


class NexBankAgenticWorkflow:
    """
    Dialogue Manager and Agent Workflow Engine executing multi-turn reasoning,
    context carry-over, clarification flows, confirmation-before-action rules,
    safety guardrails, escalation triggers, and live banking profile data integration.
    """
    def __init__(self):
        self.nlu = NLUPipelineService()
        self.banking_core = MockBankingCoreService()
        self.guardrails = GuardrailSafetyEngine()
        self.escalation_router = EscalationRouterService()

    def process_agent_turn(
        self,
        state: DialogueState,
        user_text: str,
        customer_profile: Optional[Dict[str, Any]] = None
    ) -> AgentWorkflowOutput:
        start_time = time.time()

        # Update Dialogue State slots with live customer profile inputs if provided
        if customer_profile:
            state.slots.update(customer_profile)
            if customer_profile.get("accNum"):
                state.slots["account_id"] = customer_profile.get("accNum")
            if customer_profile.get("cardNum"):
                card_num = customer_profile.get("cardNum")
                state.slots["card_last4"] = card_num[-4:] if len(card_num) >= 4 else "4521"

        # 1. Run Safety Guardrail Input Inspection (Module 8)
        guardrail_res: GuardrailCheckResult = self.guardrails.scan_input(user_text)
        if not guardrail_res.is_safe:
            return AgentWorkflowOutput(
                action_type="blocked",
                response_text=guardrail_res.sanitized_text,
                updated_state=state
            )

        sanitized_input = guardrail_res.sanitized_text
        lower_input = sanitized_input.lower().strip()

        # 2. Run NLU Pipeline
        nlu_res: NLUPipelineResult = self.nlu.process(text=sanitized_input, current_slots=state.slots)

        # 3. Context Carry-over & Confirmation / Clarification Turn Handler:
        previous_intent = state.current_intent
        is_user_affirming = any(aff in lower_input for aff in ["yes", "confirm", "proceed", "sure", "haan", "correct", "yep", "do it"])

        if (nlu_res.intent.intent_id == "OUT_OF_SCOPE" or nlu_res.intent.confidence < 0.60) and previous_intent and previous_intent != "OUT_OF_SCOPE":
            extracted_entities = self.nlu.extractor.extract_all(sanitized_input)
            matched_entity = next((e for e in extracted_entities if e.entity_type in ["account_id", "card_last4", "complaint_id", "transaction_id", "transaction_amount"]), None)
            
            if is_user_affirming or matched_entity or sanitized_input.strip().isdigit():
                logger.info(f"Context Carry-over Turn Answer Detected! Restoring intent [{previous_intent}].")
                nlu_res.intent.intent_id = previous_intent
                nlu_res.intent.confidence = 0.98
                if matched_entity:
                    state.slots[matched_entity.entity_type] = matched_entity.value
                elif sanitized_input.strip().isdigit():
                    state.slots["account_id"] = sanitized_input.strip()

        # State Memory & Context Updates
        state.current_intent = nlu_res.intent.intent_id
        state.intent_confidence = nlu_res.intent.confidence
        state.alternative_intents = nlu_res.intent.alternative_intents
        state.slots.update(nlu_res.slot_status["slots"])
        state.sentiment_trajectory.append(nlu_res.sentiment_language.sentiment_score)

        # Append to 20-turn history buffer
        turn_item = {
            "turn_index": len(state.history_buffer) + 1,
            "user": user_text,
            "intent": nlu_res.intent.intent_id,
            "sentiment": nlu_res.sentiment_language.sentiment_score
        }
        state.history_buffer.append(turn_item)
        if len(state.history_buffer) > 20:
            state.history_buffer = state.history_buffer[-20:]

        # 4. Run Escalation Router (Module 9 - 15 Triggers)
        esc_check: EscalationCheckResult = self.escalation_router.evaluate_escalation(
            state=state,
            user_text=user_text,
            nlu_confidence=nlu_res.intent.confidence,
            sentiment_score=nlu_res.sentiment_language.sentiment_score
        )
        if esc_check.should_escalate and nlu_res.intent.confidence < 0.60:
            state.escalation_proximity = 1.0
            return AgentWorkflowOutput(
                action_type="escalate",
                response_text=f"⚠️ Your inquiry requires specialized assistance ({esc_check.reason}). Routing to live [{esc_check.target_queue}] support agent (Priority: {esc_check.priority}, SLA: {esc_check.sla_minutes} mins).",
                updated_state=state,
                escalation_check=esc_check
            )

        # 5. Check Clarification Flow (Ambiguity or Missing Required Slots)
        if not nlu_res.disambiguation.is_disambiguated:
            return AgentWorkflowOutput(
                action_type="clarify",
                response_text=nlu_res.disambiguation.clarifying_question,
                updated_state=state
            )

        # Compute missing slots considering filled state
        missing = [s for s in self.nlu.slot_manager.REQUIRED_SLOTS.get(state.current_intent, []) if s not in state.slots or not state.slots[s]]
        if missing:
            missing_slot = missing[0].replace("_", " ")
            return AgentWorkflowOutput(
                action_type="clarify",
                response_text=f"Could you please specify your {missing_slot} so I can assist you with your request?",
                updated_state=state
            )

        # 6. Check Confirmation-Before-Action Flow for High-Stakes Account Modifications
        high_stakes_intents = ["ACC-005", "ACC-006", "CRD-001", "TXN-002"]
        
        if state.current_intent in high_stakes_intents and not is_user_affirming:
            action_desc = "block your debit card" if state.current_intent == "CRD-001" else "proceed with this account modification"
            return AgentWorkflowOutput(
                action_type="confirm",
                response_text=f"⚠️ <strong>Confirmation Required:</strong> Are you sure you want to {action_desc}? Please reply 'YES' to proceed.",
                updated_state=state
            )

        # 7. Execute Banking Workflows using Live Customer Profile Data
        banking_result: Optional[BankingActionResult] = None
        intent = state.current_intent

        if intent == "ACC-001":
            banking_result = self.banking_core.check_balance(state.customer_id, profile=state.slots)
        elif intent == "ACC-002":
            banking_result = self.banking_core.request_statement(state.customer_id, profile=state.slots)
        elif intent == "CRD-001":
            card_last4 = state.slots.get("card_last4", "4521")
            banking_result = self.banking_core.block_card(state.customer_id, card_last4=card_last4, profile=state.slots)
        elif intent == "CRD-002":
            card_last4 = state.slots.get("card_last4", "4521")
            banking_result = self.banking_core.replace_card(state.customer_id, card_last4=card_last4, profile=state.slots)
        elif intent == "CMP-001":
            banking_result = self.banking_core.register_complaint(state.customer_id, issue_description=user_text, profile=state.slots)
        elif intent == "CMP-002":
            cmp_id = state.slots.get("complaint_id", "CMP-2024-78901")
            banking_result = self.banking_core.check_complaint_status(complaint_id=cmp_id, profile=state.slots)
        elif intent == "TXN-002":
            amount = state.slots.get("transaction_amount", 15000.0)
            banking_result = self.banking_core.dispute_transaction(state.customer_id, transaction_id="TXN98721", amount=amount, reason=user_text, profile=state.slots)
        elif intent == "TXN-003":
            upi_ref = state.slots.get("upi_ref", "UPI123456789")
            banking_result = self.banking_core.resolve_upi_issue(upi_ref=upi_ref, amount=2500.0, profile=state.slots)
        elif intent == "PRD-002":
            banking_result = self.banking_core.check_loan_eligibility(loan_type="Personal Loan", profile=state.slots)
        elif intent in ["PRD-001", "PRD-003", "PRD-004"]:
            banking_result = self.banking_core.get_product_info(product_name="NexSave Savings", profile=state.slots)

        response_text = banking_result.user_message if banking_result else f"Processed your request for [{intent}]."

        # Add SEBI Disclaimer if financial advice flag was triggered
        if guardrail_res.action_taken == "DISCLAIMER_ADDED" and "disclaimer" in guardrail_res.details:
            response_text += f"\n\n{guardrail_res.details['disclaimer']}"

        # 8. Output PCI DSS & PII Sanitization
        sanitized_response = self.guardrails.sanitize_output(response_text)

        return AgentWorkflowOutput(
            action_type="respond",
            response_text=sanitized_response,
            updated_state=state,
            banking_action_result=banking_result
        )
