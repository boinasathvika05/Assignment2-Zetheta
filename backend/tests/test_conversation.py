import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import init_db


@pytest.mark.asyncio
async def test_conversation_lifecycle():
    await init_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Register & Login User
        reg_payload = {
            "email": "chat.test@nexbank.in",
            "password": "Password123!",
            "full_name": "Chat Test User",
            "role": "CUSTOMER"
        }
        await ac.post("/api/v1/auth/register", json=reg_payload)
        login_resp = await ac.post("/api/v1/auth/login", json={"email": "chat.test@nexbank.in", "password": "Password123!"})
        access_token = login_resp.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        # 2. Start Conversation
        start_resp = await ac.post("/api/v1/chat/start", json={"channel": "web"}, headers=headers)
        assert start_resp.status_code == 201
        conv_id = start_resp.json()["data"]["conversation_id"]

        # 3. Process Customer Turn
        msg_resp = await ac.post("/api/v1/chat/message", json={"conversation_id": conv_id, "message": "Hi, check my savings account balance"}, headers=headers)
        assert msg_resp.status_code == 200
        res_data = msg_resp.json()["data"]
        assert res_data["intent_id"] == "ACC-001"
        assert "account" in res_data["bot_response"].lower() or "balance" in res_data["bot_response"].lower()

        # 4. Get Conversation History
        hist_resp = await ac.get(f"/api/v1/chat/history/{conv_id}", headers=headers)
        assert hist_resp.status_code == 200
        messages = hist_resp.json()["data"]
        assert len(messages) >= 2
