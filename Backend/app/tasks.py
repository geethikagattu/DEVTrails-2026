import logging
from uuid import UUID
from datetime import datetime
from celery.utils.log import get_task_logger

from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.models import Claim, ClaimStatusEnum, Payout, PayoutStatusEnum
from app.services.ml_service import run_anomaly_detection
from app.services.ml_service import run_anomaly_detection

logger = get_task_logger(__name__)

@celery_app.task(name="app.tasks.poll_weather_data")
def poll_weather_data():
    """
    Periodic task to check weather/AQI for all active zones.
    If a threshold is crossed, it creates claims.
    """
    logger.info("🌤️ Initiating periodic weather/trigger check...")
    # existing logic (this function currently does the check and creates claims)
    # in Phase 3, we'll make it more granular per zone
    # Import locally to avoid circular dependency with trigger_engine.py
    from app.services.trigger_engine import run_trigger_check
    run_trigger_check()
    return "Weather check completed"

@celery_app.task(name="app.tasks.process_claim_fraud_check")
def process_claim_fraud_check(claim_id_str: str):
    """
    Analyzes signals for a specific claim using ML models.
    """
    claim_id = UUID(claim_id_str)
    db = SessionLocal()
    try:
        claim = db.query(Claim).filter(Claim.id == claim_id).first()
        if not claim:
            logger.error(f"Claim {claim_id} not found")
            return

        logger.info(f"🔍 Running Phase 3 Fraud Check for Claim {claim_id}")
        
        # ML Logic (Isolation Forest / GNN placeholder)
        fraud_score = run_anomaly_detection(str(claim_id), db)
        
        # update claim with AI score
        claim.fraud_score = fraud_score
        
        # Decision Tiers:
        if fraud_score < 0.3:
            claim.status = ClaimStatusEnum.approved
        elif fraud_score < 0.7:
            claim.status = ClaimStatusEnum.partial
        else:
            claim.status = ClaimStatusEnum.flagged
            
        claim.processed_at = datetime.utcnow()
        db.commit()

        if claim.status in [ClaimStatusEnum.approved, ClaimStatusEnum.partial]:
            # Trigger payout
            initiate_payout.delay(str(claim_id))
            
    except Exception as e:
        logger.error(f"Error processing fraud check: {e}")
        db.rollback()
    finally:
        db.close()

@celery_app.task(name="app.tasks.initiate_payout")
def initiate_payout(claim_id_str: str):
    """
    Mock Razorpay/UPI payout integration.
    """
    claim_id = UUID(claim_id_str)
    db = SessionLocal()
    try:
        claim = db.query(Claim).filter(Claim.id == claim_id).first()
        if not claim or claim.status != ClaimStatusEnum.approved:
            return

        logger.info(f"💸 Initiating Payout for Claim {claim_id}")
        
        # Record payout attempt
        payout = Payout(
            claim_id=claim_id,
            razorpay_txn_id=f"pay_mock_{datetime.now().strftime('%Y%m%d%H%M')}",
            status=PayoutStatusEnum.success,
            retry_count=0
        )
        db.add(payout)
        
        # Update claim with ref
        claim.payout_upi_ref = payout.razorpay_txn_id
        db.commit()
        
        # Send Notification
        send_push_notification.delay(str(claim.worker_id), f"Payout Sent: ₹{claim.payout_amount_paise/100:.2f} credited for {claim.trigger_label}")

    except Exception as e:
        logger.error(f"Error initiating payout: {e}")
        db.rollback()
    finally:
        db.close()

@celery_app.task(name="app.tasks.send_push_notification")
def send_push_notification(worker_id_str: str, message: str):
    """
    Mock Firebase Cloud Messaging (FCM) sender.
    """
    logger.info(f"🔔 Notification to Worker {worker_id_str}: {message}")
    # In Phase 3 implementation, we would use firebase_admin here
    return True
