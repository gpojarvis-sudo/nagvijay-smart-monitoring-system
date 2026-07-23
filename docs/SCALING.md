# Scaling Roadmap

## Current MVP: Nagpur City Division
- 1 HO, 35 SO, 114 BO = 150 offices
- ~400 employees
- Single region

## Scaling Challenges
- Office hierarchy depth
- Target allocation complexity
- Achievement volume (daily per employee)
- Analytics queries on large datasets

## Phase 2: Nagpur Region (600 offices)
- Add region filter everywhere
- Index optimization
- Redis for dashboard cache (5 min TTL)
- Pagination everywhere

## Phase 3: Maharashtra Circle (5000 offices)
- Read replica for analytics
- Materialized views for KPIs
- Separate audit log archival (S3)
- Bulk operations via background jobs (Celery)

## Phase 4: National (150k offices)
- Partitioning: by circle (list partitioning)
- Sharding: by circle ID
- CQRS: Write DB (OLTP) + Read DB (OLAP - ClickHouse)
- Microservices: Office service, Target service, Employee service, AI service
- Kubernetes with auto-scaling
- CDN + edge caching
- Full-text search via Elasticsearch for office/employee search

## Multi-Tenancy
- Column division/region/circle in every table
- RLS policies: user can only see own division unless SUPER_ADMIN
- Frontend division switcher for SUPER_ADMIN

## Performance Tips Implemented
- Async everywhere (SQLAlchemy async, FastAPI async)
- Connection pooling (pool_size 10, max_overflow 20)
- Pagination with total count
- Denormalized achievement percentages
- Indexed foreign keys
