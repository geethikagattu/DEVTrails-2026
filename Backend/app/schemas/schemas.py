from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.models.models import PlatformEnum, PlanEnum, ClaimStatusEnum


# ══════════════════════════════════════════════════════════
#  WORKER SCHEMAS
# ══════════════════════════════════════════════════════════

class WorkerCreate(BaseModel):
    phone:              str   = Field(..., example="9876543210", description="10-digit mobile number")
    name:               str   = Field(..., example="Raju Kumar")
    platform:           PlatformEnum
    platform_id:        str   = Field(..., example="ZOM12345", description="Zomato or Swiggy worker ID")
    zone_pincode:       str   = Field(..., example="500032")
    city:               str   = Field(..., example="Hyderabad")
    upi_id:             Optional[str] = Field(None, example="raju@ybl")
    avg_daily_earnings: Optional[float] = Field(500.0, example=600.0, description="Estimated daily earnings in ₹")
    otp_code:           str   = Field(..., example="1234", description="4-digit OTP code sent to phone")

class OtpRequest(BaseModel):
    phone: str = Field(..., example="9876543210")

class WorkerLogin(BaseModel):
    phone: str = Field(..., example="9876543210")
    otp_code: str = Field(..., example="1234")

class WorkerResponse(BaseModel):
    id:                 UUID
    phone:              str
    name:               str
    platform:           PlatformEnum
    platform_id:        str
    zone_pincode:       str
    city:               str
    upi_id:             Optional[str]
    firebase_uid:       Optional[str]
    zone_risk_score:    int
    avg_daily_earnings: float
    is_active:          bool
    created_at:         datetime

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════════════════
#  PREMIUM / QUOTE SCHEMAS
# ══════════════════════════════════════════════════════════

class PremiumQuoteRequest(BaseModel):
    worker_id: UUID
    plan:      PlanEnum


class PremiumQuoteResponse(BaseModel):
    plan:                  str
    plan_label:            str
    base_premium_rs:       float
    adjusted_premium_rs:   float
    risk_multiplier:       float
    coverage_per_day_rs:   float
    max_weekly_payout_rs:  float
    risk_explanation:      str


class AllQuotesResponse(BaseModel):
    worker_id:  UUID
    worker_name: str
    zone_risk_score: int
    quotes:     dict   # plan_name → PremiumQuoteResponse


# ══════════════════════════════════════════════════════════
#  POLICY SCHEMAS
# ══════════════════════════════════════════════════════════

class PolicyCreate(BaseModel):
    worker_id: UUID
    plan:      PlanEnum


class PolicyResponse(BaseModel):
    id:                      UUID
    worker_id:               UUID
    plan:                    PlanEnum
    base_premium_paise:      int
    weekly_premium_paise:    int
    coverage_per_day_paise:  int
    max_weekly_payout_paise: int
    risk_multiplier:         float
    risk_explanation:        str
    active:                  bool
    activated_at:            datetime
    expires_at:              Optional[datetime]
    total_paid_out_paise:    int

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════════════════
#  CLAIM SCHEMAS
# ══════════════════════════════════════════════════════════

class ClaimResponse(BaseModel):
    id:                  UUID
    worker_id:           UUID
    policy_id:           UUID
    trigger_type:        str
    trigger_value:       float
    trigger_threshold:   float
    trigger_label:       str
    fraud_score:         float
    fraud_signals:       str    # JSON string
    status:              ClaimStatusEnum
    payout_amount_paise: int
    payout_upi_ref:      Optional[str]
    created_at:          datetime
    processed_at:        Optional[datetime]

    class Config:
        from_attributes = True


class ManualTriggerRequest(BaseModel):
    """Used by the demo endpoint to simulate a weather event instantly."""
    worker_id:     UUID
    trigger_type:  str   = Field(..., example="heavy_rain",
                              description="One of: heavy_rain, flood_alert, extreme_heat, severe_aqi, low_visibility")
    trigger_value: float = Field(..., example=40.0, description="The simulated sensor value")


class AdminClaimAction(BaseModel):
    reason: Optional[str] = Field(None, example="Verified via manual review")


# ══════════════════════════════════════════════════════════
#  DASHBOARD SCHEMAS
# ══════════════════════════════════════════════════════════

class WorkerDashboard(BaseModel):
    worker:            WorkerResponse
    active_policy:     Optional[PolicyResponse]
    recent_claims:     List[ClaimResponse]
    total_earned_rs:   float
    claims_this_week:  int
    is_protected:      bool   # True if active policy exists


class AdminStats(BaseModel):
    total_workers:      int
    active_policies:    int
    total_claims:       int
    pending_claims:     int
    flagged_claims:     int
    approved_claims:    int
    rejected_claims:    int
    total_paid_out_rs:  float
    approval_rate_pct:  float


# ══════════════════════════════════════════════════════════
#  HEALTH CHECK
# ══════════════════════════════════════════════════════════

class HealthResponse(BaseModel):
    status:      str
    db_connected: bool
    environment: str
    version:     str


# ══════════════════════════════════════════════════════════
#  PHASE 3 SCHEMAS (Triggers, Signals, Payouts)
# ══════════════════════════════════════════════════════════

class SignalCreate(BaseModel):
    claim_id:      UUID
    gps:           Optional[str] = None
    accelerometer: Optional[str] = None
    battery:       Optional[str] = None
    cell_id:       Optional[str] = None
    mock_flag:     bool = False

class TriggerResponse(BaseModel):
    id:        UUID
    zone:      Optional[str] = None
    type:      str
    value:     float
    timestamp: datetime

    class Config:
        from_attributes = True

class PayoutResponse(BaseModel):
    id:              UUID
    claim_id:        UUID
    razorpay_txn_id: Optional[str]
    status:          str
    retry_count:     int

    class Config:
        from_attributes = True
