# ⚡ ShieldRun — Income Protection for Every Kilometer

> **Guidewire DEVTrails 2026 | Team Submission | Phase 1**
> AI-powered parametric insurance for Zomato & Swiggy delivery partners in India.

---

##  The Problem

India has **12+ million gig delivery workers**. A Swiggy or Zomato delivery partner in Bengaluru earns roughly ₹700–900/day. When a monsoon hits, an AQI spike grounds them, or a local strike shuts down zones — they lose income immediately, with zero safety net.

**Real scenario:**
> Arjun, a Swiggy partner in Bengaluru, earns ₹820/day across 8 hours. On a heavy rain day (July 2024), deliveries halted for 5 hours. He lost ₹512 with no recourse — no claim process, no payout, nothing. ShieldRun would have detected the rainfall trigger automatically and credited ₹480 to his UPI within 60 seconds. No paperwork. No waiting.

Currently, no insurance product addresses **income loss from environmental/social disruptions** for gig workers on a weekly, affordable basis.

---

##  Our Solution: ShieldRun

ShieldRun is a **mobile-first, AI-enabled parametric insurance platform** that:
- Onboards food delivery workers in under 2 minutes
- Profiles their risk using AI/ML (zone, weather history, delivery hours)
- Offers weekly coverage plans starting at ₹29/week
- Monitors real-time parametric triggers (weather, AQI, curfews)
- Auto-initiates claims and pays out to UPI — no manual filing needed
- Detects and blocks fraudulent claims using intelligent anomaly detection

---

##  Persona: Food Delivery Partner (Zomato / Swiggy)

**Who they are:**
- Age: 20–38, male-dominated workforce
- Income: ₹600–1,000/day, operates in 6–10 hour shifts
- Device: Android smartphone, limited storage, low-to-mid data plan
- Pain point: Income is entirely dependent on being able to ride. Anything that stops riding = zero income.

**Persona-based scenarios:**

| Scenario | Trigger | Income Lost | ShieldRun Response |
|---|---|---|---|
| Heavy monsoon in Mumbai | Rainfall > 35mm/hr | 4–6 hrs of earnings | Auto-payout within 60 sec |
| Severe pollution in Delhi | AQI > 300 | Full day halted | Auto-payout for covered hours |
| Heatwave in Hyderabad | Temp > 44°C | Reduced working hours | Partial payout based on severity |
| Local bandh / curfew | Verified zone alert | Full day halted | Auto-payout after validation |
| Platform outage (Swiggy app down) | API health check fails | Lost order hours | Auto-payout after 30-min threshold |

**Application Workflow:**

```
Worker Downloads PWA
        ↓
Onboarding (Phone + Swiggy/Zomato ID + Zone)
        ↓
AI Risk Profiling (Zone Risk Score generated)
        ↓
Weekly Plan Selection (₹29 / ₹49 / ₹79)
        ↓
Policy Activated — Real-time Monitoring Begins
        ↓
Parametric Trigger Detected (e.g., Rainfall > 35mm/hr)
        ↓
AI Fraud Validation (GPS check, claim pattern, duplicate check)
        ↓
Claim Auto-Approved → UPI Payout in < 60 seconds
        ↓
Worker Dashboard Updated — Earnings Protected shown
```

---

##  Weekly Premium Model

Gig workers operate week-to-week. Our pricing mirrors that reality.

### Premium Tiers

| Plan | Weekly Premium | Coverage Per Disruption Day | Max Weekly Payout | Best For |
|---|---|---|---|---|
|  Basic | ₹29/week | ₹400 | ₹800 | Part-time workers |
|  Standard | ₹49/week | ₹600 | ₹1,200 | Full-time workers |
|  Premium | ₹79/week | ₹900 | ₹1,800 | High-earner zones |

### AI-Driven Dynamic Pricing

The base weekly premium is **dynamically adjusted** by our ML risk model using:

| Factor | Effect on Premium |
|---|---|
| Zone flood/waterlogging history | +₹5 to +₹15/week |
| Worker's avg daily hours (>8hrs) | -₹3/week (low-risk pattern) |
| Past claim frequency | +₹8 if >2 claims/month |
| City pollution index (seasonal) | +₹4 to +₹10/week in winter |
| New worker (no history) | Base rate, no adjustment |

> Example: A Swiggy partner in Dharavi (high flood risk zone) on Standard plan pays ₹49 + ₹12 zone premium = **₹61/week**. A partner in a low-risk Pune suburb pays **₹44/week**.

### Why Weekly?
Gig workers don't think monthly. They earn daily, budget weekly. A ₹49/week premium is a visible, manageable cost — not a forgotten monthly deduction. Weekly renewal also lets the model re-price dynamically as seasonal risk changes.

---

##  Parametric Triggers

No manual claims. These thresholds fire automatically:

