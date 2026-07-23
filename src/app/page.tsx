import { db } from "@/db";
import { sql } from "drizzle-orm";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  let dbStatus = "checking";
  try {
    await db.execute(sql`select 1`);
    dbStatus = "connected";
  } catch {
    dbStatus = "not configured (set DATABASE_URL)";
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-red-50 via-white to-orange-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-red-600 to-red-700 rounded-xl flex items-center justify-center text-white font-bold">N</div>
            <div>
              <h1 className="font-bold text-gray-900">NagVijay NSMS</h1>
              <p className="text-xs text-gray-500">India Post • Enterprise Platform</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className={`px-3 py-1 rounded-full text-xs font-medium border ${dbStatus === "connected" ? "bg-green-50 text-green-700 border-green-200" : "bg-amber-50 text-amber-700 border-amber-200"}`}>
              DB: {dbStatus}
            </span>
            <span className="px-3 py-1 rounded-full text-xs font-medium bg-red-50 text-red-700 border border-red-200">MVP v1.0.0</span>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* Hero */}
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <div>
            <div className="inline-flex px-3 py-1 bg-red-50 border border-red-200 rounded-full text-xs font-medium text-red-700 mb-4">
              Nagpur City Division • Scalable to National
            </div>
            <h1 className="text-5xl font-bold leading-tight text-gray-900">
              Smart Monitoring for <span className="text-red-600">India Post</span>
            </h1>
            <p className="mt-6 text-lg text-gray-600 leading-relaxed">
              Enterprise platform for Nagpur City Division. Unified office master, employee tracking, target engine with Google Forms/Sheets sync, AI insights via Gemini, and n8n automation. Built for 150 offices now, scalable to 150k+ nationally.
            </p>
            
            <div className="mt-8 grid grid-cols-3 gap-4">
              <div className="bg-white rounded-xl p-4 border shadow-sm">
                <p className="text-2xl font-bold text-gray-900">150</p>
                <p className="text-xs text-gray-500">Offices • HO/SO/BO</p>
              </div>
              <div className="bg-white rounded-xl p-4 border shadow-sm">
                <p className="text-2xl font-bold text-gray-900">8+</p>
                <p className="text-xs text-gray-500">Schemes • PLI/RPLI/SSA</p>
              </div>
              <div className="bg-white rounded-xl p-4 border shadow-sm">
                <p className="text-2xl font-bold text-gray-900">AI</p>
                <p className="text-xs text-gray-500">Gemini + n8n</p>
              </div>
            </div>

            <div className="mt-8 flex flex-wrap gap-3">
              <a href="/api/health" className="px-6 py-3 bg-red-600 text-white rounded-xl font-medium hover:bg-red-700 transition-colors">Check Health API</a>
              <a href="https://github.com" className="px-6 py-3 bg-white border rounded-xl font-medium hover:bg-gray-50 transition-colors">View Repository Structure</a>
            </div>

            <div className="mt-8 p-4 bg-amber-50 border border-amber-200 rounded-xl">
              <p className="text-sm font-medium text-amber-900">📦 Complete Repository Generated</p>
              <p className="text-xs text-amber-800 mt-1">Backend: FastAPI + Python 3.13 async • Frontend: React Vite TS • Supabase PG • Google OAuth • Gemini AI • n8n • Docker • Railway</p>
              <p className="text-xs text-amber-700 mt-2">Structure: backend/app/api, core, models, schemas, services, integrations... frontend/src/components, pages, services... docs, docker, .github/workflows</p>
            </div>
          </div>

          <div className="space-y-6">
            {/* Tech Stack */}
            <div className="bg-white rounded-2xl p-6 border shadow-[0_24px_60px_rgba(16,24,40,0.08)]">
              <h3 className="font-semibold text-gray-900">Tech Stack • Production Ready</h3>
              <div className="mt-4 grid grid-cols-2 gap-3 text-xs">
                <div className="p-3 bg-gray-50 rounded-xl"><p className="font-medium">Backend</p><p className="text-gray-500">FastAPI, Python 3.13, async, SQLAlchemy, Pydantic v2</p></div>
                <div className="p-3 bg-gray-50 rounded-xl"><p className="font-medium">Frontend</p><p className="text-gray-500">React 18, Vite 5, TS 5.6, Tailwind, TanQuery, Zustand</p></div>
                <div className="p-3 bg-gray-50 rounded-xl"><p className="font-medium">Database</p><p className="text-gray-500">Supabase PostgreSQL 15, RLS, Realtime</p></div>
                <div className="p-3 bg-gray-50 rounded-xl"><p className="font-medium">Auth</p><p className="text-gray-500">Google OAuth + JWT (access 15m, refresh 7d)</p></div>
                <div className="p-3 bg-gray-50 rounded-xl"><p className="font-medium">AI</p><p className="text-gray-500">Gemini 1.5 Flash, RAG, anomaly detection</p></div>
                <div className="p-3 bg-gray-50 rounded-xl"><p className="font-medium">Automation</p><p className="text-gray-500">n8n webhooks, APScheduler, Google Sheets/Forms</p></div>
              </div>
            </div>

            {/* Features */}
            <div className="bg-gray-900 rounded-2xl p-6 text-white">
              <h3 className="font-semibold">✅ Features Implemented</h3>
              <div className="mt-4 grid grid-cols-2 gap-2 text-xs text-gray-300">
                <span>✓ Google Login + JWT</span><span>✓ RBAC 5 roles</span>
                <span>✓ Office Master (HO/SO/BO)</span><span>✓ Employee Master</span>
                <span>✓ Target Engine</span><span>✓ Forms/Sheets Sync</span>
                <span>✓ Dashboard + Analytics</span><span>✓ Reports (PDF/Excel)</span>
                <span>✓ AI Chatbot (Gemini)</span><span>✓ Notifications + Realtime</span>
                <span>✓ Audit Logs</span><span>✓ Health + Settings</span>
                <span>✓ Scheduler</span><span>✓ Supabase CRUD</span>
              </div>
              <p className="mt-4 text-[10px] text-gray-400">After GitHub upload: 1. Add env vars 2. Connect Railway 3. Connect Supabase 4. Google OAuth 5. Run project</p>
            </div>
          </div>
        </div>

        {/* Repository Structure */}
        <div className="mt-16 bg-white rounded-2xl border p-8">
          <h2 className="text-2xl font-bold">📁 Complete Repository Structure</h2>
          <div className="mt-6 grid md:grid-cols-2 lg:grid-cols-4 gap-6 text-xs font-mono">
            <div>
              <p className="font-bold text-gray-900">backend/</p>
              <p className="text-gray-600">main.py<br/>app/core/config, database, security, logging, exceptions<br/>app/api/v1/auth, offices, employees, targets, analytics, reports, ai...<br/>app/models/user, office, employee, target, audit, notification<br/>app/schemas/...<br/>app/services/...<br/>app/repositories/...<br/>app/integrations/supabase, google_oauth, forms, sheets, gemini, n8n<br/>app/middleware, dependencies, validators, tasks, utils</p>
            </div>
            <div>
              <p className="font-bold text-gray-900">frontend/</p>
              <p className="text-gray-600">src/main.tsx, App.tsx<br/>src/components/ProtectedRoute<br/>src/pages/Dashboard, OfficeMaster, EmployeeMaster, Targets, Analytics, Reports, AIChat, Settings, Notifications<br/>src/layouts/MainLayout, AuthLayout<br/>src/services/api, authStore<br/>src/hooks/useDebounce<br/>vite.config.ts, tailwind.config.js<br/>package.json</p>
            </div>
            <div>
              <p className="font-bold text-gray-900">infra & docs</p>
              <p className="text-gray-600">Dockerfile (multi-stage)<br/>docker/backend.Dockerfile, frontend.Dockerfile, nginx.conf<br/>docker-compose.yml (postgres, redis, backend, frontend, n8n)<br/>railway.json<br/>.github/workflows/deploy.yml (lint, test, docker, railway)<br/>docs/ARCHITECTURE, API, DEPLOYMENT, SCALING<br/>scripts/setup.sh, migrate.sh<br/>tests/backend/test_health.py</p>
            </div>
            <div>
              <p className="font-bold text-gray-900">Root</p>
              <p className="text-gray-600">README.md (complete)<br/>LICENSE (MIT)<br/>.gitignore<br/>.env.example (all blank)<br/>requirements.txt<br/>package.json (Next.js for verification + frontend separate)<br/>Next.js src/app/page.tsx (this page) for preview<br/>src/db/schema.ts (Drizzle)</p>
            </div>
          </div>
        </div>
      </div>

      <footer className="mt-16 border-t bg-white">
        <div className="max-w-7xl mx-auto px-6 py-8 flex flex-col md:flex-row justify-between gap-4 text-sm text-gray-500">
          <div>
            <p className="font-medium text-gray-900">NagVijay Smart Monitoring System • India Post</p>
            <p className="text-xs mt-1">MVP Phase: Nagpur City Division • Next: Nagpur Region → Maharashtra Circle → India Post</p>
          </div>
          <div className="text-xs">
            <p>Backend: /api/v1/health • /api/docs (when DEBUG=True)</p>
            <p>Frontend: /dashboard (after auth) • Built for Railway + Supabase + Google OAuth + Gemini</p>
          </div>
        </div>
      </footer>
    </main>
  );
}
