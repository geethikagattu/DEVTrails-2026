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
    firebase_uid        = Column(String(128), unique=True, nullable=True, index=True) # Phase 3: Firebase Auth
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

# ─── OTP ───────────────────────────────────────────────────────────────────────

class OneTimePassword(Base):
    """
    Temporarily stores an OTP generated for a phone number for login/registration verification.
    """
    __tablename__ = "one_time_passwords"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone      = Column(String(15), nullable=False, index=True)
    otp_code   = Column(String(6), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def is_valid(self):
        return datetime.utcnow() <= self.expires_at

    def __repr__(self):
        return f"<OTP phone={self.phone} expire={self.expires_at}>"


# ─── Trigger (Phase 3) ─────────────────────────────────────────────────────────

class TriggerEnum(str, enum.Enum):
    weather = "weather"
    aqi     = "aqi"
    curfew  = "curfew"
    outage  = "outage"

class Trigger(Base):
    """Recorded events from external APIs (Weather, AQI, Manual Mock)."""
    __tablename__ = "triggers"
    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    zone        = Column(String(50), nullable=False, index=True)
    type        = Column(Enum(TriggerEnum), nullable=False)
    value       = Column(Float, nullable=False)
    timestamp   = Column(DateTime, default=datetime.utcnow)


# ─── Signals (Phase 3 Fraud Detection) ─────────────────────────────────────────

class Signal(Base):
    """Multi-signal telemetry for each claim, used by the Fraud GNN."""
    __tablename__ = "signals"
    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_id      = Column(UUID(as_uuid=True), ForeignKey("claims.id"), nullable=False, index=True)
    gps           = Column(String(100), nullable=True)          # e.g. "lat,lng"
    accelerometer = Column(String(100), nullable=True)
    battery       = Column(String(50), nullable=True)
    cell_id       = Column(String(50), nullable=True)
    mock_flag     = Column(Boolean, default=False)              # True if spoofed
    created_at    = Column(DateTime, default=datetime.utcnow)


# ─── Fraud Ring (Phase 3 GNN Output) ──────────────────────────────────────────

class FraudRing(Base):
    """Stores clusters detected by the GNN."""
    __tablename__ = "fraudrings"
    cluster_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_ids  = Column(Text, default="[]")                     # JSON list of claim UUIDs
    ring_score = Column(Float, default=0.0)
    detected_at= Column(DateTime, default=datetime.utcnow)


# ─── Payout (Phase 3) ──────────────────────────────────────────────────────────

class PayoutStatusEnum(str, enum.Enum):
    pending = "pending"
    success = "success"
    failed  = "failed"

class Payout(Base):
    """Tracks UPI transactions via Razorpay."""
    __tablename__ = "payouts"
    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_id        = Column(UUID(as_uuid=True), ForeignKey("claims.id"), nullable=False, index=True)
    razorpay_txn_id = Column(String(100), nullable=True)
    status          = Column(Enum(PayoutStatusEnum), default=PayoutStatusEnum.pending)
    retry_count     = Column(Integer, default=0)
    created_at      = Column(DateTime, default=datetime.utcnow)
    updated_at      = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

