#!/usr/bin/env python3
"""
Data Integrity Audit Script
Run: python scripts/check_data_integrity.py
"""
import asyncio
import sys
from datetime import datetime, timedelta
from sqlalchemy import select, func, text
from app.core.database import AsyncSessionLocal
from app.models.office import Office
from app.models.daily_office_report import DailyOfficeReport
from app.models.sync_error import SyncError


async def audit():
    print("\n" + "="*60)
    print("🔍 DATA INTEGRITY AUDIT")
    print("="*60 + "\n")

    async with AsyncSessionLocal() as session:
        # 1. Office count
        office_count = await session.execute(select(func.count()).select_from(Office))
        total_offices = office_count.scalar()
        print(f"✅ Total Offices: {total_offices}")

        # 2. Office type breakdown
        type_result = await session.execute(
            select(Office.office_type, func.count(Office.id))
            .group_by(Office.office_type)
        )
        print("   Office types:")
        for typ, cnt in type_result:
            print(f"      {typ}: {cnt}")

        # 3. Daily report records per date (last 7 days)
        seven_days_ago = datetime.now(timezone.utc).date() - timedelta(days=7)
        date_result = await session.execute(
            select(DailyOfficeReport.report_date, func.count(DailyOfficeReport.id))
            .where(DailyOfficeReport.report_date >= seven_days_ago)
            .group_by(DailyOfficeReport.report_date)
            .order_by(DailyOfficeReport.report_date.desc())
        )
        print("\n📅 Recent daily report counts:")
        for dt, cnt in date_result:
            print(f"   {dt}: {cnt} offices")

        # 4. Duplicate check (should be zero)
        dup_result = await session.execute(
            text("""
                SELECT office_id, report_date, COUNT(*)
                FROM daily_office_reports
                GROUP BY office_id, report_date
                HAVING COUNT(*) > 1
            """)
        )
        duplicates = dup_result.all()
        if duplicates:
            print("\n⚠️ DUPLICATES FOUND (should not happen):")
            for row in duplicates:
                print(f"   office_id={row[0]}, date={row[1]}, count={row[2]}")
        else:
            print("\n✅ No duplicate records found in daily_office_reports.")

        # 5. Foreign key integrity
        fk_result = await session.execute(
            text("""
                SELECT COUNT(*)
                FROM daily_office_reports dor
                LEFT JOIN offices o ON dor.office_id = o.id
                WHERE o.id IS NULL
            """)
        )
        orphan_count = fk_result.scalar()
        if orphan_count > 0:
            print(f"\n⚠️ {orphan_count} orphaned daily report records (office_id missing).")
        else:
            print("\n✅ All daily reports have valid office_id references.")

        # 6. Recent errors
        error_result = await session.execute(
            select(SyncError)
            .order_by(SyncError.created_at.desc())
            .limit(5)
        )
        errors = error_result.scalars().all()
        print("\n🔴 Recent sync/webhook errors (latest 5):")
        if errors:
            for e in errors:
                print(f"   [{e.created_at.strftime('%Y-%m-%d %H:%M')}] {e.error_type}: {e.error_message[:60]}...")
        else:
            print("   No errors logged recently.")

        # 7. Summary
        print("\n" + "="*60)
        print("✅ Audit complete.")
        print("="*60)

if __name__ == "__main__":
    asyncio.run(audit())
