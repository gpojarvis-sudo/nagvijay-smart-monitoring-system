# Deployment - Railway

## Prerequisites
- GitHub repo connected
- Railway account
- Supabase project
- Google Cloud project with OAuth + Sheets + Forms API enabled
- Gemini API key from AI Studio
- n8n instance (optional)

## Steps

### 1. Railway Setup
```bash
railway login
railway link
railway up
```
Or via dashboard: New Project -> Deploy from GitHub.

Railway auto-detects Dockerfile (multi-stage: frontend build + backend).

### 2. Environment Variables (Railway Dashboard -> Variables)
Add all from .env.example:
- DATABASE_URL (from Supabase)
- SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY
- JWT_SECRET_KEY (generate 32+ chars)
- GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI
- GEMINI_API_KEY
- N8N_WEBHOOK_URL (if using n8n)
- FRONTEND_URL, BACKEND_URL, CORS_ORIGINS (set to Railway URLs)

### 3. Supabase
- Create tables via SQL editor (or let SQLAlchemy create_all)
- Enable RLS policies
- Set up Auth if needed (but we use Google OAuth + JWT)
- Get connection string for DATABASE_URL (use pooled for production)

### 4. Google OAuth
- Google Cloud Console -> APIs & Services -> Credentials
- Create OAuth 2.0 Client ID (Web)
- Authorized JS origins: your frontend URL, http://localhost:5173
- Authorized redirect URIs: backend URL + /api/v1/auth/google/callback
- Enable People API, Sheets API, Forms API

### 5. Google Sheets Integration
- Create service account, download JSON
- Share sheets with service account email
- Set GOOGLE_SHEETS_CREDENTIALS_JSON as stringified JSON in env

### 6. Frontend
- Frontend is built into Docker image's /frontend/dist and served via FastAPI? Actually Dockerfile copies dist but backend serves API only. For production, deploy frontend separately on Vercel/Railway static, or nginx.
- Alternative: Use two Railway services - backend (Docker) and frontend (Node). Set VITE_API_URL to backend URL.

### 7. Health Check
- Railway uses healthcheckPath: /api/v1/health from railway.json
- Verify logs

### 8. Custom Domain
- Railway -> Settings -> Domains -> Add custom domain

## Docker Local
```bash
docker-compose up --build
```

## CI/CD
- .github/workflows/deploy.yml handles lint, test, build, docker check, and railway deploy on main push if RAILWAY_TOKEN set.
- Set RAILWAY_TOKEN in GitHub Secrets.
