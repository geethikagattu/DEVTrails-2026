from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.models import Worker, Policy, Claim, ClaimStatusEnum
from app.schemas.schemas import WorkerCreate, WorkerResponse, WorkerDashboard
from app.services.premium_service import calculate_zone_risk_score

router = APIRouter(prefix="/workers", tags=["👷 Workers"])


# ─── Register ─────────────────────────────────────────────────────────────────

@router.post(
    "/register",
    response_model=WorkerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new delivery worker",
)
def register_worker(payload: WorkerCreate, db: Session = Depends(get_db)):
    """
    Onboard a new Zomato/Swiggy worker.
    Phone number must be unique — used as the login identifier.
    Zone risk score is auto-calculated from the pincode.
    """
    existing = db.query(Worker).filter(Worker.phone == payload.phone).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A worker with phone {payload.phone} is already registered.",
        )

    risk_score = calculate_zone_risk_score(payload.zone_pincode)

    worker = Worker(
        phone              = payload.phone,
        name               = payload.name,
        platform           = payload.platform,
        platform_id        = payload.platform_id,
        zone_pincode       = payload.zone_pincode,
        city               = payload.city,
        upi_id             = payload.upi_id,
        avg_daily_earnings = payload.avg_daily_earnings or 500.0,
        zone_risk_score    = risk_score,
    )
    db.add(worker)
    db.commit()
    db.refresh(worker)
    return worker


# ─── Login / Lookup ───────────────────────────────────────────────────────────

@router.get(
    "/login/{phone}",
    response_model=WorkerResponse,
    summary="Worker login by phone number",
)
def login_by_phone(phone: str, db: Session = Depends(get_db)):
    """
    Saniya uses this for the worker login screen.
    The frontend sends the phone number, gets back the worker object (incl. ID).
    """
    worker = db.query(Worker).filter(Worker.phone == phone).first()
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No worker found with this phone number. Please register first.",
        )
    return worker


@router.get(
    "/{worker_id}",
    response_model=WorkerResponse,
    summary="Get worker by ID",
)
def get_worker(worker_id: UUID, db: Session = Depends(get_db)):
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    return worker


# ─── Dashboard ────────────────────────────────────────────────────────────────

@router.get(
    "/{worker_id}/dashboard",
    response_model=WorkerDashboard,
    summary="Worker home screen — all data in one call",
)
def get_dashboard(worker_id: UUID, db: Session = Depends(get_db)):
    """
    Returns everything the worker home screen needs in a single API call:
    - Worker profile
    - Active policy (if any)
    - Last 10 claims
    - Total amount earned via claims
    - Is currently protected (boolean)

    Saniya calls this endpoint to render the worker's home screen.
    """
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    now = datetime.utcnow()

    # Active policy
    active_policy = db.query(Policy).filter(
        Policy.worker_id == worker_id,
        Policy.active    == True,
        Policy.expires_at > now,
    ).first()

    # Recent claims (last 7 days)
    week_ago      = now - timedelta(days=7)
    recent_claims = (
        db.query(Claim)
        .filter(Claim.worker_id == worker_id, Claim.created_at >= week_ago)
        .order_by(Claim.created_at.desc())
        .limit(10)
        .all()
    )

    # Total ever earned
    all_paid = db.query(Claim).filter(
        Claim.worker_id == worker_id,
        Claim.status.in_([ClaimStatusEnum.approved, ClaimStatusEnum.partial]),
    ).all()
    total_earned_rs = sum(c.payout_amount_paise for c in all_paid) / 100

    return WorkerDashboard(
        worker           = worker,
        active_policy    = active_policy,
        recent_claims    = recent_claims,
        total_earned_rs  = round(total_earned_rs, 2),
        claims_this_week = len(recent_claims),
        is_protected     = active_policy is not None,
    )


# ─── All Workers (Admin) ──────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=list[WorkerResponse],
    summary="[Admin] List all registered workers",
)
def list_all_workers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Chandini uses this for the admin workers list."""
    return db.query(Worker).offset(skip).limit(limit).all()
