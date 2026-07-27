"""
Scheduler - APScheduler for background jobs
"""
from __future__ import annotations

from typing import Optional

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()

scheduler: Optional[AsyncIOScheduler] = None


def init_scheduler() -> AsyncIOScheduler:
    global scheduler
    
    if scheduler and scheduler.running:
        logger.warning("scheduler_already_running")
        return scheduler
    
    scheduler = AsyncIOScheduler(
        job_defaults={
            "coalesce": True,
            "max_instances": 1,
            "misfire_grace_time": 300,  # 5 min grace
        },
        timezone="Asia/Kolkata",
    )
    
    # Register jobs
    _register_jobs(scheduler)
    
    scheduler.start()
    logger.info("scheduler_started", jobs=len(scheduler.get_jobs()))
    return scheduler


def _register_jobs(sched: AsyncIOScheduler):
    """Register all scheduled jobs"""
    
    from app.tasks.daily_summary_task import generate_daily_summary
from app.tasks.sync_tasks import (
        daily_target_rollover,
        sync_google_sheets,
        cleanup_audit_logs,
        send_daily_reports,
        check_pending_verifications,
    )
    
    # Daily at 6 AM IST - Target rollover
    sched.add_job(
        daily_target_rollover,
        CronTrigger(hour=6, minute=0),
        id="daily_target_rollover",
        name="Daily Target Rollover",
        replace_existing=True,
    )
    
    # Every 2 hours - Google Sheets sync
    if settings.ENABLE_GOOGLE_SHEETS_SYNC:
        sched.add_job(
            sync_google_sheets,
            IntervalTrigger(hours=2),
            id="sheets_sync",
            name="Google Sheets Sync",
            replace_existing=True,
        )
    
    # Daily at 7 AM IST - Daily reports
    sched.add_job(
        send_daily_reports,
        CronTrigger(hour=7, minute=0),
        id="daily_reports",
        name="Send Daily Reports",
        replace_existing=True,
    )
    
    # Every hour - Check pending verifications
    sched.add_job(
        check_pending_verifications,
        IntervalTrigger(hours=1),
        id="pending_verifications",
        name="Check Pending Verifications",
        replace_existing=True,
    )
    
    # Daily at 8 PM IST - Generate daily summary
    sched.add_job(
        generate_daily_summary,
        CronTrigger(hour=20, minute=0),
        id="daily_summary",
        name="Generate Daily Summary",
        replace_existing=True,
    )
    
    # Weekly Sunday 2 AM - Cleanup old audit logs (keep 90 days)
    sched.add_job(
        cleanup_audit_logs,
        CronTrigger(day_of_week="sun", hour=2, minute=0),
        id="audit_cleanup",
        name="Cleanup Audit Logs",
        replace_existing=True,
    )
    
    logger.info("scheduler_jobs_registered", jobs=[j.id for j in sched.get_jobs()])


def shutdown_scheduler():
    global scheduler
    if scheduler and scheduler.running:
        scheduler.shutdown()
        logger.info("scheduler_shutdown")
        scheduler = None


def get_scheduler() -> Optional[AsyncIOScheduler]:
    return scheduler
