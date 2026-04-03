"""
Premium Calculation Service  (Akash's AI brain — Geethika calls this)
─────────────────────────────────────────────────────────────────────
How it works:
  1. Base premium comes from the plan (₹29 / ₹49 / ₹79)
  2. Zone risk multiplier: pincodes with historically bad weather pay more
  3. Platform modifier: Swiggy has more night shifts → slightly higher risk
  4. Earnings modifier: workers earning more need more coverage → small surcharge

Final premium = base × zone_multiplier × platform_mod × earnings_mod
"""
from app.models.models import PlanEnum, Worker
from app.core.config import PLANS


# ─── Zone Risk Table ───────────────────────────────────────────────────────────
# multiplier > 1.0 = risky zone (surcharge)
# multiplier < 1.0 = safer zone (discount)
# Any unknown pincode defaults to 1.0 (neutral)
ZONE_RISK_MAP: dict[str, float] = {
    # Hyderabad — flood-prone areas
    "500001": 1.15, "500004": 1.20, "500018": 1.30, "500032": 1.25,
    "500034": 0.90, "500072": 1.35, "500081": 1.10, "500044": 1.05,
    # Bengaluru
    "560001": 1.00, "560034": 1.10, "560100": 0.85, "560068": 0.90,
    "560076": 1.05, "560103": 0.95,
    # Mumbai — very high flood risk
    "400001": 1.40, "400050": 1.50, "400070": 1.30, "400088": 1.45,
    "400097": 1.35,
    # Chennai
    "600001": 1.20, "600020": 1.15, "600040": 1.10, "600078": 0.95,
    # Delhi
    "110001": 1.00, "110045": 0.90, "110092": 1.05,
    # Pune
    "411001": 1.05, "411014": 1.10, "411028": 0.95,
}

PLATFORM_MODIFIER: dict[str, float] = {
    "zomato": 1.00,   # standard
    "swiggy": 1.05,   # slight surcharge for night-shift heavy profile
}


def calculate_zone_risk_score(pincode: str) -> int:
    """
    Convert the zone multiplier to a 0–100 score stored on the Worker.
    0 = safest, 100 = most risky.
    """
    multiplier = ZONE_RISK_MAP.get(pincode, 1.0)
    # Map range 0.8 → 1.5  to  0 → 100
    score = int(((multiplier - 0.8) / 0.7) * 100)
    return max(0, min(100, score))


def calculate_premium(worker: Worker, plan: str) -> dict:
    """
    Main dynamic pricing function.
    Returns a full dict that goes straight into PolicyCreate and the quote response.
    """
    plan_enum = PlanEnum(plan)
    plan_data = PLANS[plan]
    base = plan_data["weekly_premium_paise"]

    # ── Factor 1: Zone risk ──────────────────────────────────────────────────
    zone_mult = ZONE_RISK_MAP.get(worker.zone_pincode, 1.0)

    # ── Factor 2: Platform ───────────────────────────────────────────────────
    platform_mod = PLATFORM_MODIFIER.get(worker.platform.value, 1.0)

    # ── Factor 3: Earnings bracket ───────────────────────────────────────────
    earnings = worker.avg_daily_earnings
    if earnings >= 800:
        earnings_mod = 1.12    # high earner → more coverage → small surcharge
    elif earnings >= 600:
        earnings_mod = 1.05
    elif earnings <= 250:
        earnings_mod = 0.88    # low earner discount
    elif earnings <= 400:
        earnings_mod = 0.94
    else:
        earnings_mod = 1.00    # neutral (₹400–₹600 bracket)

    # ── Final calculation ────────────────────────────────────────────────────
    final_multiplier = round(zone_mult * platform_mod * earnings_mod, 4)
    adjusted_paise   = max(int(base * final_multiplier), 100)  # min ₹1

    # ── Human-readable explanation ───────────────────────────────────────────
    parts = []
    if zone_mult >= 1.2:
        parts.append(f"high flood/rain risk in pincode {worker.zone_pincode} (+{int((zone_mult-1)*100)}%)")
    elif zone_mult <= 0.95:
        parts.append(f"low-risk zone discount for {worker.zone_pincode} (-{int((1-zone_mult)*100)}%)")

    if platform_mod > 1.0:
        parts.append(f"Swiggy night-shift surcharge (+{int((platform_mod-1)*100)}%)")

    if earnings_mod > 1.0:
        parts.append(f"high earnings bracket (+{int((earnings_mod-1)*100)}%)")
    elif earnings_mod < 1.0:
        parts.append(f"low earnings discount (-{int((1-earnings_mod)*100)}%)")

    explanation = ("Standard rate — no adjustments needed." if not parts
                   else "Premium adjusted: " + "; ".join(parts) + ".")

    return {
        "plan":                     plan_enum,
        "plan_label":               plan_data["label"],
        "base_premium_paise":       base,
        "base_premium_rs":          round(base / 100, 2),
        "adjusted_premium_paise":   adjusted_paise,
        "adjusted_premium_rs":      round(adjusted_paise / 100, 2),
        "risk_multiplier":          final_multiplier,
        "coverage_per_day_paise":   plan_data["coverage_per_day_paise"],
        "coverage_per_day_rs":      round(plan_data["coverage_per_day_paise"] / 100, 2),
        "max_weekly_payout_paise":  plan_data["max_weekly_paise"],
        "max_weekly_payout_rs":     round(plan_data["max_weekly_paise"] / 100, 2),
        "risk_explanation":         explanation,
    }
