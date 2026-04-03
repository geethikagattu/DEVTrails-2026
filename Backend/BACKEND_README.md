# ShieldRun Backend — Phase 2

AI-powered parametric income insurance for Zomato/Swiggy delivery partners.

## Project Structure

```
shieldrun/
├── app/
│   ├── main.py                    ← Entry point (Geethika)
│   ├── api/routes/
│   │   ├── workers.py             ← Registration + dashboard APIs
│   │   ├── policies.py            ← Premium quote + purchase APIs
│   │   └── claims.py              ← Claims view + admin + demo trigger
│   ├── core/
│   │   ├── database.py            ← DB connection
│   │   └── config.py              ← Thresholds + env vars
│   ├── models/models.py           ← DB tables (Worker, Policy, Claim)
│   ├── schemas/schemas.py         ← Request/response shapes
│   └── services/
│       ├── premium_service.py     ← AI premium calculator (Akash owns)
│       ├── fraud_service.py       ← Fraud scoring (Akash owns)
│       └── trigger_engine.py     ← Auto weather trigger (Geethika owns)
├── requirements.txt
├── Procfile                       ← Railway deployment
└── railway.toml
```

## Setup (Local)

```bash
# 1. Clone and go into the backend folder
cd shieldrun

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy env file and fill in values
cp .env.example .env
# Edit .env: add your DATABASE_URL and OPENWEATHER_API_KEY

# 5. Run the server
uvicorn app.main:app --reload
```

Server runs at: http://localhost:8000  
Swagger docs at: http://localhost:8000/docs  ← USE THIS TO TEST ALL APIS

## Deploy to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

railway login
railway init
railway add postgres        # adds free PostgreSQL
railway up                  # deploys the backend
```

## Key API Endpoints

| Method | Endpoint | What it does |
|--------|----------|-------------|
| POST | `/api/v1/workers/register` | Register new worker |
| GET | `/api/v1/workers/by-phone/{phone}` | Login by phone |
| GET | `/api/v1/workers/{id}/dashboard` | Worker home screen data |
| POST | `/api/v1/policies/quote/all?worker_id=` | Get all 3 plan quotes |
| POST | `/api/v1/policies/purchase` | Buy a plan |
| GET | `/api/v1/claims/worker/{id}` | Worker's claim history |
| POST | `/api/v1/claims/demo/trigger` | 🎬 Fire a fake trigger (DEMO) |
| GET | `/api/v1/claims/admin/dashboard` | Admin dashboard stats |

## Demo Flow (for the 2-minute video)

1. Register a worker → `POST /workers/register`
2. Get quotes → `GET /policies/quote/all?worker_id=<id>`
3. Buy premium plan → `POST /policies/purchase`
4. Fire fake rainstorm → `POST /claims/demo/trigger` with `{"trigger_type": "heavy_rain", "trigger_value": 40.0}`
5. Show claim auto-approved → `GET /claims/worker/<id>`
6. Show admin dashboard → `GET /claims/admin/dashboard`

## Team Contacts

- **Geethika** — Backend, trigger engine, deployment
- **Saniya** — Worker-facing frontend (React)
- **Chandini** — Admin dashboard frontend (React)
- **Akash** — ML premium model, fraud scoring

## Frontend API Base URL

Set this in your React `.env`:
```
VITE_API_BASE_URL=https://your-railway-url.railway.app
```
