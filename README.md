# NagVijay Smart Monitoring System (NSMS)

**Enterprise Monitoring Platform for India Post - Nagpur City Division**

> MVP Phase - Scalable to Nagpur Region, Maharashtra Circle, and Pan-India Post

![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/Python-3.13%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-green)
![React](https://img.shields.io/badge/React-18%2B-61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![Railway](https://img.shields.io/badge/Deployed%20on-Railway-purple)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Repository Structure](#repository-structure)
- [Quick Start](#quick-start)
- [Environment Variables](#environment-variables)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)
- [Security](#security)
- [Contributing](#contributing)
- [License](#license)

## 🏛 Overview

NagVijay Smart Monitoring System (NSMS) is an enterprise-grade monitoring and management platform designed for India Post operations. Initially targeting Nagpur City Division, the system is architected to scale across Nagpur Region, Maharashtra Circle, and eventually Pan-India.

### Core Objectives

- **Unified Office Management**: Centralized master for all post offices, branch offices, and administrative units
- **Employee Performance Tracking**: Role-based employee master with hierarchical reporting
- **Target vs Achievement Engine**: Real-time tracking of postal schemes, PLI, RPLI, business targets
- **Automation**: Google Forms/Sheets integration for field data collection, n8n workflows
- **AI Insights**: Gemini-powered chatbot for analytics, anomaly detection, and report summarization
- **Audit & Compliance**: Full audit trail for every transaction

## 🏗 Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  React + Vite   │────▶│   FastAPI API    │────▶│  Supabase PG    │
│  Frontend       │◀────│   Backend        │◀────│  Database       │
└─────────────────┘     └──────────────────┘     └─────────────────┘
        │                        │                        │
        │                        ├────▶ Gemini API (AI)    │
        │                        ├────▶ Google OAuth      │
        │                        ├────▶ Google Forms/Sheets│
        │                        └────▶ n8n Webhooks      │
        │                                                
        └────▶ Railway Deployment (Docker)
```

### Multi-Tenancy Ready

- Division → Region → Circle → National hierarchy
- Row-level security via Supabase RLS
- Role-based access control (Super Admin, Division Admin, Office Admin, Employee, Auditor)

## 💻 Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Backend** | FastAPI | 0.110+ |
| | Python | 3.13 |
| | Uvicorn | Async |
| | Pydantic v2 | Validation |
| | SQLAlchemy 2.0 | Async ORM |
| **Frontend** | React | 18.3 |
| | Vite | 5.x |
| | TypeScript | 5.6 |
| | TailwindCSS | 3.4 |
| | Tanstack Query | 5.x |
| | Zustand | State |
| **Database** | Supabase PostgreSQL | 15 |
| | Supabase Auth | |
| | Supabase Realtime | |
| **Auth** | JWT (PyJWT) | |
| | Google OAuth2 | |
| **AI** | Google Gemini 1.5 Flash | |
| **Automation** | n8n Webhooks | |
| **Deployment** | Railway | |
| | Docker | Multi-stage |
| **Monitoring** | Structlog | |
| | Health Checks | |

## ✨ Features

### 🔐 Authentication & Authorization
- Google OAuth2 login
- JWT access + refresh tokens (15m / 7d)
- RBAC: 5 roles with granular permissions
- Secure httpOnly cookies + Bearer fallback

### 🏢 Office Master
- CRUD for HO, SO, BO, Administrative Offices
- Pincode, beat, jurisdiction mapping
- Hierarchy tree view
- Bulk import via CSV/Sheets

### 👥 Employee Master
- Employee profile, designation, DOJ, category
- Office mapping, reporting manager
- Transfer history, deputation tracking
- Document uploads (Supabase Storage)

### 🎯 Target Engine
- Scheme master (PLI, RPLI, SSA, TD, Business)
- Division/Office/Employee level target allocation
- Daily/Monthly/Quarterly achievement entry
- Auto calculation of % achievement, gap analysis
- Google Forms integration for field submission
- Google Sheets real-time sync

### 📊 Dashboard & Analytics
- KPI cards: Total offices, employees, targets, achievement %
- Charts: Recharts - bar, pie, trend, heatmap
- Filters: Date range, office type, division, scheme
- Top performers / Laggards

### 📄 Reports
- Daily Performance Report (DPR)
- Monthly Consolidated
- Office-wise, Employee-wise, Scheme-wise
- Export to PDF (jsPDF) and Excel (xlsx)
- Scheduled email reports via n8n

### 🤖 AI Chatbot
- Gemini-powered assistant
- Natural language queries: "Show low performing BOs in Nagpur East"
- Anomaly detection
- Report summarization
- Context-aware with RAG over office/employee data

### 🔔 Notifications
- In-app notifications (Realtime)
- Email via n8n + SMTP
- Achievement milestones, target deadlines
- System alerts

### ⚙️ Automation & Integrations
- **Google Forms**: Webhook receiver, auto-parse submissions to targets
- **Google Sheets**: Two-way sync for bulk updates
- **n8n**: Workflow triggers for notifications, reports, sync jobs
- **Scheduler**: APScheduler for daily jobs (target rollover, reminder)

### 📝 Audit Logs
- Every CREATE/UPDATE/DELETE logged
- User, timestamp, IP, old/new values
- Immutable logs table, retention policy

### ❤️ Health & Settings
- `/api/v1/health` comprehensive check: DB, Supabase, Gemini, n8n
- Admin settings for division config, financial year, target cycles

## 📁 Repository Structure

```
nagvijay-smart-monitoring-system/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── app/
│       ├── api/v1/ (auth, offices, employees, targets, analytics, reports, ai, health...)
│       ├── core/ (config, database, security, logging, exceptions)
│       ├── models/ (SQLAlchemy models)
│       ├── schemas/ (Pydantic schemas)
│       ├── repositories/ (Data access layer)
│       ├── services/ (Business logic)
│       ├── middleware/
│       ├── dependencies/
│       ├── validators/
│       ├── integrations/ (supabase, google oauth, forms, sheets, gemini, n8n)
│       ├── constants/
│       ├── tasks/
│       └── utils/
├── frontend/
│   ├── src/
│   │   ├── components/ (ui, forms, charts, layout)
│   │   ├── pages/ (Dashboard, OfficeMaster, EmployeeMaster, Targets, Reports...)
│   │   ├── hooks/
│   │   ├── services/ (api clients)
│   │   ├── layouts/
│   │   ├── assets/
│   │   └── styles/
│   ├── vite.config.ts
│   └── package.json
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── SCALING.md
├── docker/
│   ├── backend.Dockerfile
│   └── frontend.Dockerfile
├── .github/workflows/deploy.yml
├── tests/
├── scripts/
├── Dockerfile (multistage)
├── docker-compose.yml
├── railway.json
├── .env.example
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- Node 20+
- Supabase account
- Google Cloud project (OAuth + Sheets + Forms API enabled)
- Gemini API Key
- n8n instance (optional, for automation)

### 1. Clone

```bash
git clone https://github.com/your-org/nagvijay-smart-monitoring-system.git
cd nagvijay-smart-monitoring-system
```

### 2. Environment Setup

```bash
cp .env.example .env
# Fill all values - see Environment Variables section
```

### 3. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs at: http://localhost:8000
Docs at: http://localhost:8000/api/docs

### 4. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend at: http://localhost:5173

### 5. Docker (Full Stack)

```bash
docker-compose up --build
```

## 🔑 Environment Variables

See `.env.example` for full list. Never commit `.env`.

| Variable | Description |
|----------|-------------|
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key |
| `SUPABASE_ANON_KEY` | Anon key for frontend |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | OAuth secret |
| `JWT_SECRET_KEY` | 32+ char secret |
| `GEMINI_API_KEY` | Google AI Studio key |
| `N8N_WEBHOOK_URL` | n8n webhook base |
| `DATABASE_URL` | Postgres connection string |

## 🚢 Deployment (Railway)

1. Connect GitHub repo to Railway
2. Add services: Backend (Python), Frontend (Node), Postgres (or use Supabase)
3. Set environment variables in Railway dashboard
4. Railway auto-detects `railway.json` and `Dockerfile`
5. Deploy:

```bash
railway login
railway link
railway up
```

Detailed: `docs/DEPLOYMENT.md`

## 📚 API Documentation

- Swagger: `/api/docs` (only in dev/debug)
- ReDoc: `/api/redoc`
- OpenAPI JSON: `/api/openapi.json`

### Key Endpoints

- `POST /api/v1/auth/google` - Google OAuth
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/offices` - List offices (paginated, filtered)
- `POST /api/v1/targets/allocate` - Allocate targets
- `POST /api/v1/integrations/forms/webhook` - Google Forms webhook
- `POST /api/v1/ai/chat` - AI assistant

## 🔒 Security

- JWT with short expiry, refresh rotation
- Bcrypt password hashing (for fallback)
- CORS restricted to frontend origin
- Rate limiting (slowapi)
- Security headers (HSTS, CSP, X-Frame-Options)
- Input validation via Pydantic + sanitization
- RLS policies in Supabase
- Audit logs immutable

## 🧪 Testing

```bash
# Backend
cd backend
pytest tests/ -v --cov=app

# Frontend
cd frontend
npm run test
```

## 📈 Scaling Roadmap

- **Phase 1 (MVP)**: Nagpur City Division (150 offices)
- **Phase 2**: Nagpur Region (600+ offices)
- **Phase 3**: Maharashtra Circle (5000+ offices)
- **Phase 4**: National (150k+ offices) - Sharding, Read replicas, CDN

See `docs/SCALING.md`

## 🤝 Contributing

1. Fork
2. Feature branch: `feat/offices-bulk-import`
3. Commit: Conventional commits
4. PR with tests

## 📄 License

MIT License - See LICENSE file.

---

**Built for India Post** 📮 | **NagVijay Team** | **2026**
