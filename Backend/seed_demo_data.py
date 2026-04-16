"""
ShieldRun Phase 3 — Demo Data Seeder
Run this ONCE before your demo video to populate the system with realistic data.

Usage:
    cd Backend
    source venv/bin/activate
    python seed_demo_data.py
"""
import uuid
import json
import bcrypt
from datetime import datetime, timedelta
from app.core.database import SessionLocal
from app.models.models import (
    Worker, Policy, Claim, ClaimStatusEnum,
    Signal, FraudRing, Payout, PayoutStatusEnum
)

def hash_pw(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

db = SessionLocal()

print("🌱 Seeding ShieldRun demo data...")

# ─── 1. Workers ───────────────────────────────────────────────────────────────
workers_data = [
    {"name": "Ravi Kumar",     "phone": "+919876543210", "zone": "500001", "city": "Hyderabad", "platform": "zomato",  "platform_id": "ZOM-RK-9821"},
    {"name": "Priya Sharma",   "phone": "+919876543211", "zone": "500002", "city": "Hyderabad", "platform": "swiggy",  "platform_id": "SWY-PS-4432"},
    {"name": "Arjun Reddy",    "phone": "+919876543212", "zone": "500003", "city": "Hyderabad", "platform": "zomato",  "platform_id": "ZOM-AR-7744"},
    {"name": "Meena Devi",     "phone": "+919876543213", "zone": "500004", "city": "Hyderabad", "platform": "swiggy",  "platform_id": "SWY-MD-1122"},
    {"name": "Suresh Babu",    "phone": "+919876543214", "zone": "500008", "city": "Hyderabad", "platform": "zomato",  "platform_id": "ZOM-SB-3388"},
    {"name": "Lakshmi Prasad", "phone": "+919876543215", "zone": "500033", "city": "Hyderabad", "platform": "swiggy",  "platform_id": "SWY-LP-9933"},
    {"name": "Kiran Rao",      "phone": "+919876543216", "zone": "500001", "city": "Hyderabad", "platform": "zomato",  "platform_id": "ZOM-KR-7711"},
    {"name": "Anita Naik",     "phone": "+919876543217", "zone": "500002", "city": "Hyderabad", "platform": "swiggy",  "platform_id": "SWY-AN-5544"},
]

worker_objs = []
for w in workers_data:
    existing = db.query(Worker).filter(Worker.phone == w["phone"]).first()
    if existing:
        worker_objs.append(existing)
        print(f"  → Worker {w['name']} already exists, skipping.")
        continue

    worker = Worker(
        id=uuid.uuid4(),
        name=w["name"],
        phone=w["phone"],
        city=w["city"],
        zone_pincode=w["zone"],
        platform=w["platform"],
        platform_id=w["platform_id"],
        upi_id=f"upi_{w['phone'][-4:]}@okaxis",
        avg_daily_earnings=500.0,
    )
    db.add(worker)
    worker_objs.append(worker)
    print(f"  ✓ Worker created: {w['name']}")

db.commit()

# ─── 2. Policies ──────────────────────────────────────────────────────────────
plans = [
    {"plan": "basic",    "base": 2900,  "weekly": 2900,  "coverage": 20000, "max": 20000},
    {"plan": "standard", "base": 4900,  "weekly": 4900,  "coverage": 40000, "max": 40000},
    {"plan": "premium",  "base": 7900,  "weekly": 7900,  "coverage": 80000, "max": 80000},
]

policy_objs = []
for i, worker in enumerate(worker_objs):
    existing = db.query(Policy).filter(Policy.worker_id == worker.id, Policy.active == True).first()
    if existing:
        policy_objs.append(existing)
        continue

    plan = plans[i % len(plans)]
    policy = Policy(
        id=uuid.uuid4(),
        worker_id=worker.id,
        plan=plan["plan"],
        base_premium_paise=plan["base"],
        weekly_premium_paise=plan["weekly"],
        coverage_per_day_paise=plan["coverage"],
        max_weekly_payout_paise=plan["max"],
        active=True,
        activated_at=datetime.utcnow() - timedelta(days=10),
        expires_at=datetime.utcnow() + timedelta(days=20),
    )
    db.add(policy)
    policy_objs.append(policy)
    print(f"  ✓ Policy [{plan['plan'].upper()}] for {worker.name}")

db.commit()

# ─── 3. Historical Claims (Mix of approved/flagged/partial) ───────────────────
historical_events = [
    {"type": "heavy_rain",  "value": 42.5, "threshold": 15.0, "pct": 0.8, "label": "Heavy Rainfall ≥15mm/hr", "days_ago": 12, "status": ClaimStatusEnum.approved, "fraud": 0.05},
    {"type": "heavy_rain",  "value": 38.0, "threshold": 15.0, "pct": 0.8, "label": "Heavy Rainfall ≥15mm/hr", "days_ago": 10, "status": ClaimStatusEnum.approved, "fraud": 0.08},
    {"type": "flood_alert", "value": 57.2, "threshold": 35.0, "pct": 1.0, "label": "Flood Alert ≥35mm/hr",    "days_ago": 8,  "status": ClaimStatusEnum.approved, "fraud": 0.12},
    {"type": "severe_aqi",  "value": 325,  "threshold": 300,  "pct": 0.6, "label": "Hazardous AQI >300",      "days_ago": 7,  "status": ClaimStatusEnum.partial,  "fraud": 0.55},
    {"type": "heavy_rain",  "value": 29.0, "threshold": 15.0, "pct": 0.8, "label": "Heavy Rainfall ≥15mm/hr", "days_ago": 5,  "status": ClaimStatusEnum.flagged,  "fraud": 0.82},  # GPS Spoof
    {"type": "extreme_heat","value": 44.5, "threshold": 42.0, "pct": 0.5, "label": "Extreme Heat Alert",      "days_ago": 4,  "status": ClaimStatusEnum.approved, "fraud": 0.10},
    {"type": "heavy_rain",  "value": 51.3, "threshold": 15.0, "pct": 0.8, "label": "Heavy Rainfall ≥15mm/hr", "days_ago": 2,  "status": ClaimStatusEnum.approved, "fraud": 0.06},
    {"type": "flood_alert", "value": 43.1, "threshold": 35.0, "pct": 1.0, "label": "Flood Alert ≥35mm/hr",    "days_ago": 1,  "status": ClaimStatusEnum.approved, "fraud": 0.09},
]

payout_count = 0
for i, event in enumerate(historical_events):
    worker = worker_objs[i % len(worker_objs)]
    policy = policy_objs[i % len(policy_objs)]
    created = datetime.utcnow() - timedelta(days=event["days_ago"])
    payout_amount = int(policy.coverage_per_day_paise * event["pct"])

    claim = Claim(
        id=uuid.uuid4(),
        worker_id=worker.id,
        policy_id=policy.id,
        trigger_type=event["type"],
        trigger_value=event["value"],
        trigger_threshold=event["threshold"],
        trigger_label=event["label"],
        status=event["status"],
        fraud_score=event["fraud"],
        payout_amount_paise=payout_amount,
        created_at=created,
        processed_at=created + timedelta(seconds=12),
    )
    db.add(claim)
    db.flush()

    # Add telemetry signal for each claim
    signal = Signal(
        id=uuid.uuid4(),
        claim_id=claim.id,
        gps=f"{worker.zone_pincode},real" if event["fraud"] < 0.5 else f"0.0,0.0,SPOOFED",
        accelerometer="vibration_level: 0.85" if event["fraud"] < 0.5 else "no_movement",
        battery="78%",
        mock_flag=(event["fraud"] > 0.5),
    )
    db.add(signal)

    if event["status"] == ClaimStatusEnum.approved:
        payout = Payout(
            id=uuid.uuid4(),
            claim_id=claim.id,
            razorpay_txn_id=f"pay_RZP_{str(claim.id)[:8].upper()}",
            status=PayoutStatusEnum.success,
            retry_count=0,
            created_at=created + timedelta(seconds=15),
        )
        db.add(payout)
        payout_count += 1
        print(f"  ✓ [{event['status'].value.upper()}] Claim: {event['label']} — ₹{payout_amount/100} paid")
    else:
        print(f"  ⚠️  [{event['status'].value.upper()}] Claim: {event['label']} — fraud_score={event['fraud']}")

db.commit()

# ─── 4. One Fraud Ring ────────────────────────────────────────────────────────
flagged_claims = db.query(Claim).filter(Claim.fraud_score > 0.5).all()
if flagged_claims and len(flagged_claims) >= 2:
    existing_ring = db.query(FraudRing).first()
    if not existing_ring:
        ring = FraudRing(
            cluster_id=uuid.uuid4(),
            claim_ids=json.dumps([str(c.id) for c in flagged_claims[:3]]),
            ring_score=0.87,
            detected_at=datetime.utcnow() - timedelta(hours=3),
        )
        db.add(ring)
        db.commit()
        print("  🕸️  Fraud ring cluster created with score 0.87")

print(f"""
✅ Done! Database seeded successfully.

📊 Summary:
   Workers:       {len(worker_objs)}
   Policies:      {len(policy_objs)}
   Claims:        {len(historical_events)} (mix of approved/flagged/partial)
   Payouts:       {payout_count}
   Fraud Rings:   1

🎬 Your platform is now demo-ready. Start recording!
""")

db.close()
