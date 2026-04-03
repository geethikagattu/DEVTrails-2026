from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.models import Worker, Policy, PlanEnum
from app.schemas.schemas import (
    PolicyCreate, PolicyResponse,
    PremiumQuoteRequest, PremiumQuoteResponse,
    AllQuotesResponse,
)
from app.services.premium_service import calculate_premium

router = APIRouter(prefix="/policies", tags=["📋 Policies"])


# ─── Quote Endpoints ──────────────────────────────────────────────────────────

@router.get(
    "/quote/all/{worker_id}",
    response_model=AllQuotesResponse,
    summary="Get AI-calculated quotes for all 3 plans",
)
def get_all_quotes(worker_id: UUID, db: Session = Depends(get_db)):
    """
    Saniya calls this to show the plan selection screen.
    Returns personalised prices for Basic, Standard, and Premium plans
    based on the worker's zone, platform, and earnings.
    """
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    quotes = {
        plan.value: calculate_premium(worker, plan.value)
        for plan in PlanEnum
    }

    return AllQuotesResponse(
        worker_id       = worker.id,
        worker_name     = worker.name,
        zone_risk_score = worker.zone_risk_score,
        quotes          = quotes,
    )


@router.post(
    "/quote",
    response_model=PremiumQuoteResponse,
    summary="Get a quote for a single plan",
)
def get_single_quote(payload: PremiumQuoteRequest, db: Session = Depends(get_db)):
    worker = db.query(Worker).filter(Worker.id == payload.worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    result = calculate_premium(worker, payload.plan.value)
    return PremiumQuoteResponse(**result)


# ─── Purchase ─────────────────────────────────────────────────────────────────

@router.post(
    "/purchase",
    response_model=PolicyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Worker buys an insurance plan",
)
def purchase_policy(payload: PolicyCreate, db: Session = Depends(get_db)):
    """
    Creates a new active policy for the worker (valid 7 days).
    If they already have an active policy, it's deactivated first.
    Premium is calculated fresh at purchase time.
    """
    worker = db.query(Worker).filter(Worker.id == payload.worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    # Deactivate any existing active policy
    existing_policy = db.query(Policy).filter(
        Policy.worker_id == payload.worker_id,
        Policy.active    == True,
    ).first()
    if existing_policy:
        existing_policy.active = False
        db.commit()

    # Calculate the dynamic premium
    pricing = calculate_premium(worker, payload.plan.value)

    now = datetime.utcnow()
    policy = Policy(
        worker_id               = payload.worker_id,
        plan                    = payload.plan,
        base_premium_paise      = pricing["base_premium_paise"],
        weekly_premium_paise    = pricing["adjusted_premium_paise"],
        coverage_per_day_paise  = pricing["coverage_per_day_paise"],
        max_weekly_payout_paise = pricing["max_weekly_payout_paise"],
        risk_multiplier         = pricing["risk_multiplier"],
        risk_explanation        = pricing["risk_explanation"],
        active                  = True,
        activated_at            = now,
        expires_at              = now + timedelta(days=7),
        total_paid_out_paise    = 0,
    )
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


# ─── View Policies ────────────────────────────────────────────────────────────

@router.get(
    "/active/{worker_id}",
    response_model=PolicyResponse,
    summary="Get a worker's currently active policy",
)
def get_active_policy(worker_id: UUID, db: Session = Depends(get_db)):
    policy = db.query(Policy).filter(
        Policy.worker_id == worker_id,
        Policy.active    == True,
        Policy.expires_at > datetime.utcnow(),
    ).first()
    if not policy:
        raise HTTPException(
            status_code=404,
            detail="No active policy. Worker needs to purchase a plan.",
        )
    return policy


@router.get(
    "/history/{worker_id}",
    response_model=list[PolicyResponse],
    summary="Get all policies (history) for a worker",
)
def get_policy_history(worker_id: UUID, db: Session = Depends(get_db)):
    return (
        db.query(Policy)
        .filter(Policy.worker_id == worker_id)
        .order_by(Policy.activated_at.desc())
        .all()
    )


@router.get(
    "/{policy_id}",
    response_model=PolicyResponse,
    summary="Get a specific policy by ID",
)
def get_policy(policy_id: UUID, db: Session = Depends(get_db)):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


@router.get(
    "/admin/all",
    response_model=list[PolicyResponse],
    summary="[Admin] List all policies",
)
def list_all_policies(
    active_only: bool = False,
    skip:  int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(Policy)
    if active_only:
        query = query.filter(Policy.active == True, Policy.expires_at > datetime.utcnow())
    return query.order_by(Policy.activated_at.desc()).offset(skip).limit(limit).all()
