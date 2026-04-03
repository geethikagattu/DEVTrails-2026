import uuid
import enum
from datetime import datetime
from sqlalchemy import (
    Column, String, Boolean, Float, Integer,
    DateTime, ForeignKey, Enum, Text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


# ─── Enums ─────────────────────────────────────────────────────────────────────

class PlatformEnum(str, enum.Enum):
    zomato = "zomato"
    swiggy = "swiggy"


class PlanEnum(str, enum.Enum):
    basic    = "basic"      # ₹29/week
    standard = "standard"   # ₹49/week
    premium  = "premium"    # ₹79/week


class ClaimStatusEnum(str, enum.Enum):
    pending  = "pending"    # just created, not yet processed
    approved = "approved"   # auto or manually approved, full payout
    partial  = "partial"    # soft fraud flag → 40% advance payout
    flagged  = "flagged"    # high fraud score → needs human review
    rejected = "rejected"   # admin rejected it


# ─── Worker ────────────────────────────────────────────────────────────────────

class Worker(Base):
    """
    A delivery partner (Zomato/Swiggy) who registers on ShieldRun.
    One worker can have many policies over time, and many claims.
    """
    __tablename__ = "workers"

    id                  = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone               = Column(String(15), unique=True, nullable=False, index=True)
    name                = Column(String(100), nullable=False)
    platform            = Column(Enum(PlatformEnum), nullable=False)
    platform_id         = Column(String(50), nullable=False)        # their Zomato/Swiggy ID
    zone_pincode        = Column(String(10), nullable=False)
    city                = Column(String(50), nullable=False)
    upi_id              = Column(String(100), nullable=True)         # for payouts
    zone_risk_score     = Column(Integer, default=50)               # 0–100, AI-computed
    avg_daily_earnings  = Column(Float, default=500.0)              # ₹ per day
    is_active           = Column(Boolean, default=True)
    created_at          = Column(DateTime, default=datetime.utcnow)
    updated_at          = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    policies = relationship("Policy", back_populates="worker", lazy="select")
    claims   = relationship("Claim",  back_populates="worker", lazy="select")

    def __repr__(self):
        return f"<Worker {self.name} ({self.phone})>"


# ─── Policy ────────────────────────────────────────────────────────────────────

class Policy(Base):
    """
    An insurance policy purchased by a worker. Valid for 7 days.
    Premium is dynamically calculated by the AI pricing engine.
    """
    __tablename__ = "policies"

    id                       = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    worker_id                = Column(UUID(as_uuid=True), ForeignKey("workers.id"), nullable=False, index=True)
    plan                     = Column(Enum(PlanEnum), nullable=False)

    # Pricing (all in PAISE to avoid float errors)
    base_premium_paise       = Column(Integer, nullable=False)      # before AI adjustment
    weekly_premium_paise     = Column(Integer, nullable=False)      # final price worker pays
    coverage_per_day_paise   = Column(Integer, nullable=False)      # how much per disrupted day
    max_weekly_payout_paise  = Column(Integer, nullable=False)      # weekly cap

    # AI metadata
    risk_multiplier          = Column(Float, default=1.0)           # how much AI adjusted
    risk_explanation         = Column(String(500), default="")      # human-readable reason

    # Status
    active                   = Column(Boolean, default=True)
    activated_at             = Column(DateTime, default=datetime.utcnow)
    expires_at               = Column(DateTime, nullable=True)      # activated_at + 7 days

    # Running totals
    total_paid_out_paise     = Column(Integer, default=0)

    # Relationships
    worker = relationship("Worker", back_populates="policies")
    claims = relationship("Claim",  back_populates="policy")

    def __repr__(self):
        return f"<Policy {self.plan} worker={self.worker_id} active={self.active}>"


# ─── Claim ─────────────────────────────────────────────────────────────────────

class Claim(Base):
    """
    Auto-generated when a parametric trigger fires (or manually via demo endpoint).
    Fraud score determines if it's auto-approved, partially paid, or flagged.
    """
    __tablename__ = "claims"

    id                   = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    worker_id            = Column(UUID(as_uuid=True), ForeignKey("workers.id"), nullable=False, index=True)
    policy_id            = Column(UUID(as_uuid=True), ForeignKey("policies.id"), nullable=False)

    # What triggered this claim
    trigger_type         = Column(String(30), nullable=False)       # e.g. "heavy_rain"
    trigger_value        = Column(Float, nullable=False)            # actual measured value
    trigger_threshold    = Column(Float, nullable=False)            # value that was crossed
    trigger_label        = Column(String(100), default="")          # human-readable

    # Fraud detection results
    fraud_score          = Column(Float, default=0.0)               # 0.0=clean → 1.0=fraud
    fraud_signals        = Column(Text, default="[]")               # JSON list of signal names

    # Decision & payout
    status               = Column(Enum(ClaimStatusEnum), default=ClaimStatusEnum.pending)
    payout_amount_paise  = Column(Integer, default=0)
    payout_upi_ref       = Column(String(100), nullable=True)       # mock UPI transaction ID

    # Timestamps
    created_at           = Column(DateTime, default=datetime.utcnow, index=True)
    processed_at         = Column(DateTime, nullable=True)

    # Relationships
    worker = relationship("Worker", back_populates="claims")
    policy = relationship("Policy", back_populates="claims")

    def __repr__(self):
        return f"<Claim {self.trigger_type} status={self.status} payout=₹{self.payout_amount_paise/100}>"
