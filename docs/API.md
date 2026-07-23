# API Documentation - NSMS

Base URL: `/api/v1`

## Auth
- `POST /auth/google` - Google ID token -> JWT pair
- `POST /auth/refresh` - Refresh tokens
- `GET /auth/me` - Current user
- `POST /auth/logout`
- `GET /auth/google/url` - Get OAuth redirect URL

## Offices
- `GET /offices` - List with pagination, search, filters (office_type, division)
- `GET /offices/stats` - Stats by type, status, division
- `GET /offices/{id}`
- `POST /offices` - Requires OFFICE_CREATE
- `PUT /offices/{id}` - Requires OFFICE_UPDATE
- `DELETE /offices/{id}` - Requires OFFICE_DELETE
- `POST /offices/bulk-import` - Bulk

## Employees
- `GET /employees`, `GET /employees/stats`, `GET /employees/{id}`, `POST`, `PUT`, `DELETE`

## Targets
- `GET /targets/schemes`, `POST /targets/schemes`
- `GET /targets`, `POST /targets`, `GET /targets/{id}`
- `GET /targets/{id}/allocations`, `POST /targets/allocations`, `POST /targets/{id}/allocations/bulk`
- `GET /targets/achievements/list`, `POST /targets/achievements`

## Analytics
- `GET /analytics/dashboard?division=Nagpur City&financial_year=2024-25`
- `GET /analytics/kpis`
- `GET /analytics/trends`

## Reports
- `POST /reports/generate`
- `GET /reports/dpr`, `GET /reports/monthly`, `GET /reports/export`

## AI
- `POST /ai/chat` - { message, conversation_id, context }
- `GET /ai/anomalies`
- `GET /ai/health`

## Notifications
- `GET /notifications`, `PUT /notifications/{id}/read`, `PUT /notifications/read-all`

## Integrations
- `POST /integrations/forms/webhook` - Public, X-Webhook-Secret header
- `GET /integrations/sheets/status`, `POST /integrations/sheets/read`
- `POST /integrations/n8n/trigger`
- `GET /integrations/status`

## Health
- `GET /health` - Comprehensive
- `GET /health/ready`, `GET /health/live`

## Settings
- `GET /settings` - Requires SETTINGS_MANAGE
- `GET /settings/frontend-config` - Public
- `GET /settings/audit` - Audit logs

## Response Format
Success:
```json
{
  "success": true,
  "data": {},
  "pagination": { "total": 100, "page": 1, "page_size": 20 }
}
```
Error:
```json
{
  "success": false,
  "error": { "code": "NOT_FOUND", "message": "...", "details": {} },
  "timestamp": 1234567890,
  "path": "/api/v1/offices/123"
}
```
