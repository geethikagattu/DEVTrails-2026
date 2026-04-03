import os
from dotenv import load_dotenv

load_dotenv()

# ─── Environment ───────────────────────────────────────────────────────────────
DATABASE_URL    = os.getenv("DATABASE_URL", "postgresql://postgres:jgscVhKoOFbdZqbNmEEwOSaWSjxRxmlk@maglev.proxy.rlwy.net:52400/railway")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
SECRET_KEY      = os.getenv("SECRET_KEY", "changeme-use-a-real-secret")
ENVIRONMENT     = os.getenv("ENVIRONMENT", "development")

# ─── Parametric Trigger Thresholds ────────────────────────────────────────────
# These define WHEN a claim fires automatically.
# payout_pct = fraction of daily coverage paid out (1.0 = full day, 0.5 = half day)
TRIGGERS = {
    "heavy_rain": {
        "param":      "rain_mm_per_hr",
        "threshold":  15.0,    # ≥15mm/hr triggers a claim
        "payout_pct": 1.0,     # 100% of daily coverage
        "label":      "Heavy Rain (≥15mm/hr)",
    },
    "flood_alert": {
        "param":      "rain_mm_per_hr",
        "threshold":  35.0,    # ≥35mm/hr = flood level
        "payout_pct": 1.0,
        "label":      "Flood Alert (≥35mm/hr)",
    },
    "extreme_heat": {
        "param":      "temp_celsius",
        "threshold":  42.0,    # ≥42°C = unsafe to work outdoors
        "payout_pct": 0.5,     # 50% (worker can still do some work)
        "label":      "Extreme Heat (≥42°C)",
    },
    "severe_aqi": {
        "param":      "aqi",
        "threshold":  300,     # AQI ≥300 = hazardous
        "payout_pct": 0.75,
        "label":      "Severe Air Quality (AQI ≥300)",
    },
    "low_visibility": {
        "param":      "visibility_m",
        "threshold":  500,     # <500m visibility = dense fog
        "payout_pct": 0.5,
        "label":      "Low Visibility/Dense Fog (<500m)",
    },
}

# ─── Plan Definitions ──────────────────────────────────────────────────────────
# All amounts in PAISE (₹1 = 100 paise). Stored as integers to avoid float issues.
PLANS = {
    "basic": {
        "label":                 "Basic Shield",
        "weekly_premium_paise":  2900,   # ₹29/week
        "coverage_per_day_paise":40000,  # ₹400/day
        "max_weekly_paise":      200000, # ₹2000/week max
    },
    "standard": {
        "label":                 "Standard Shield",
        "weekly_premium_paise":  4900,   # ₹49/week
        "coverage_per_day_paise":60000,  # ₹600/day
        "max_weekly_paise":      300000, # ₹3000/week max
    },
    "premium": {
        "label":                 "Premium Shield",
        "weekly_premium_paise":  7900,   # ₹79/week
        "coverage_per_day_paise":90000,  # ₹900/day
        "max_weekly_paise":      450000, # ₹4500/week max
    },
}
