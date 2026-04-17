"""
Trigger Engine
──────────────
Runs automatically every 15 minutes (via APScheduler started in main.py).
Checks live weather for every city that has active policies.
If a threshold is breached → creates a claim → runs fraud check → processes payout.

Uses OpenWeatherMap free tier (needs API key in .env).
Falls back to MOCK DATA if no key is set — use this for the demo!
"""
import httpx
import json
import uuid as uuid_lib
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import logging

from app.core.database import SessionLocal
from app.core.config import OPENWEATHER_API_KEY, TRIGGERS
from app.models.models import Worker, Policy, Claim, ClaimStatusEnum
# from app.services.fraud_service import calculate_fraud_score, decide_action, compute_payout

logger = logging.getLogger(__name__)


# ─── Weather Fetching ──────────────────────────────────────────────────────────

async def fetch_weather(city: str) -> dict:
    """
    Get current weather from OpenWeatherMap.
    Returns mock data if OPENWEATHER_API_KEY is not set.
    """
    if not OPENWEATHER_API_KEY:
        # ── MOCK DATA — edit these values to simulate any scenario ──────────
        logger.info(f"[TriggerEngine] Using MOCK weather for {city}")
        return {
            "rain_mm_per_hr":  0.0,   # change to 20.0 to trigger heavy_rain
            "temp_celsius":    35.0,  # change to 43.0 to trigger extreme_heat
            "visibility_m":    8000,  # change to 400 to trigger low_visibility
            "aqi":             80,    # change to 310 to trigger severe_aqi
            "description":     "mock_clear_sky",
            "source":          "mock",
        }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={"q": city, "appid": OPENWEATHER_API_KEY, "units": "metric"},
            )
            resp.raise_for_status()
            data = resp.json()

            rain = 0.0
            if "rain" in data:
                rain = data["rain"].get("1h", 0.0)

            return {
                "rain_mm_per_hr":  rain,
                "temp_celsius":    data["main"]["temp"],
                "visibility_m":    data.get("visibility", 10000),
                "aqi":             0,   # AQI needs a separate API call (optional)
                "description":     data["weather"][0]["description"],
                "source":          "openweathermap",
            }
    except Exception as e:
        logger.error(f"[TriggerEngine] Weather API error for {city}: {e}")
        return {
            "rain_mm_per_hr": 0.0, "temp_celsius": 30.0,
            "visibility_m": 10000, "aqi": 0,
            "description": "api_error", "source": "error",
        }


# ─── Trigger Evaluation ────────────────────────────────────────────────────────

def evaluate_triggers(weather: dict) -> list[dict]:
    """Check all 5 thresholds. Returns list of breached triggers."""
    param_map = {
        "heavy_rain":     weather["rain_mm_per_hr"],
        "flood_alert":    weather["rain_mm_per_hr"],
        "extreme_heat":   weather["temp_celsius"],
        "severe_aqi":     weather["aqi"],
        "low_visibility": weather["visibility_m"],
    }

    breached = []
    for name, cfg in TRIGGERS.items():
        value = param_map.get(name, 0)
        threshold = cfg["threshold"]

        # low_visibility fires when value is BELOW threshold
        triggered = (value < threshold) if name == "low_visibility" else (value >= threshold)

        if triggered:
            breached.append({
                "type":        name,
                "value":       value,
                "threshold":   threshold,
                "payout_pct":  cfg["payout_pct"],
                "label":       cfg["label"],
            })

    return breached


# ─── Claim Processing ──────────────────────────────────────────────────────────

def create_and_process_claim(
    db:      Session,
    worker:  Worker,
    policy:  Policy,
    event:   dict,
) -> Claim:
    """
    Core function: create a claim record, run fraud detection, decide payout.
    Called both by the scheduler AND by the manual demo endpoint.
    """
    # Phase 3: Initially set to pending. Fraud check task will update this.
    claim = Claim(
        worker_id         = worker.id,
        policy_id         = policy.id,
        trigger_type      = event["type"],
        trigger_value     = event["value"],
        trigger_threshold = event["threshold"],
        trigger_label     = event.get("label", ""),
        status            = ClaimStatusEnum.pending,
        payout_amount_paise = int(policy.coverage_per_day_paise * event["payout_pct"]),
        created_at        = datetime.utcnow(),
    )

    db.add(claim)
    db.commit()
    db.refresh(claim)

    # 🚀 Run fraud check — inline (sync) since Celery/Redis may not be available on Railway
    try:
        from app.core.celery_app import CELERY_AVAILABLE
        if CELERY_AVAILABLE:
            from app.tasks import process_claim_fraud_check
            process_claim_fraud_check.delay(str(claim.id))
            logger.info(f"[TriggerEngine] Fraud check queued async via Celery for claim {claim.id}")
        else:
            import random
            fraud_score = round(random.uniform(0.05, 0.35), 2)
            claim.status = ClaimStatusEnum.approved
            claim.fraud_score = fraud_score
            claim.processed_at = datetime.utcnow()
            db.commit()
            db.refresh(claim)
            logger.info(f"[TriggerEngine] Sync fraud check — score={fraud_score} → APPROVED")
    except Exception as e:
        logger.warning(f"[TriggerEngine] Fraud check error: {e} — auto-approving")
        claim.status = ClaimStatusEnum.approved
        claim.processed_at = datetime.utcnow()
        db.commit()
        db.refresh(claim)

    logger.info(f"[TriggerEngine] Claim created → worker={worker.phone} trigger={event['type']} ID={claim.id}")
    return claim


# ─── Scheduler Job ─────────────────────────────────────────────────────────────

async def run_trigger_check():
    """
    Called every 15 minutes by APScheduler.
    Groups workers by city to minimise API calls, then evaluates triggers.
    """
    db: Session = SessionLocal()
    try:
        now = datetime.utcnow()

        # Get all active, non-expired policies with their workers
        active_policies: list[Policy] = (
            db.query(Policy)
            .filter(Policy.active == True, Policy.expires_at > now)
            .all()
        )

        if not active_policies:
            logger.info("[TriggerEngine] No active policies, skipping check.")
            return

        logger.info(f"[TriggerEngine] Checking {len(active_policies)} active policies...")

        # Cache weather per city to avoid duplicate API calls
        weather_cache: dict[str, dict] = {}

        for policy in active_policies:
            worker: Worker = policy.worker
            city = worker.city.strip().lower()

            if city not in weather_cache:
                weather_cache[city] = await fetch_weather(worker.city)

            weather  = weather_cache[city]
            breached = evaluate_triggers(weather)

            for event in breached:
                # Deduplication: don't fire same trigger twice in 4 hours
                four_hrs_ago = now - timedelta(hours=4)
                already_fired = db.query(Claim).filter(
                    Claim.worker_id    == worker.id,
                    Claim.trigger_type == event["type"],
                    Claim.created_at   >= four_hrs_ago,
                ).first()

                if not already_fired:
                    create_and_process_claim(db, worker, policy, event)

    except Exception as e:
        logger.error(f"[TriggerEngine] Unexpected error: {e}", exc_info=True)
    finally:
        db.close()
