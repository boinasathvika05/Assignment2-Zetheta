import pytest
from app.services.banking_service import MockBankingCoreService


def test_banking_actions_all_workflows():
    banking = MockBankingCoreService()

    # 1. Balance Enquiry
    bal = banking.check_balance("cust_123")
    assert bal.status == "SUCCESS"
    assert "4521" in bal.user_message

    # 2. Statement Request
    stmt = banking.request_statement("cust_123", "30_days")
    assert stmt.status == "SUCCESS"
    assert "STMT-" in stmt.reference_number

    # 3. Card Block
    blk = banking.block_card("cust_123", "5678", "Stolen")
    assert blk.status == "SUCCESS"
    assert "5678" in blk.user_message

    # 4. Card Replacement
    rep = banking.replace_card("cust_123", "5678")
    assert rep.status == "SUCCESS"
    assert "REP-" in rep.reference_number

    # 5. Register Complaint
    cmp = banking.register_complaint("cust_123", "Wrong debit of 8500")
    assert cmp.status == "SUCCESS"
    assert "CMP-2024-" in cmp.reference_number

    # 6. Check Complaint Status
    status_res = banking.check_complaint_status("CMP-2024-78901")
    assert status_res.status == "SUCCESS"
    assert "CMP-2024-78901" in status_res.user_message

    # 7. Transaction Dispute
    dsp = banking.dispute_transaction("cust_123", "TXN123", 15000.0, "Unauthorized")
    assert dsp.status == "SUCCESS"
    assert "DSP-" in dsp.reference_number

    # 8. UPI Issue
    upi = banking.resolve_upi_issue("UPI987654", 2500.0)
    assert upi.status == "SUCCESS"
    assert "UPI-" in upi.reference_number

    # 9. Loan Enquiry
    loan = banking.check_loan_eligibility("Personal Loan", 80000.0)
    assert loan.status == "SUCCESS"
    assert loan.details["pre_approved_amount"] > 0

    # 10. Product Info
    prd = banking.get_product_info("NexSave Savings")
    assert prd.status == "SUCCESS"
    assert "NexSave" in prd.user_message
