import random
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.core.logging import logger


class BankingActionResult(BaseModel):
    action_type: str
    status: str  # "SUCCESS", "PENDING_AUTH", "ESCALATED", "FAILED"
    reference_number: str
    details: Dict[str, Any]
    user_message: str


class MockBankingCoreService:
    """
    Mock Core Banking Platform APIs handling secure banking workflows with Live Customer Profile Data.
    """
    def check_balance(self, customer_id: str, account_type: str = "savings", profile: Optional[Dict[str, Any]] = None) -> BankingActionResult:
        profile = profile or {}
        acc_num = profile.get("accNum") or profile.get("account_id") or "110294817502"
        acc_type = profile.get("accType") or "Savings Account"
        
        raw_bal = profile.get("accBal") or profile.get("balance")
        if raw_bal is not None:
            try:
                balance = float(raw_bal)
            except (ValueError, TypeError):
                balance = 128450.00
        else:
            balance = 128450.00

        ref = f"BAL-{uuid.uuid4().hex[:8].upper()}"
        return BankingActionResult(
            action_type="BALANCE_ENQUIRY",
            status="SUCCESS",
            reference_number=ref,
            details={"account_number": acc_num, "available_balance": balance, "currency": "INR", "ifsc": profile.get("ifsc", "NXBK0008821")},
            user_message=f"Your NexBank {acc_type} (Account No: {acc_num}) has a live available balance of INR {balance:,.2f}."
        )

    def request_statement(self, customer_id: str, date_range: str = "30_days", profile: Optional[Dict[str, Any]] = None) -> BankingActionResult:
        profile = profile or {}
        acc_num = profile.get("accNum") or profile.get("account_id") or "110294817502"
        cust_name = profile.get("custName") or "SATHVIKA BOINA"
        email = profile.get("email") or "customer@nexbank.in"
        ref = f"STMT-{uuid.uuid4().hex[:8].upper()}"
        return BankingActionResult(
            action_type="STATEMENT_REQUEST",
            status="SUCCESS",
            reference_number=ref,
            details={"account_number": acc_num, "date_range": date_range, "sent_to_email": email},
            user_message=f"Dear {cust_name}, your account statement for Account No. {acc_num} ({date_range}) has been generated (Ref: {ref}) and sent to your registered email ({email})."
        )

    def block_card(self, customer_id: str, card_last4: str = "4521", reason: str = "Lost/Stolen", profile: Optional[Dict[str, Any]] = None) -> BankingActionResult:
        profile = profile or {}
        card_num = profile.get("cardNum") or f"•••• •••• •••• {card_last4}"
        target_last4 = card_num[-4:] if len(card_num) >= 4 else card_last4
        ref = f"BLK-{uuid.uuid4().hex[:8].upper()}"
        return BankingActionResult(
            action_type="CARD_BLOCK",
            status="SUCCESS",
            reference_number=ref,
            details={"card_number": card_num, "card_last4": target_last4, "block_reason": reason, "blocked_at": datetime.now(timezone.utc).isoformat()},
            user_message=f"Your debit card ending in {target_last4} has been immediately blocked for your security (Ref: {ref}). Card status is now set to BLOCKED."
        )

    def replace_card(self, customer_id: str, card_last4: str = "4521", profile: Optional[Dict[str, Any]] = None) -> BankingActionResult:
        profile = profile or {}
        card_num = profile.get("cardNum") or f"•••• •••• •••• {card_last4}"
        target_last4 = card_num[-4:] if len(card_num) >= 4 else card_last4
        ref = f"REP-{uuid.uuid4().hex[:8].upper()}"
        return BankingActionResult(
            action_type="CARD_REPLACEMENT",
            status="SUCCESS",
            reference_number=ref,
            details={"old_card_last4": target_last4, "delivery_eta": "3-5 business days"},
            user_message=f"Replacement card request recorded for card ending in {target_last4} (Ref: {ref}). Your new debit card will be dispatched to your registered address within 3-5 business days."
        )

    def register_complaint(self, customer_id: str, issue_description: str, profile: Optional[Dict[str, Any]] = None) -> BankingActionResult:
        profile = profile or {}
        cust_name = profile.get("custName") or "Customer"
        ref = f"CMP-2024-{random.randint(70000, 99999)}"
        return BankingActionResult(
            action_type="REGISTER_COMPLAINT",
            status="SUCCESS",
            reference_number=ref,
            details={"complaint_id": ref, "sla_hours": 24, "customer_name": cust_name},
            user_message=f"Your complaint has been registered under Reference ID: {ref}. Our operations team will investigate and update you within 24 hours."
        )

    def check_complaint_status(self, complaint_id: str, profile: Optional[Dict[str, Any]] = None) -> BankingActionResult:
        statuses = ["In Investigation", "Reversal Approved - Processing", "Resolved"]
        curr_status = random.choice(statuses)
        return BankingActionResult(
            action_type="COMPLAINT_STATUS",
            status="SUCCESS",
            reference_number=complaint_id,
            details={"complaint_id": complaint_id, "current_status": curr_status},
            user_message=f"Complaint {complaint_id} status: '{curr_status}'. Priority note has been flagged for expedited processing."
        )

    def dispute_transaction(self, customer_id: str, transaction_id: str, amount: float, reason: str, profile: Optional[Dict[str, Any]] = None) -> BankingActionResult:
        profile = profile or {}
        acc_num = profile.get("accNum") or "110294817502"
        ref = f"DSP-{uuid.uuid4().hex[:8].upper()}"
        return BankingActionResult(
            action_type="TRANSACTION_DISPUTE",
            status="SUCCESS",
            reference_number=ref,
            details={"transaction_id": transaction_id, "dispute_amount": amount, "reason": reason, "account_number": acc_num},
            user_message=f"Dispute raised for transaction {transaction_id} on Account {acc_num} (Amount: INR {amount:,.2f}). Dispute Ref: {ref}. Under NexBank Zero-Liability policy, provisional credit will be credited if verified."
        )

    def resolve_upi_issue(self, upi_ref: str, amount: float, profile: Optional[Dict[str, Any]] = None) -> BankingActionResult:
        profile = profile or {}
        acc_num = profile.get("accNum") or "110294817502"
        ref = f"UPI-{uuid.uuid4().hex[:8].upper()}"
        return BankingActionResult(
            action_type="UPI_FAILURE_RESOLUTION",
            status="SUCCESS",
            reference_number=ref,
            details={"upi_ref": upi_ref, "amount": amount, "account_number": acc_num, "rbi_deemed_success": True},
            user_message=f"UPI transaction {upi_ref} checked for Account {acc_num}. Under RBI deemed success rules, if merchant pending confirmation exceeds 48 hours, INR {amount:,.2f} will be automatically credited back to your account."
        )

    def check_loan_eligibility(self, loan_type: str = "Personal Loan", monthly_income: float = 75000, profile: Optional[Dict[str, Any]] = None) -> BankingActionResult:
        profile = profile or {}
        bal_str = profile.get("accBal") or "128450"
        try:
            current_bal = float(bal_str)
        except (ValueError, TypeError):
            current_bal = 128450.0
        max_loan = round(max(monthly_income * 25, current_bal * 3), -3)
        ref = f"LOAN-{uuid.uuid4().hex[:8].upper()}"
        return BankingActionResult(
            action_type="LOAN_ELIGIBILITY",
            status="SUCCESS",
            reference_number=ref,
            details={"loan_type": loan_type, "pre_approved_amount": max_loan, "interest_rate": "10.5% p.a.", "based_on_balance": current_bal},
            user_message=f"Based on your active account balance (INR {current_bal:,.2f}), you are pre-approved for a {loan_type.title()} up to INR {max_loan:,.2f} at interest rates starting from 10.5% p.a."
        )

    def get_product_info(self, product_name: str, profile: Optional[Dict[str, Any]] = None) -> BankingActionResult:
        ref = f"PRD-{uuid.uuid4().hex[:8].upper()}"
        return BankingActionResult(
            action_type="PRODUCT_INFO",
            status="SUCCESS",
            reference_number=ref,
            details={"product_name": product_name},
            user_message=f"NexBank {product_name} offers premium neo-banking features, zero hidden charges, instant UPI, and DICGC insurance protection."
        )
