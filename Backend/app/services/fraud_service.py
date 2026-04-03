"""
Fraud Detection Service
───────────────────────
Scores every claim from 0.0 (definitely clean) to 1.0 (definitely fraud).

Decision tiers:
  score < 0.40  →  auto-approve   (Tier 1) → full payout
  score < 0.70  →  partial payout (Tier 2) → 40% advance, rest after review
  score ≥ 0.70  →  flag for human (Tier 3) → admin must approve/reject

Signals checked:
  1. Duplicate claim in last 6 hours for same trigger type
  2. Too many claims this week (>3)
  3. Unrealistically high trigger value (possible fake API data)
  4. Brand new account (<3 days old) claiming immediately
  5. Claimed while policy is near expiry (within 12 hours)
"""
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.models import Claim, Worker, ClaimStatusEnum


# ─── Signal weights (must sum to ≤ 1.0 to keep score in 0–1 range) ───────────
SIGNAL_WEIGHTS = {
    "duplicate_claim_6h":         0.50,
    "high_claim_frequency":       0.20,
    "unrealistic_trigger_value":  0.30,
    "new_account_early_claim":    0.15,
    "near_expiry_claim":          0.10,
}

# Realistic max values for each trigger type
MAX_REALISTIC_VALUES = {
    "heavy_rain":     100.0,    # mm/hr — anything above this is physically impossible
    "flood_alert":    100.0,
    "extreme_heat":   52.0,     # °C — highest ever recorded in India
    "severe_aqi":     500.0,    # AQI scale tops at 500
    "low_visibility": 10000.0,  # if visibility > 10km, fog trigger is wrong
}


def calculate_fraud_score(
    worker: Worker,
    trigger_type: str,
    trigger_value: float,
    db: Session,
) -> tuple[float, list[str]]:
    """
    Returns:
        fraud_score: float between 0.0 and 1.0
        signals:     list of signal names that were triggered (for audit trail)
    """
    score   = 0.0
    signals = []

    # ── Signal 1: Duplicate claim in last 6 hours ────────────────────────────
    six_hours_ago = datetime.utcnow() - timedelta(hours=6)
    duplicate = db.query(Claim).filter(
        Claim.worker_id  == worker.id,
        Claim.trigger_type == trigger_type,
        Claim.created_at >= six_hours_ago,
        Claim.status     != ClaimStatusEnum.rejected,
    ).first()
    if duplicate:
        score += SIGNAL_WEIGHTS["duplicate_claim_6h"]
        signals.append("duplicate_claim_6h")

    # ── Signal 2: Too many claims this week ──────────────────────────────────
    week_ago = datetime.utcnow() - timedelta(days=7)
    weekly_count = db.query(Claim).filter(
        Claim.worker_id  == worker.id,
        Claim.created_at >= week_ago,
        Claim.status     != ClaimStatusEnum.rejected,
    ).count()
    if weekly_count >= 4:
        score += SIGNAL_WEIGHTS["high_claim_frequency"]
        signals.append(f"high_claim_frequency_{weekly_count}_this_week")

    # ── Signal 3: Unrealistic trigger value ──────────────────────────────────
    max_realistic = MAX_REALISTIC_VALUES.get(trigger_type, 9999)
    if trigger_value > max_realistic:
        score += SIGNAL_WEIGHTS["unrealistic_trigger_value"]
        signals.append(f"unrealistic_value_{trigger_value}_max_{max_realistic}")

    # ── Signal 4: New account claiming immediately ───────────────────────────
    account_age_days = (datetime.utcnow() - worker.created_at).days
    if account_age_days < 3:
        score += SIGNAL_WEIGHTS["new_account_early_claim"]
        signals.append(f"new_account_{account_age_days}_days_old")

    # ── Signal 5: Claiming near policy expiry ────────────────────────────────
    from app.models.models import Policy
    active_policy = db.query(Policy).filter(
        Policy.worker_id == worker.id,
        Policy.active    == True,
    ).first()
    if active_policy and active_policy.expires_at:
        hours_to_expiry = (active_policy.expires_at - datetime.utcnow()).total_seconds() / 3600
        if 0 < hours_to_expiry < 12:
            score += SIGNAL_WEIGHTS["near_expiry_claim"]
            signals.append(f"near_expiry_{round(hours_to_expiry, 1)}h_remaining")

    final_score = min(round(score, 3), 1.0)
    return final_score, signals


def decide_action(fraud_score: float) -> str:
    """Returns 'approve', 'partial', or 'flag'."""
    if fraud_score < 0.40:
        return "approve"
    elif fraud_score < 0.70:
        return "partial"
    else:
        return "flag"


def compute_payout(
    action: str,
    coverage_per_day_paise: int,
    payout_pct: float,
) -> int:
    """
    Calculate the actual payout amount in paise.
    - approve: full coverage × payout_pct (e.g. extreme_heat = 50%)
    - partial: 40% advance of what would have been approved
    - flag:    0 (pending human review)
    """
    full_payout = int(coverage_per_day_paise * payout_pct)
    if action == "approve":
        return full_payout
    elif action == "partial":
        return int(full_payout * 0.40)
    else:
        return 0
