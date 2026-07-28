#!/usr/bin/env python3
"""
Controlled Migration: Insert targets and allocations for all offices and schemes.
Run: python scripts/insert_targets_and_allocations.py
"""
import asyncio
import sys
import uuid
from datetime import datetime
from sqlalchemy import select, func
from app.core.database import AsyncSessionLocal
from app.models.target import Scheme, Target, TargetAllocation
from app.models.office import Office


async def migrate():
    print("\n" + "="*60)
    print("📦 TARGET & ALLOCATION MIGRATION")
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
        circle = "Maharashtra"

        # For each scheme, create a target (if not exists)
        for scheme in schemes:
            # Check if target already exists for this scheme, division, FY
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

            # Create target
            total_target = 1000  # Default value – adjust as needed
            target_id = str(uuid.uuid4())
            target = Target(
                id=target_id,
                scheme_id=scheme.id,
                financial_year=financial_year,
                division=division,
                region=region,
                circle=circle,
                total_target=total_target,
                description=f"Default target for {scheme.scheme_name}",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(target)
            await session.flush()
            print(f"✅ Created target for {scheme.scheme_code} (ID: {target_id})")

            # Distribute total target among offices
            # Simple: equal distribution
            per_office = total_target // len(offices) if offices else 0
            remainder = total_target % len(offices) if offices else 0

            for idx, office in enumerate(offices):
                allocated = per_office + (1 if idx < remainder else 0)
                # Check if allocation already exists for this target and office
                existing_alloc = await session.execute(
                    select(TargetAllocation).where(
                        TargetAllocation.target_id == target_id,
                        TargetAllocation.office_id == office.id
                    )
                )
                if existing_alloc.scalar_one_or_none():
                    continue  # skip if already exists

                alloc_id = str(uuid.uuid4())
                allocation = TargetAllocation(
                    id=alloc_id,
                    target_id=target_id,
                    scheme_id=scheme.id,
                    office_id=office.id,
                    allocated_target=allocated,
                    financial_year=financial_year,
                    achievement_percentage=0.0,
                    achieved=0.0,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(allocation)
            print(f"   → Created {len(offices)} allocations for {scheme.scheme_code}")

        await session.commit()
        print("\n✅ Migration complete. Targets and allocations inserted.")

if __name__ == "__main__":
    asyncio.run(migrate())
