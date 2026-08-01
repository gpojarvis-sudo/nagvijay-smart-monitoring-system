import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from app.services.daily_office_report_service import DailyOfficeReportService


@pytest.fixture
def db():
    db = MagicMock()
    db.execute = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.add = MagicMock()
    return db


@pytest.fixture
def service(db):
    return DailyOfficeReportService(db)


@pytest.mark.asyncio
async def test_upsert_missing_report_date(service, db):
    office = SimpleNamespace(
        id="office-1",
        office_code="GPO001",
        office_name="Nagpur GPO",
    )

    office_result = MagicMock()
    office_result.scalar_one_or_none.return_value = office

    db.execute.return_value = office_result

    payload = {
        "office_code": "GPO001",
    }

    with pytest.raises(ValueError, match="report_date is required"):
        await service.upsert(payload)


@pytest.mark.asyncio
async def test_upsert_invalid_office(service, db):
    office_result = MagicMock()
    office_result.scalar_one_or_none.return_value = None

    db.execute.return_value = office_result

    payload = {
        "office_code": "INVALID001",
        "report_date": "2026-07-31",
    }

    with pytest.raises(ValueError, match="Office not found"):
        await service.upsert(payload)


def make_office():
    return SimpleNamespace(
        id="office-1",
        office_code="GPO001",
        office_name="Nagpur GPO",
    )


def make_result(value):
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    return result



@pytest.mark.asyncio
async def test_upsert_creates_new_report(service, db):
    office = make_office()

    office_result = make_result(office)
    report_result = make_result(None)

    db.execute.side_effect = [
        office_result,
        report_result,
    ]

    payload = {
        "office_code": "GPO001",
        "report_date": "2026-07-31",
        "sb_opened": 5,
    }

    report = await service.upsert(payload)

    assert report.office_id == office.id
    assert report.office_code == office.office_code
    assert report.office_name == office.office_name
    assert report.sb_opened == 5

    db.add.assert_called_once()
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once()
