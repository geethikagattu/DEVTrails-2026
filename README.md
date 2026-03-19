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
# 🛡️ Adversarial Defense & Anti-Spoofing Strategy

> **Emergency Architecture Update — Phase 1 Final 24 Hours**
> In response to a confirmed threat: a coordinated syndicate of 500+ delivery workers
> using GPS-spoofing apps to trigger false parametric payouts. ShieldRun's response below.

---

## 1. Differentiation: Genuine Worker vs. GPS Spoofer

Simple GPS coordinates are a single point of truth — and a single point of failure.
ShieldRun replaces GPS-only verification with a **Multi-Signal Behavioral Fingerprint**
that a spoofer cannot fake all at once.

### The Core Insight
A delivery worker genuinely stranded in a red-alert weather zone will produce a
**consistent behavioral signature** across multiple data streams simultaneously.
A bad actor sitting at home spoofing GPS will fail to replicate this signature across
even 2–3 of these signals.

### Signal Stack (7 Layers)

| Layer | Signal | Genuine Worker | Spoofer at Home |
|---|---|---|---|
| 1 | GPS coordinates | Inside affected zone | Spoofed to zone |
| 2 | **Device accelerometer** | Near-zero movement (sheltering) OR erratic (riding in rain) | Stationary flat-line |
| 3 | **Network cell tower ID** | Tower physically inside affected zone | Home area tower |
| 4 | **Battery drain rate** | Higher (GPS + rain screen usage) | Normal home rate |
| 5 | **Platform API activity** | Last order accepted near zone, then halted | No recent order history |
| 6 | **Device mock location flag** | OFF | Often ON (Android dev mode) |
| 7 | **Historical zone presence** | Regularly delivers in this zone | Never or rarely present |

**Decision:** A claim passes fraud validation only if it satisfies **≥ 5 of 7 signals**.
Failing 3+ signals triggers the flagged review queue, not an auto-rejection.

---

## 2. Data Points: Detecting a Coordinated Fraud Ring

Individual spoofers are hard to catch. **Coordinated rings are easy** — because
coordination itself leaves patterns. ShieldRun monitors the following at the
**population level**, not just the individual claim level.

### Ring Detection Data Points

**A. Claim Surge Velocity**
- If >15% of active policyholders in a single pincode file claims within a 12-minute
  window, a **Surge Alert** is automatically triggered.
- Genuine disruptions cause gradual claim increases. Coordinated fraud causes
  simultaneous spikes.

**B. Telegram / Social Coordination Proxy**
- We monitor the **inter-claim time gap distribution** across a zone.
- Organic claims: randomly distributed over 30–90 minutes.
- Coordinated claims: tightly clustered (all within 5–8 minutes) — a statistical
  fingerprint of group messaging coordination.

**C. Device Fingerprint Clustering**
- If multiple claims originate from devices with identical:
  - Android build version
  - Screen resolution
  - Installed VPN or mock GPS app signatures
- These are flagged as a **Device Cluster Anomaly**.

**D. Weather-Claim Correlation Mismatch**
- Our system cross-references the claimed disruption severity against hyperlocal
  weather station data at 500m resolution.
- If 300 workers claim a "red alert" trigger but the weather API shows only 18mm/hr
  rainfall (below our 35mm threshold) — all claims in that batch are auto-held.

**E. Zone Presence History Score**
- Every worker has a Zone Presence Score built from their 90-day delivery history.
- A worker claiming to be stranded in Dharavi who has never delivered in Dharavi
  scores 0/100 on zone legitimacy — automatically escalated.

### ML Model: Ring Detection
- **Algorithm:** Graph Neural Network (GNN) on claim relationship graph
- **Nodes:** Individual claims
- **Edges:** Shared device fingerprints, overlapping GPS timestamps, same pincode
- **Output:** Ring Probability Score (0–1). Score >0.80 = entire cluster held for
  human review.

---

## 3. UX Balance: Protecting Honest Workers During Flags

The biggest risk of aggressive fraud detection is **false positives** — honest workers
denied payouts during the exact moment they need help most. ShieldRun's philosophy:

> **"Flag for review, never punish upfront."**

### The Three-Tier Response System

**Tier 1 — Auto-Approved (≥5/7 signals pass)**
- Payout hits UPI in <60 seconds.
- No friction. No notification beyond "Payout Sent ✅"

**Tier 2 — Soft Flag (3–4/7 signals pass)**
- Worker receives an immediate partial advance payout (40% of claim value)
  credited within 60 seconds — so they are not left with nothing.
- A lightweight verification is triggered in the background:
  - One-tap confirmation: "Are you currently in [Zone Name]?" with a real photo
    upload option (not mandatory — optional for faster full clearance).
  - Full payout released within 2 hours if no contradicting evidence surfaces.
- Worker notification: *"Your claim is being fast-tracked. ₹240 advance credited.
  Full amount arriving shortly."* — no mention of "fraud" or "flagged."

**Tier 3 — Hard Flag (<3/7 signals pass OR Ring Score >0.80)**
- No payout issued yet.
- Worker is notified: *"We're verifying your claim due to high activity in your zone.
  This usually resolves in 4 hours."*
- A human reviewer from the ShieldRun ops team is assigned within 30 minutes.
- If verified legitimate: full payout + ₹50 inconvenience bonus credited.
- If confirmed fraud: claim rejected, policy flagged, repeat offenders permanently
  blacklisted.

### Network Drop Protection
A genuine worker in a storm may experience connectivity loss — meaning their
accelerometer, cell tower, and platform signals may not transmit in real time.

**Solution: Offline Signal Buffering**
- The ShieldRun PWA stores sensor data locally for up to 4 hours.
- When connectivity is restored, the buffered signal history is transmitted and
  evaluated retroactively.
- Workers are never penalized for network drops caused by the same disruption
  they're claiming for.

### Appeals Process
- Any rejected claim can be appealed in 1 tap from the worker dashboard.
- Appeals are reviewed within 24 hours by a human agent.
- Wrongful rejections trigger a full payout + formal apology notification.
- Appeal outcome data feeds back into the ML model to reduce future false positives.

---

## Summary: Why This Architecture is Spoof-Proof

| Attack Vector | ShieldRun Defense |
|---|---|
| Single GPS spoof | 7-layer signal stack — GPS is 1 of 7 |
| Coordinated Telegram ring | Surge velocity + inter-claim timing analysis |
| Fake device location (mock GPS app) | Android dev mode flag detection |
| Mass claims in low-rainfall event | Weather-claim correlation mismatch check |
| New worker claiming unfamiliar zone | 90-day Zone Presence History Score |
| Honest worker caught in false positive | Soft flag → partial advance → auto-clear |
| Network drop during genuine disruption | Offline signal buffering + retroactive eval |

> ShieldRun doesn't just detect fraud. It does so without making honest workers
> collateral damage. That's the design principle that separates us.


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
