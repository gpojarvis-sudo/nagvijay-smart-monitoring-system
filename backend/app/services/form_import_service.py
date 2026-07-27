from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException
from app.integrations.google_forms import GoogleFormsIntegration
from app.models.office import Office
from app.models.target import Scheme, Target, TargetAllocation
from app.schemas.target import AchievementCreate
from app.services.target_service import TargetService
from app.utils.helpers import get_financial_year


class FormImportService:
    @staticmethod
    async def process(parsed: dict, db: AsyncSession):
        if not parsed.get("office_code") or not parsed.get("scheme_code"):
            raise BadRequestException(
                "Missing office_code or scheme_code in form response"
            )

        office_result = await db.execute(
            select(Office).where(
                Office.office_code == parsed["office_code"]
            )
        )
        office = office_result.scalars().first()

        if not office:
            raise BadRequestException(
                f"Office code {parsed['office_code']} not found"
            )

        scheme_result = await db.execute(
            select(Scheme).where(
                Scheme.scheme_code == parsed["scheme_code"]
            )
        )
        scheme = scheme_result.scalars().first()

        if not scheme:
            raise BadRequestException(
                f"Scheme code {parsed['scheme_code']} not found"
            )

        current_fy = get_financial_year()

        allocation_result = await db.execute(
            select(TargetAllocation)
            .where(
                TargetAllocation.office_id == office.id,
                TargetAllocation.scheme_id == scheme.id,
                TargetAllocation.financial_year == current_fy,
            )
            .limit(1)
        )

        allocation = allocation_result.scalars().first()

        if not allocation:
            raise BadRequestException(
                f"No allocation found for office {office.office_code} "
                f"and scheme {scheme.scheme_code} in FY {current_fy}"
            )

        target_result = await db.execute(
            select(Target).where(
                Target.id == allocation.target_id
            )
        )

        target = target_result.scalars().first()

        achievement_data = GoogleFormsIntegration.map_to_achievement(
            parsed=parsed,
            office_id=office.id,
            scheme_id=scheme.id,
            allocation_id=allocation.id,
            target_id=target.id if target else allocation.target_id,
        )

        achievement = AchievementCreate(**achievement_data)

        service = TargetService(db)

        return await service.record_achievement(achievement)
