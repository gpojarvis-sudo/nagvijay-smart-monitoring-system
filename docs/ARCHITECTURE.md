# Architecture - NagVijay Smart Monitoring System

## Overview
Enterprise platform for India Post, starting with Nagpur City Division (150 offices), scalable to National (150k+ offices).

## Layers

### Frontend (React + Vite + TS)
- Component-based with TailwindCSS
- State: Zustand for auth, TanStack Query for server state
- Routing: React Router v6 protected routes
- Charts: Recharts
- Auth: Google OAuth GIS + JWT

### Backend (FastAPI + Python 3.13 Async)
- Layered: API → Service → Repository → Model (SQLAlchemy async)
- Dependencies: Auth + RBAC
- Middleware: Logging + Security Headers + CORS
- Integrations: Supabase, Google OAuth, Gemini, n8n, Sheets/Forms

### Database (Supabase PostgreSQL 15)
- Tables: users, offices, employees, schemes, targets, allocations, achievements, audit_logs, notifications
- RLS policies for multi-tenancy
- Realtime for notifications

### AI (Gemini 1.5 Flash)
- Context-aware chatbot with dashboard KPIs as context
- Anomaly detection
- Report summarization

### Automation (n8n)
- Webhooks for notifications, reports, sheets sync
- Scheduler via APScheduler (daily rollover, verification checks)

## Scaling Strategy

### Phase 1: Nagpur City (MVP) - 150 offices, 500 users
- Single Railway instance, Supabase free tier
- Direct DB queries

### Phase 2: Nagpur Region - 600 offices, 2000 users
- Read replicas, Redis cache
- Pagination, indexed queries
- CDN for frontend

### Phase 3: Maharashtra Circle - 5000 offices, 20k users
- Horizontal scaling (Railway replicas)
- Supabase pooling
- CQRS for analytics (materialized views)

### Phase 4: National - 150k offices, 500k users
- Sharding by circle/region
- Dedicated analytics DB (ClickHouse/Timescale)
- Microservices split: Office, Employee, Target, AI
- Kubernetes

## Security
- JWT short-lived + refresh rotation
- RBAC with hierarchy
- Audit logs immutable
- CORS restricted
- Security headers

## Deployment
- Railway with Dockerfile multi-stage
- Health checks at /api/v1/health
- GitHub Actions CI/CD
