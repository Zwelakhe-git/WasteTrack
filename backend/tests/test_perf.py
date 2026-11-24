"""Производительность (сценарий 15, NF_perf_3, NF_data_21).

Медленный тест: можно пропустить флагом  -m "not perf".
"""
import random
import time
from datetime import timedelta
from decimal import Decimal

import pytest
from sqlalchemy import insert

from app.models.waste_record import WasteRecord
from app.utils.utils import wall_clock_now

N_RECORDS = 10_000


@pytest.mark.perf
async def test_summary_and_export_on_10k_records(client, db, seed, manager_headers):
    rnd = random.Random(42)
    now = wall_clock_now()
    rows = [
        {
            "product_id": rnd.choice([seed["patty"], seed["bun"], seed["cheese"]]),
            "reason_id": rnd.choice([seed["expired"], seed["dropped"]]),
            "restaurant_id": seed["restaurant"],
            "quantity": Decimal(rnd.randint(1, 20)),
            "unit_cost": Decimal("100.00"),
            "created_at": now - timedelta(minutes=rnd.randint(60, 29 * 24 * 60)),
        }
        for _ in range(N_RECORDS)
    ]
    await db.execute(insert(WasteRecord), rows)
    await db.commit()

    t0 = time.perf_counter()
    r = await client.get("/api/analytics/summary", params={"days": 30}, headers=manager_headers)
    summary_time = time.perf_counter() - t0
    assert r.status_code == 200
    assert r.json()["total_records"] == N_RECORDS

    t0 = time.perf_counter()
    e = await client.get("/api/analytics/export", params={"days": 30, "format": "csv"}, headers=manager_headers)
    export_time = time.perf_counter() - t0
    assert e.status_code == 200

    print(f"\nСводка за месяц, {N_RECORDS} записей: {summary_time:.3f} с")
    print(f"Экспорт CSV, {N_RECORDS} записей: {export_time:.3f} с")
    assert summary_time < 2.0      # NF_perf_3
    assert export_time < 10.0      # NF_data_21
