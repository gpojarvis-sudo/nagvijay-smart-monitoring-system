# Nagvijay Smart Monitoring System - MASTER CONTEXT

## PROJECT STATUS
**Current Phase:** POST-IMPLEMENTATION ✅  
**Next Phase:** OPTIONAL ENHANCEMENTS (AI, Alerts, Frontend improvements)

## COMPLETED WORK (All Phases)
1. **Backend Architecture** – FastAPI, SQLAlchemy Async, Supabase PostgreSQL.
2. **Authentication** – JWT with Google OAuth and employee_id login.
3. **Google Sheets Integration** – Sync 66 offices daily data to `daily_office_reports`.
4. **Google Forms Webhook** – Receives form responses, stores data, logs errors.
5. **DailyOfficeReport Model** – Complete schema with unique constraint on (office_id, report_date).
6. **Non-Reporting Offices API** – `GET /api/v1/daily-reports/non-reporting`.
7. **Report Export** – CSV/JSON export for any date.
8. **Error Logging** – `SyncError` model with `SYNC` and `WEBHOOK` error types.
9. **Duplicate Detection** – Logs duplicate submissions to `sync_errors` table.
10. **Scheduler** – APScheduler with jobs: target rollover (6 AM), Sheets sync (every 2h), daily reports (7 AM), daily summary (8 PM), pending verifications (hourly), audit cleanup (weekly).
11. **Frontend Dashboard** – Displays office count (66), daily summary, non-reporting offices, and performance metrics.
12. **Database Fix** – Switched to Supabase Session Pooler (port 6543) for Render compatibility.

## FINAL ARCHITECTURE DECISIONS
- **Google Form is the only input source.**
- **Responses Sheet is the permanent audit log.**
- **Dashboard reads ONLY from PostgreSQL.**
- **`office_name` is the primary business identifier (backed by `office_code`).**
- **Unique constraint on `(office_id, report_date)` prevents duplicates.**
- **Errors are logged to `sync_errors` table for monitoring and debugging.**
- **Scheduler runs in Asia/Kolkata timezone.**

## DO NOT REPEAT
- All models, APIs, and integrations are verified and working.
- No further debugging or inspection required.

## NEXT STEPS (Optional Enhancements)
- **Frontend**: Add a card to display recent `sync_errors` (duplicate alerts).
- **AI Insights**: Integrate Gemini/Cloudflare for anomaly detection.
- **Email Alerts**: Send notifications for non-reporting offices.
- **Back-Date Validation**: Optionally reject future dates (if required).

## SYNC SUMMARY (Tested)
- Parsed 67 rows from Google Sheets.
- Synced 66 offices, skipped 1 header row.
- Sample: Nagpur GPO | 2026-07-28 | SB Opened: 10.
- Duplicate detection logs errors to `sync_errors`.
- Webhook returns `{"success":true}` for valid submissions.

## FRONTEND ACCESS
- Production URL: `https://nagvijay-smart-monitoring-system-1.onrender.com`
- Login: `employee_id=12345678`, `password=Admin@123`
- Dashboard includes "Non-Reporting Offices" card.

## ENVIRONMENT VARIABLES (Render)
- `DATABASE_URL` – Supabase Session Pooler (port 6543)
- `GOOGLE_FORMS_WEBHOOK_SECRET` – `my_secret_key_123`
- `CORS_ORIGINS` – Frontend Render URL
- `VITE_API_URL` – Backend Render URL

