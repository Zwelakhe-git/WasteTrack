"""Аутентификация и разграничение доступа (раздел 2.6, сценарии 1–4)."""
from jose import jwt

from app.config import settings
from tests.helpers import PASSWORD, TERMINAL, login, waste_payload


async def test_login_success_returns_jwt(client, seed):
    """Сценарий 1 (F_login_1): верные логин и пароль — выдан JWT, /auth/me его принимает."""
    r = await login(client, "manager_t")
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer"

    payload = jwt.decode(body["access_token"], settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    assert "exp" in payload and payload["sub"]

    me = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert me.status_code == 200
    assert me.json()["login"] == "manager_t"
    assert me.json()["role"] == "manager"
    assert "password_hash" not in me.json()


async def test_login_wrong_password(client, seed):
    """Сценарий 2: неверный пароль — 400, токен не выдан."""
    r = await login(client, "manager_t", "wrong_password")
    assert r.status_code == 400
    assert "access_token" not in r.json()


async def test_login_unknown_user(client, seed):
    r = await login(client, "nobody", PASSWORD)
    assert r.status_code == 400


async def test_password_stored_as_bcrypt_hash(db, seed):
    """Пароль хранится только в виде хеша bcrypt."""
    from sqlalchemy import select
    from app.models.user import User
    user = (await db.execute(select(User).where(User.login == "manager_t"))).scalars().one()
    assert user.password_hash != PASSWORD
    assert user.password_hash.startswith("$2")


async def test_analytics_requires_token(client, seed):
    """Сценарий 3: аналитика без токена — 401."""
    r = await client.get("/api/analytics/summary")
    assert r.status_code == 401


async def test_invalid_token_rejected(client, seed):
    r = await client.get("/api/auth/me", headers={"Authorization": "Bearer not.a.token"})
    assert r.status_code == 401


async def test_token_signed_with_other_key_rejected(client, seed):
    forged = jwt.encode({"sub": "1"}, "other_secret", algorithm="HS256")
    r = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {forged}"})
    assert r.status_code == 401


async def test_waste_wrong_terminal_key(client, seed):
    """Сценарий 4: неверный ключ терминала — 401, запись не создана."""
    r = await client.post("/api/waste/", json=waste_payload(seed), headers={"x-terminal-key": "wrong"})
    assert r.status_code == 401
    grid = await client.get(
        "/api/waste/grid",
        params={"restaurant_id": seed["restaurant"], "date": waste_payload(seed)["created_at"][:10]},
        headers=TERMINAL,
    )
    assert grid.json() == []


async def test_waste_missing_terminal_key(client, seed):
    r = await client.post("/api/waste/", json=waste_payload(seed))
    assert r.status_code == 422


async def test_terminal_key_does_not_open_manager_api(client, seed):
    """Ключ терминала не даёт доступа к функциям менеджера."""
    r = await client.get("/api/analytics/summary", headers=TERMINAL)
    assert r.status_code == 401


async def test_manager_cannot_create_restaurant(client, manager_headers):
    """Разграничение ролей: добавлять рестораны может только администратор."""
    r = await client.post("/api/restaurants/", json={"name": "Новый", "number": "T-002"}, headers=manager_headers)
    assert r.status_code == 403


async def test_admin_can_create_restaurant(client, admin_headers):
    r = await client.post("/api/restaurants/", json={"name": "Новый", "number": "T-002"}, headers=admin_headers)
    assert r.status_code == 201
    assert r.json()["number"] == "T-002"