| # | Trigger | Threshold | Data Source | Payout Condition |
|---|---|---|---|---|
| 1 | Heavy Rainfall | > 35mm/hr in worker's pincode | OpenWeatherMap API (free tier) | ≥ 2 consecutive hours |
| 2 | Severe Air Pollution | AQI > 300 in worker's city | WAQI API (free tier) | ≥ 4 hours in the day |
| 3 | Extreme Heat | Temperature > 44°C | OpenWeatherMap API | ≥ 3 hours mid-shift |
| 4 | Local Curfew / Bandh | Verified zone alert | Mock alert API + admin confirmation | Full day payout |
| 5 | Platform Outage | Swiggy/Zomato API health = DOWN | Mock platform status API | > 30 min continuous outage |

---

##  AI/ML Integration Plan

### 1. Risk Scoring Model (Premium Calculation)
- **Algorithm:** Random Forest Regressor
- **Input features:** delivery zone, city, historical weather data, seasonal risk index, worker's delivery hours, past claim history
- **Output:** Zone Risk Score (0–100) → maps to premium adjustment
- **Training data:** Mock dataset of 10,000 synthetic gig worker profiles + 3 years of historical OpenWeatherMap data for Tier 1 Indian cities

### 2. Fraud Detection Model
- **Algorithm:** Isolation Forest (unsupervised anomaly detection)
- **Signals monitored:**
  - GPS location at time of claimed disruption (was worker actually in the affected zone?)
  - Mass claim spikes (>30% of workers claiming simultaneously in a zone with <20mm rainfall = flag)
  - Duplicate claim attempts within same disruption window
  - Device fingerprinting — same device filing multiple worker claims
- **Output:** Fraud Risk Score (0–1). Score > 0.75 → human review queue. Score > 0.9 → auto-reject.

### 3. Predictive Analytics (Phase 3)
- Week-ahead disruption probability forecasting per city zone
- Helps insurer pre-provision payout reserves
- Built using LSTM on historical weather + claim correlation data

---

##  Tech Stack

### Frontend
- **Framework:** React.js (PWA — no app store needed)
- **Styling:** Tailwind CSS
- **Rationale:** PWA works on low-storage Android phones without installation friction. Critical for gig worker adoption.

### Backend
- **Framework:** FastAPI (Python) — chosen for native ML model integration
- **Database:** PostgreSQL (structured policy + claims data)
- **Auth:** Phone OTP via Firebase Auth

### AI/ML
- **Stack:** Python, scikit-learn, pandas, numpy
- **Serving:** FastAPI ML endpoints
- **Models:** Random Forest (risk scoring), Isolation Forest (fraud detection)

### Integrations
| Integration | Service | Mode |
|---|---|---|
| Weather | OpenWeatherMap API | Free tier (real) |
| Air Quality | WAQI API | Free tier (real) |
| Platform status | Zomato/Swiggy | Mocked |
| Payments | Razorpay | Test mode |
| Notifications | Firebase Cloud Messaging | Free tier |

### Infrastructure
- **Frontend hosting:** Vercel (free tier)
- **Backend hosting:** Railway (free tier)
- **CI/CD:** GitHub Actions

---

##  Platform Choice: Web (PWA) vs Mobile App

**We chose Progressive Web App (PWA).**

| Factor | PWA  | Native App  |
|---|---|---|
| Storage requirement | ~2MB | ~80–150MB |
| App store approval | Not needed | 3–7 days |
| Update speed | Instant | Requires user update |
| Target device (low-mid Android) | Works perfectly | Often lags |
| Development speed | Single codebase | iOS + Android = 2x effort |

A delivery partner with a ₹8,000 phone with 8GB storage won't download another app. They will tap a WhatsApp link that opens ShieldRun instantly.

---

##  Development Plan

| Week | Milestone | Owner(s) |
|---|---|---|
| Week 1 | Repo setup, DB schema, backend skeleton, wireframes | P1, P3 |
| Week 2 | README, ML model research, mock data, risk scoring logic draft | P2, P5 |
| Week 3 | Worker onboarding UI, policy management, trigger engine (3 APIs) | P1, P3 |
| Week 4 | Fraud detection model, dynamic premium endpoint, claims UI | P2, P4 |
| Week 5 | Advanced fraud (GPS spoofing), payout simulation, admin dashboard | P1, P2, P4 |
| Week 6 | Final polish, demo video, pitch deck, submission package | P5 + all |

---

##  Team

| Member | Role |
|---|---|
| [Geethika Gattu] | Team Lead + Backend Engineer |
| [Akash Ambati] | AI/ML Engineer |
| [Saniya Hassen] | Frontend Developer (Worker PWA) |
| [Chandini Konda] | Frontend Developer (Admin Dashboard) |
| [Kusuma Nandarapu] | Full Stack + DevOps + Submissions |

---

## 🔗 Links

- **Repository:** *(https://github.com/geethikagattu/DEVTrails-2026/edit/main/README.md)*
- **Demo Video (Phase 1):** https://drive.google.com/file/d/1llNzdJ-xETvSFLIZ_f2jC9FYSMWWeZvq/view?usp=sharing
- **Live Demo:** [Link to be added — Phase 2 onwards]

---

> *ShieldRun — Because every kilometer deserves a safety net.*
