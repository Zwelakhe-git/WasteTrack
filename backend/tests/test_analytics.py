"""Аналитика и экспорт (раздел 2.5.3, сценарий 14)."""
import csv
import io

from openpyxl import load_workbook

from tests.helpers import TERMINAL, past_hour, waste_payload

HEADER = ['Дата и время', 'Продукт', 'Причина', 'Количество', 'Ед. изм.',
          'Себестоимость ед., руб.', 'Сумма, руб.', 'Комментарий']


async def make_records(client, seed):
    when = past_hour(hour=11)
    await client.post("/api/waste/", json=waste_payload(seed, "patty", "expired", 2, when), headers=TERMINAL)   # 280 ₽
    await client.post("/api/waste/", json=waste_payload(seed, "bun", "dropped", 4, when), headers=TERMINAL)     # 60 ₽
    await client.post("/api/waste/", json=waste_payload(seed, "patty", "other", 1, when, comment="Упала упаковка"),
                      headers=TERMINAL)                                                                         # 140 ₽
    return when


async def test_summary_in_rubles(client, seed, manager_headers):
    """F_analytics_1, F_analytics_2, F_analytics_6: сумма, разбивка по причинам, топ продуктов."""
    await make_records(client, seed)
    r = await client.get("/api/analytics/summary", params={"days": 7}, headers=manager_headers)
    assert r.status_code == 200
    s = r.json()
    assert s["total_records"] == 3
    assert float(s["total_cost"]) == 480

    by_reason = {x["reason_name"]: float(x["total_cost"]) for x in s["top_reasons"]}
    assert by_reason == {"Истек срок хранения": 280, "Прочее": 140, "Упало на пол": 60}
    assert s["top_reasons"][0]["reason_name"] == "Истек срок хранения"   # по убыванию суммы

    top = s["top_products"]
    assert top[0]["product_name"] == "Котлета для Воппера"
    assert float(top[0]["total_cost"]) == 420
    assert float(top[0]["total_quantity"]) == 3
    assert top[0]["unit_name"] == "шт"


async def test_summary_period_excludes_old_records(client, seed, manager_headers):
    await client.post("/api/waste/", json=waste_payload(seed, created_at=past_hour(days_ago=20)), headers=TERMINAL)
    week = await client.get("/api/analytics/summary", params={"days": 7}, headers=manager_headers)
    month = await client.get("/api/analytics/summary", params={"days": 30}, headers=manager_headers)
    assert week.json()["total_records"] == 0
    assert month.json()["total_records"] == 1


async def test_export_csv_columns_match_header(client, seed, manager_headers):
    """Сценарий 14 (F_analytics_5): CSV для русского Excel, колонки совпадают с заголовками."""
    when = await make_records(client, seed)
    r = await client.get("/api/analytics/export", params={"days": 7, "format": "csv"}, headers=manager_headers)
    assert r.status_code == 200
    assert r.content.startswith(b"\xef\xbb\xbf")                      # BOM: Excel распознаёт UTF-8
    assert "wastetrack_report_7d.csv" in r.headers["content-disposition"]

    rows = list(csv.reader(io.StringIO(r.content.decode("utf-8-sig")), delimiter=";"))
    assert rows[0] == HEADER
    assert len(rows) == 4
    record = dict(zip(HEADER, [row for row in rows[1:] if row[2] == "Прочее"][0]))
    assert record["Дата и время"] == when[:16]
    assert record["Продукт"] == "Котлета для Воппера"
    assert record["Количество"] == "1,0"                                 # десятичная запятая
    assert record["Ед. изм."] == "шт"
    assert record["Себестоимость ед., руб."] == "140,0"
    assert record["Сумма, руб."] == "140,0"
    assert record["Комментарий"] == "Упала упаковка"


async def test_export_xlsx_columns_match_header(client, seed, manager_headers):
    await make_records(client, seed)
    r = await client.get("/api/analytics/export", params={"days": 7}, headers=manager_headers)
    assert r.status_code == 200
    ws = load_workbook(io.BytesIO(r.content)).active
    rows = list(ws.values)
    assert list(rows[0]) == HEADER
    bun = dict(zip(HEADER, [row for row in rows[1:] if row[1] == "Булочка гамбургер"][0]))
    assert bun["Причина"] == "Упало на пол"
    assert bun["Количество"] == 4
    assert bun["Сумма, руб."] == 60


async def test_export_empty_period(client, seed, manager_headers):
    r = await client.get("/api/analytics/export", params={"days": 7, "format": "csv"}, headers=manager_headers)
    assert r.status_code == 200
    rows = list(csv.reader(io.StringIO(r.content.decode("utf-8-sig")), delimiter=";"))
    assert rows == [HEADER]


async def test_export_unknown_format_rejected(client, seed, manager_headers):
    r = await client.get("/api/analytics/export", params={"format": "pdf"}, headers=manager_headers)
    assert r.status_code == 422
