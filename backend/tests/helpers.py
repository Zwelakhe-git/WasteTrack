"""Константы и вспомогательные функции тестов."""
from datetime import timedelta

from app.utils.utils import wall_clock_now

PASSWORD = "Test_pass1"
TERMINAL_KEY = "test_terminal_key"
TERMINAL = {"x-terminal-key": TERMINAL_KEY}


async def login(client, username: str, password: str = PASSWORD):
    return await client.post("/api/auth/login", data={"username": username, "password": password})


def past_hour(days_ago: int = 1, hour: int = 12) -> str:
    """Время списания в формате терминала: '2026-11-23 12:00:00' (по часам ресторана)."""
    day = (wall_clock_now() - timedelta(days=days_ago)).date()
    return f"{day.isoformat()} {hour:02d}:00:00"


def waste_payload(seed, product="patty", reason="expired", quantity=1, created_at=None, **extra):
    return {
        "product_id": seed[product],
        "reason_id": seed[reason],
        "restaurant_id": seed["restaurant"],
        "quantity": quantity,
        "created_at": created_at or past_hour(),
        **extra,
    }
