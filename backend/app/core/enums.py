from enum import Enum


class UserRole(str, Enum):
    """
    Role-Based Access Control (RBAC) roles across NexBank enterprise system.
    """
    CUSTOMER = "CUSTOMER"
    SUPPORT_AGENT = "SUPPORT_AGENT"
    SUPERVISOR = "SUPERVISOR"
    RISK_OFFICER = "RISK_OFFICER"
    SYSTEM_ADMIN = "SYSTEM_ADMIN"


class AuthLevel(str, Enum):
    """
    Progressive Authentication Levels for NexBank customers.
    """
    ANONYMOUS = "ANONYMOUS"
    OTP_VERIFIED = "OTP_VERIFIED"
    BIOMETRIC_VERIFIED = "BIOMETRIC_VERIFIED"
    FULL_KYC = "FULL_KYC"


class EscalationPriority(str, Enum):
    """Priority queues for human escalations."""
    P0 = "P0"  # Critical Security / Fraud / Crisis (<2 min SLA)
    P1 = "P1"  # High Priority Legal / High Value / Retention (<5 min SLA)
    P2 = "P2"  # General Support / Technical / Overflow (<10-15 min SLA)


class ResolutionStatus(str, Enum):
    """Outcome classification for conversations."""
    RESOLVED_AI = "RESOLVED_AI"
    RESOLVED_HUMAN = "RESOLVED_HUMAN"
    UNRESOLVED_DROPPED = "UNRESOLVED_DROPPED"
    UNRESOLVED_ESCALATED = "UNRESOLVED_ESCALATED"
    FALSE_RESOLUTION = "FALSE_RESOLUTION"


class SeverityLevel(str, Enum):
    """Supervisor correction severity taxonomy."""
    CRITICAL_SAFETY_ERROR = "CRITICAL_SAFETY_ERROR"
    MODERATE_QUALITY_ISSUE = "MODERATE_QUALITY_ISSUE"
    MINOR_STYLE_IMPROVEMENT = "MINOR_STYLE_IMPROVEMENT"
    FALSE_POSITIVE_ESCALATION = "FALSE_POSITIVE_ESCALATION"
