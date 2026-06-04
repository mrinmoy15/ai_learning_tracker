# ai-learning-tracker

Personal AI training progress tracker — GitHub Pages frontend + FastAPI backend + Neon PostgreSQL.

## Architecture

```
GitHub Pages (frontend/)
    └── index.html  — training plan UI with Google OAuth
         │
         │  fetch() API calls
         ▼
Cloud Run (backend/)
    └── FastAPI — auth, progress CRUD
         │
         ▼
Neon PostgreSQL — serverless, scales to zero
```

## Repo structure

```
ai-learning-tracker/
├── frontend/
│   └── index.html          ← GitHub Pages site
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/            ← auth.py, progress.py
│   │   ├── models/         ← user.py, progress.py
│   │   ├── schemas/        ← schemas.py
│   │   └── core/           ← config.py, database.py, security.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── docker-compose.yml      ← local dev with Postgres
└── .github/workflows/
    └── deploy-backend.yml  ← CI/CD to Cloud Run
```

## Local development

```bash
# 1. Copy and fill env
cp backend/.env.example backend/.env.local

# 2. Start local Postgres + API
docker compose up

# 3. Open frontend with Live Server (VS Code)
#    or: python -m http.server 5500 --directory frontend/
```

## Production setup

### 1. Neon database
1. Create account at neon.tech
2. Create a new project → copy the connection string
3. Add to Secret Manager: `tracker-db-url`

### 2. Google OAuth
1. Go to console.cloud.google.com → APIs & Services → Credentials
2. Create OAuth 2.0 Client ID (Web application)
3. Add authorised redirect URI: `https://YOUR-CLOUD-RUN-URL/auth/callback`
4. Add to Secret Manager: `tracker-google-client-id`, `tracker-google-client-secret`

### 3. JWT secret
```bash
python -c "import secrets; print(secrets.token_hex(32))"
# Add output to Secret Manager: tracker-jwt-secret
```

### 4. GitHub Secrets (for CI/CD)
```
GCP_PROJECT_ID         — your GCP project ID
WIF_PROVIDER           — Workload Identity Federation provider
WIF_SERVICE_ACCOUNT    — service account email
GH_PAGES_URL           — yourusername.github.io/ai-learning-tracker
CLOUD_RUN_HASH         — the hash part of your Cloud Run URL
```

### 5. GitHub Pages
- Repo Settings → Pages → Source: Deploy from branch → `main` → `/frontend`

### 6. Update frontend config
In `frontend/index.html`, update:
```js
const API_BASE = 'https://YOUR-CLOUD-RUN-URL';
```

## Cost

| Component | Cost |
|---|---|
| Neon PostgreSQL | Free tier (0.5 GB, scales to zero) |
| Cloud Run | ~$0 (scales to zero, free tier covers personal use) |
| GitHub Pages | Free |
| **Total** | **$0/month** |
