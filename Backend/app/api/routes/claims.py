import json
import uuid as uuid_lib
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import TRIGGERS
from app.models.models import Worker, Policy, Claim, ClaimStatusEnum
from app.schemas.schemas import (
    ClaimResponse, ManualTriggerRequest,
    AdminStats, AdminClaimAction,
    TriggerResponse, PayoutResponse
)
from app.models.models import Signal, Trigger, FraudRing, Payout
from app.services.trigger_engine import create_and_process_claim

router = APIRouter(prefix="/claims", tags=["📝 Claims"])


# ─── Worker: View their claims ────────────────────────────────────────────────

@router.get(
    "/worker/{worker_id}",
    response_model=list[ClaimResponse],
    summary="Get all claims for a worker",
)
def get_worker_claims(
    worker_id: UUID,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """Saniya uses this to show the worker their claim history."""
    return (
        db.query(Claim)
        .filter(Claim.worker_id == worker_id)
        .order_by(Claim.created_at.desc())
        .limit(limit)
        .all()
    )


# ─── Admin: View all claims ───────────────────────────────────────────────────

@router.get(
    "/admin/all",
    response_model=list[ClaimResponse],
    summary="[Admin] View all claims with optional status filter",
)
def list_all_claims(
    status_filter: str = None,
    skip:  int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    Chandini uses this for the admin claims table.
    Pass ?status_filter=flagged to see only flagged claims.
    """
    query = db.query(Claim)

    if status_filter:
        try:
            s = ClaimStatusEnum(status_filter)
            query = query.filter(Claim.status == s)
        except ValueError:
            valid = [e.value for e in ClaimStatusEnum]
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status '{status_filter}'. Valid values: {valid}",
            )

    return query.order_by(Claim.created_at.desc()).offset(skip).limit(limit).all()


# ─── Admin: Dashboard stats ───────────────────────────────────────────────────

@router.get(
    "/admin/stats",
    response_model=AdminStats,
    summary="[Admin] Dashboard statistics",
)
def get_admin_stats(db: Session = Depends(get_db)):
    """Chandini's admin dashboard — total workers, claims, payout numbers."""
    now = datetime.utcnow()

    total_workers   = db.query(Worker).count()
    active_policies = db.query(Policy).filter(
        Policy.active == True, Policy.expires_at > now
    ).count()
    total_claims    = db.query(Claim).count()
    pending_claims  = db.query(Claim).filter(Claim.status == ClaimStatusEnum.pending).count()
    flagged_claims  = db.query(Claim).filter(Claim.status == ClaimStatusEnum.flagged).count()
    rejected_claims = db.query(Claim).filter(Claim.status == ClaimStatusEnum.rejected).count()

    approved_list = db.query(Claim).filter(
        Claim.status.in_([ClaimStatusEnum.approved, ClaimStatusEnum.partial])
    ).all()
    approved_claims  = len(approved_list)
    total_paid_rs    = sum(c.payout_amount_paise for c in approved_list) / 100
    approval_rate    = round(approved_claims / total_claims * 100, 1) if total_claims > 0 else 0.0

    return AdminStats(
        total_workers     = total_workers,
        active_policies   = active_policies,
        total_claims      = total_claims,
        pending_claims    = pending_claims,
        flagged_claims    = flagged_claims,
        approved_claims   = approved_claims,
        rejected_claims   = rejected_claims,
        total_paid_out_rs = round(total_paid_rs, 2),
        approval_rate_pct = approval_rate,
    )


# ─── Admin: Approve / Reject flagged claims ───────────────────────────────────

@router.post(
    "/admin/{claim_id}/approve",
    response_model=ClaimResponse,
    summary="[Admin] Manually approve a flagged claim",
)
def approve_claim(
    claim_id: UUID,
    body: AdminClaimAction = None,
    db: Session = Depends(get_db),
):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    if claim.status not in [ClaimStatusEnum.flagged, ClaimStatusEnum.pending]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot approve a claim with status '{claim.status.value}'",
        )

    policy = db.query(Policy).filter(Policy.id == claim.policy_id).first()
    payout = policy.coverage_per_day_paise if policy else 0

    claim.status              = ClaimStatusEnum.approved
    claim.payout_amount_paise = payout
    claim.payout_upi_ref      = f"SHLD{uuid_lib.uuid4().hex[:10].upper()}"
    claim.processed_at        = datetime.utcnow()

    if policy:
        policy.total_paid_out_paise = (policy.total_paid_out_paise or 0) + payout

    db.commit()
    db.refresh(claim)
    return claim


@router.post(
    "/admin/{claim_id}/reject",
    response_model=ClaimResponse,
    summary="[Admin] Reject a flagged claim",
)
def reject_claim(
    claim_id: UUID,
    body: AdminClaimAction = None,
    db: Session = Depends(get_db),
):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    claim.status       = ClaimStatusEnum.rejected
    claim.processed_at = datetime.utcnow()
    db.commit()
    db.refresh(claim)
    return claim


# ─── Demo Trigger (most important endpoint for the video!) ────────────────────

@router.post(
    "/demo/trigger",
    response_model=ClaimResponse,
    status_code=status.HTTP_201_CREATED,
    summary="🎬 DEMO — Manually fire a weather trigger for a worker",
)
def demo_trigger(payload: ManualTriggerRequest, db: Session = Depends(get_db)):
    """
    ⚡ USE THIS IN YOUR DEMO VIDEO ⚡

    Simulates a weather event for a specific worker instantly.
    No waiting for the 15-minute scheduler.

    Example — simulate heavy rain:
    {
      "worker_id": "<paste worker UUID here>",
      "trigger_type": "heavy_rain",
      "trigger_value": 40.0
    }

    Available trigger types:
      - heavy_rain       (threshold: 15mm/hr)
      - flood_alert      (threshold: 35mm/hr)
      - extreme_heat     (threshold: 42°C)
      - severe_aqi       (threshold: AQI 300)
      - low_visibility   (threshold: <500m)
    """
    # Validate worker exists
    worker = db.query(Worker).filter(Worker.id == payload.worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    # Validate trigger type
    trigger_cfg = TRIGGERS.get(payload.trigger_type)
    if not trigger_cfg:
        valid = list(TRIGGERS.keys())
        raise HTTPException(
            status_code=400,
            detail=f"Unknown trigger '{payload.trigger_type}'. Valid: {valid}",
        )

    # Check active policy
    now = datetime.utcnow()
    policy = db.query(Policy).filter(
        Policy.worker_id == payload.worker_id,
        Policy.active    == True,
        Policy.expires_at > now,
    ).first()
    if not policy:
        raise HTTPException(
            status_code=400,
            detail="Worker has no active policy. They must purchase a plan first.",
        )

    event = {
        "type":       payload.trigger_type,
        "value":      payload.trigger_value,
        "threshold":  trigger_cfg["threshold"],
        "payout_pct": trigger_cfg["payout_pct"],
        "label":      trigger_cfg["label"],
    }

    claim = create_and_process_claim(db, worker, policy, event)

    # 🔗 PHASE 3: Generate Mock Telemetry Signals for AI analysis
    # This ensures the Isolation Forest has "features" to look at.
    mock_signals = Signal(
        claim_id=claim.id,
        gps=f"{worker.zone_pincode},mock",
        accelerometer="vibration_level: 0.12",
        battery="85%",
        mock_flag=False # Set this to True in a separate "Spoof Demo" endpoint if needed
    )
    db.add(mock_signals)
    db.commit()

    return claim


@router.get(
    "/admin/stats",
    summary="[Admin] Get high-level orchestration metrics",
)
def get_admin_stats(db: Session = Depends(get_db)):
    from sqlalchemy import func
    from app.models.models import Worker, Policy, Claim, ClaimStatusEnum
    
    total_workers = db.query(Worker).count()
    active_policies = db.query(Policy).filter(Policy.active == True).count()
    
    # Calculate Total Paid Out (in Rupees)
    total_paise = db.query(func.sum(Claim.payout_amount_paise)).filter(
        Claim.status == ClaimStatusEnum.approved
    ).scalar() or 0
    
    # Calculate Approval Rate
    total_claims = db.query(Claim).count()
    approved_claims = db.query(Claim).filter(Claim.status == ClaimStatusEnum.approved).count()
    approval_rate = (approved_claims / total_claims * 100) if total_claims > 0 else 0
    
    return {
        "total_workers": total_workers,
        "active_policies": active_policies,
        "total_paid_out_rs": round(total_paise / 100, 2),
        "approval_rate_pct": round(approval_rate, 1)
    }


# ─── Phase 3: Analytics & Visualization ────────────────────────────────────────

@router.get(
    "/admin/fraud-rings",
    response_model=list[dict],
    summary="[Admin] Get detected fraud clusters (GNN output)",
)
def get_fraud_rings(db: Session = Depends(get_db)):
    """Used for the 'GNN Ring Graph' visualization."""
    rings = db.query(FraudRing).order_by(FraudRing.detected_at.desc()).limit(10).all()
    # Convert to simple dict for the chart
    return [{"id": str(r.cluster_id), "score": r.ring_score, "claims": json.loads(r.claim_ids)} for r in rings]


@router.get(
    "/admin/heatmap",
    summary="[Admin] Get claim density by zone for Mapbox/Leaflet",
)
def get_claim_heatmap(db: Session = Depends(get_db)):
    """Returns claims grouped by zone for the heatmap visual."""
    from sqlalchemy import func
    results = (
        db.query(Worker.zone_pincode, func.count(Claim.id).label("intensity"))
        .join(Claim, Worker.id == Claim.worker_id)
        .group_by(Worker.zone_pincode)
        .all()
    )
    return [{"zone": r[0], "intensity": r[1]} for r in results]


@router.get(
    "/admin/payouts",
    response_model=list[PayoutResponse],
    summary="[Admin] View recent transaction statuses",
)
def list_payouts(db: Session = Depends(get_db)):
    return db.query(Payout).order_by(Payout.created_at.desc()).limit(50).all()
