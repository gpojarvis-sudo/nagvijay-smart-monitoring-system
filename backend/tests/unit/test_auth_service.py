import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.auth_service import AuthService
from app.schemas.auth import RegisterRequest, LoginRequest
from app.constants.roles import UserRole
from app.core.exceptions import (
    ConflictException,
    UnauthorizedException,
    NotFoundException,
)


@pytest.fixture
def service():
    db = AsyncMock()
    svc = AuthService(db)
    svc.user_repo = AsyncMock()
    return svc


@pytest.fixture
def fake_user():
    user = MagicMock()
    user.id = "user-123"
    user.email = "john@example.com"
    user.full_name = "John Doe"
    user.employee_id = "EMP001"
    user.role = UserRole.EMPLOYEE
    user.is_active = True
    user.hashed_password = "hashed-password"
    return user


@pytest.mark.asyncio
async def test_register_success(service, fake_user):
    service.user_repo.get_by_email.return_value = None
    service.user_repo.create.return_value = fake_user

    req = RegisterRequest(
        email="john@example.com",
        full_name="John Doe",
        password="Password123",
    )

    with patch("app.services.auth_service.hash_password", return_value="hashed-password"), \
         patch("app.services.auth_service.create_tokens_pair", return_value={
             "access_token": "access",
             "refresh_token": "refresh",
             "token_type": "bearer",
         }):

        result = await service.register(req)

    assert result["user"] == fake_user
    assert result["tokens"]["access_token"] == "access"
    service.user_repo.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_register_duplicate_email(service):
    service.user_repo.get_by_email.return_value = MagicMock()

    req = RegisterRequest(
        email="john@example.com",
        full_name="John Doe",
        password="Password123",
    )

    with pytest.raises(ConflictException):
        await service.register(req)


@pytest.mark.asyncio
async def test_login_success(service, fake_user):
    service.user_repo.get_by_employee_id.return_value = fake_user

    req = LoginRequest(
        employee_id="EMP001",
        password="Password123",
    )

    with patch("app.services.auth_service.verify_password", return_value=True), \
         patch("app.services.auth_service.create_tokens_pair", return_value={
             "access_token": "access",
             "refresh_token": "refresh",
             "token_type": "bearer",
         }):

        result = await service.login(req)

    assert result["user"] == fake_user
    assert result["tokens"]["access_token"] == "access"


@pytest.mark.asyncio
async def test_login_invalid_employee(service):
    service.user_repo.get_by_employee_id.return_value = None

    req = LoginRequest(
        employee_id="EMP001",
        password="Password123",
    )

    with pytest.raises(UnauthorizedException):
        await service.login(req)


@pytest.mark.asyncio
async def test_login_wrong_password(service, fake_user):
    service.user_repo.get_by_employee_id.return_value = fake_user

    req = LoginRequest(
        employee_id="EMP001",
        password="wrong-password",
    )

    with patch("app.services.auth_service.verify_password", return_value=False):
        with pytest.raises(UnauthorizedException):
            await service.login(req)


@pytest.mark.asyncio
async def test_login_inactive_user(service, fake_user):
    fake_user.is_active = False
    service.user_repo.get_by_employee_id.return_value = fake_user

    req = LoginRequest(
        employee_id="EMP001",
        password="Password123",
    )

    with patch("app.services.auth_service.verify_password", return_value=True):
        with pytest.raises(UnauthorizedException):
            await service.login(req)


@pytest.mark.asyncio
async def test_get_user_by_id(service, fake_user):
    service.user_repo.get_by_id.return_value = fake_user

    user = await service.get_user_by_id("user-123")

    assert user == fake_user


@pytest.mark.asyncio
async def test_get_current_user_success(service, fake_user):
    service.user_repo.get_by_id.return_value = fake_user

    result = await service.get_current_user({"sub": "user-123"})

    assert result == fake_user


@pytest.mark.asyncio
async def test_get_current_user_not_found(service):
    service.user_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundException):
        await service.get_current_user({"sub": "user-123"})


@pytest.mark.asyncio
async def test_get_current_user_inactive(service, fake_user):
    fake_user.is_active = False
    service.user_repo.get_by_id.return_value = fake_user

    with pytest.raises(UnauthorizedException):
        await service.get_current_user({"sub": "user-123"})
