#!/usr/bin/env python3
"""
Controlled Migration: Insert targets and allocations for all offices and schemes.
Run: python scripts/insert_targets_and_allocations.py
"""
import asyncio
import sys
import uuid
from datetime import datetime, timezone, date
from sqlalchemy import select, func
from app.core.database import AsyncSessionLocal
from app.models.target import Scheme, Target, TargetAllocation
from app.models.office import Office


async def migrate():
    print("\n" + "="*60)
    print("📦 TARGET & ALLOCATION MIGRATION (SCHEMA-ALIGNED)")
    print("="*60 + "\n")

    async with AsyncSessionLocal() as session:
        # 1. Get all active schemes
        schemes = await session.execute(select(Scheme).where(Scheme.is_active == True))
        schemes = schemes.scalars().all()
        if not schemes:
            print("❌ No active schemes found. Please insert schemes first.")
            return
        print(f"✅ Found {len(schemes)} active schemes.")

        # 2. Get all active offices
        offices = await session.execute(select(Office).where(Office.status == 'ACTIVE'))
        offices = offices.scalars().all()
        if not offices:
            print("❌ No active offices found.")
            return
        print(f"✅ Found {len(offices)} active offices.")

        financial_year = "2024-25"
        division = "Nagpur City"
        region = "Nagpur"

        # Financial year start and end dates (e.g., 1 April 2024 to 31 March 2025)
        start_date = date(2024, 4, 1)
        end_date = date(2025, 3, 31)

        total_target_base = 1000  # Default target value; adjust as needed

        for scheme in schemes:
            # Check if target already exists
            existing_target = await session.execute(
                select(Target).where(
                    Target.scheme_id == scheme.id,
                    Target.division == division,
                    Target.financial_year == financial_year
                )
            )
            target = existing_target.scalar_one_or_none()
            if target:
                print(f"⏭️ Target already exists for {scheme.scheme_code} (FY {financial_year}). Skipping.")
                continue

            target_id = str(uuid.uuid4())
            # Create target with all required fields
            target = Target(
                id=target_id,
                scheme_id=scheme.id,
                financial_year=financial_year,
                division=division,
                region=region,
                total_target=total_target_base,
                period_type="YEARLY",
                start_date=start_date,
                end_date=end_date,
                status="ALLOCATED",   # This matches TargetStatus enum
                total_achieved=0.0,
                achievement_percentage=0.0,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            session.add(target)
            await session.flush()
            print(f"✅ Created target for {scheme.scheme_code} (ID: {target_id})")

            # Distribute target among offices
            per_office = total_target_base // len(offices) if offices else 0
            remainder = total_target_base % len(offices) if offices else 0

            for idx, office in enumerate(offices):
                allocated = per_office + (1 if idx < remainder else 0)
                # Check if allocation already exists
                existing_alloc = await session.execute(
                    select(TargetAllocation).where(
                        TargetAllocation.target_id == target_id,
                        TargetAllocation.office_id == office.id
                    )
                )
                if existing_alloc.scalar_one_or_none():
                    continue
                alloc_id = str(uuid.uuid4())
                allocation = TargetAllocation(
                    id=alloc_id,
                    target_id=target_id,
                    scheme_id=scheme.id,
                    office_id=office.id,
                    allocated_target=allocated,
                    financial_year=financial_year,
                    status="ALLOCATED",
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                session.add(allocation)
            print(f"   → Created {len(offices)} allocations for {scheme.scheme_code}")

        await session.commit()
        print("\n✅ Migration complete. Targets and allocations inserted.")

if __name__ == "__main__":
    asyncio.run(migrate())
