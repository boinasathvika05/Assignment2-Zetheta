import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_register_customer_success():
    """Verify user registration succeeds for Customer role."""
    unique_email = f"priya.reg.{uuid.uuid4().hex[:6]}@nexbank.in"
    unique_phone = f"+919876{uuid.uuid4().int % 1000000:06d}"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "email": unique_email,
            "password": "Password123!",
            "full_name": "Priya Sharma",
            "role": "CUSTOMER",
            "phone_number": unique_phone
        }
        response = await ac.post("/api/v1/auth/register", json=payload)
        assert response.status_code in (200, 201)
        res_json = response.json()
        assert res_json["success"] is True
        assert res_json["data"]["email"] == unique_email
        assert res_json["data"]["role"] == "CUSTOMER"


@pytest.mark.asyncio
async def test_register_duplicate_email():
    """Verify duplicate registration fails with 400 Bad Request."""
    unique_email = f"dup.test.{uuid.uuid4().hex[:6]}@nexbank.in"
    unique_phone = f"+919876{uuid.uuid4().int % 1000000:06d}"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "email": unique_email,
            "password": "Password123!",
            "full_name": "Duplicate Test User",
            "role": "CUSTOMER",
            "phone_number": unique_phone
        }
        # First registration
        reg1 = await ac.post("/api/v1/auth/register", json=payload)
        assert reg1.status_code in (200, 201)

        # Duplicate registration
        reg2 = await ac.post("/api/v1/auth/register", json=payload)
        assert reg2.status_code == 400
        assert "already exists" in reg2.json()["detail"]


@pytest.mark.asyncio
async def test_login_success():
    """Verify login returns access token and refresh token upon valid credentials."""
    unique_email = f"login.success.{uuid.uuid4().hex[:6]}@nexbank.in"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        reg_payload = {
            "email": unique_email,
            "password": "Password123!",
            "full_name": "Login Success User",
            "role": "CUSTOMER"
        }
        await ac.post("/api/v1/auth/register", json=reg_payload)

        login_payload = {
            "email": unique_email,
            "password": "Password123!"
        }
        response = await ac.post("/api/v1/auth/login", json=login_payload)
        assert response.status_code == 200
        res_json = response.json()
        assert res_json["success"] is True
        token_data = res_json["data"]
        assert "access_token" in token_data
        assert "refresh_token" in token_data
        assert token_data["user"]["email"] == unique_email


@pytest.mark.asyncio
async def test_login_invalid_password():
    """Verify login fails with 401 UNAUTHORIZED on wrong password."""
    unique_email = f"wrong.pass.{uuid.uuid4().hex[:6]}@nexbank.in"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        reg_payload = {
            "email": unique_email,
            "password": "Password123!",
            "full_name": "Wrong Pass User",
            "role": "CUSTOMER"
        }
        await ac.post("/api/v1/auth/register", json=reg_payload)

        login_payload = {
            "email": unique_email,
            "password": "WrongPassword999!"
        }
        response = await ac.post("/api/v1/auth/login", json=login_payload)
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_account_lockout_after_5_failures():
    """Verify account locks with 423 LOCKED status after 5 consecutive failed login attempts."""
    unique_email = f"lockout.test.{uuid.uuid4().hex[:6]}@nexbank.in"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        reg_payload = {
            "email": unique_email,
            "password": "Password123!",
            "full_name": "Lockout Test User",
            "role": "CUSTOMER"
        }
        await ac.post("/api/v1/auth/register", json=reg_payload)

        login_payload = {
            "email": unique_email,
            "password": "WrongPassword!"
        }

        for _ in range(4):
            resp = await ac.post("/api/v1/auth/login", json=login_payload)
            assert resp.status_code == 401

        resp5 = await ac.post("/api/v1/auth/login", json=login_payload)
        assert resp5.status_code == 423
        assert "locked" in resp5.json()["detail"].lower()


@pytest.mark.asyncio
async def test_token_refresh_and_logout():
    """Verify token rotation on refresh and session revocation on logout."""
    unique_email = f"token.test.{uuid.uuid4().hex[:6]}@nexbank.in"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        reg_payload = {
            "email": unique_email,
            "password": "Password123!",
            "full_name": "Token Test",
            "role": "SUPERVISOR"
        }
        await ac.post("/api/v1/auth/register", json=reg_payload)

        login_resp = await ac.post("/api/v1/auth/login", json={"email": unique_email, "password": "Password123!"})
        refresh_token = login_resp.json()["data"]["refresh_token"]
        access_token = login_resp.json()["data"]["access_token"]

        me_resp = await ac.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"})
        assert me_resp.status_code == 200
        assert me_resp.json()["data"]["email"] == unique_email

        refresh_resp = await ac.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert refresh_resp.status_code == 200
        new_refresh_token = refresh_resp.json()["data"]["refresh_token"]
        assert new_refresh_token != refresh_token

        logout_resp = await ac.post("/api/v1/auth/logout", json={"refresh_token": new_refresh_token})
        assert logout_resp.status_code == 200
        assert logout_resp.json()["data"]["revoked"] is True
