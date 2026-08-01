import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.office_service import OfficeService
from app.core.exceptions import (
    ConflictException,
    NotFoundException,
)
from app.schemas.office import OfficeCreate


@pytest.fixture
def db():
    return AsyncMock()


@pytest.fixture
def service(db):
    svc = OfficeService(db)
    svc.repo = AsyncMock()
    return svc


@pytest.mark.asyncio
async def test_create_office_success(service):
    payload = OfficeCreate(
        office_code="GPO001",
        office_name="Nagpur GPO",
        office_type="HEAD_OFFICE",
        pincode="440001",
        district="Nagpur",
    )

    office = SimpleNamespace(
        id="1",
        office_code="GPO001",
    )

    service.repo.get_by_code.return_value = None
    service.repo.create.return_value = office

    result = await service.create_office(
        payload,
        created_by="admin",
    )

    assert result == office
    service.repo.get_by_code.assert_awaited_once_with("GPO001")
    service.repo.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_office_duplicate(service):
    payload = OfficeCreate(
        office_code="GPO001",
        office_name="Nagpur GPO",
        office_type="HEAD_OFFICE",
        pincode="440001",
        district="Nagpur",
    )

    service.repo.get_by_code.return_value = object()

    with pytest.raises(ConflictException):
        await service.create_office(payload)
