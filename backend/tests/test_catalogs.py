"""Справочники продуктов и причин (раздел 2.5.2, сценарии 11–13)."""
from tests.helpers import TERMINAL, past_hour, waste_payload


async def test_create_product_requires_manager(client, seed):
    r = await client.post("/api/products/", json={"name": "Соус", "category": "соусы", "unit_id": 1})
    assert r.status_code == 401


async def test_create_product_with_cost(client, seed, manager_headers):
    """F_product_1, F_product_5: продукт с единицей измерения и себестоимостью."""
    r = await client.post(
        "/api/products/", json={"name": "Соус", "category": "соусы", "unit_id": 1, "cost": 12.5},
        headers=manager_headers)
    assert r.status_code == 201
    assert r.json()["unit"]["name"] == "шт"
    assert float(r.json()["cost"]) == 12.5


async def test_negative_cost_rejected(client, seed, manager_headers):
    r = await client.patch(f"/api/products/{seed['patty']}", json={"cost": -1}, headers=manager_headers)
    assert r.status_code == 422


async def test_frozen_product_hidden_from_terminal(client, seed, manager_headers):
    """Сценарий 11 (F_product_3, NF_data_14): замороженный продукт скрыт в терминале, но остаётся в отчётах."""
    await client.post("/api/waste/", json=waste_payload(seed, quantity=2), headers=TERMINAL)
    r = await client.patch(f"/api/products/{seed['patty']}", json={"status": "frozen"}, headers=manager_headers)
    assert r.status_code == 200

    active = await client.get("/api/products/", params={"status": "active"})
    assert seed["patty"] not in [p["id"] for p in active.json()]

    summary = await client.get("/api/analytics/summary", params={"days": 7}, headers=manager_headers)
    assert "Котлета для Воппера" in [p["product_name"] for p in summary.json()["top_products"]]


async def test_delete_product_with_records_refused(client, seed, manager_headers):
    """Сценарий 12 (F_product_4, NF_sec_5): продукт со списаниями удалить нельзя."""
    await client.post("/api/waste/", json=waste_payload(seed), headers=TERMINAL)
    r = await client.delete(f"/api/products/{seed['patty']}", headers=manager_headers)
    assert r.status_code >= 400
    still = await client.get("/api/products/")
    assert seed["patty"] in [p["id"] for p in still.json()]


async def test_delete_product_without_records(client, seed, manager_headers):
    r = await client.delete(f"/api/products/{seed['bun']}", headers=manager_headers)
    assert r.status_code == 200
    left = await client.get("/api/products/")
    assert seed["bun"] not in [p["id"] for p in left.json()]


async def test_cost_change_keeps_history(client, seed, manager_headers):
    """Сценарий 13 (NF_data_13): изменение цены не меняет суммы прошлых списаний."""
    await client.post("/api/waste/", json=waste_payload(seed, quantity=2), headers=TERMINAL)   # 2 × 140
    await client.patch(f"/api/products/{seed['patty']}", json={"cost": 200}, headers=manager_headers)

    summary = await client.get("/api/analytics/summary", params={"days": 7}, headers=manager_headers)
    assert float(summary.json()["total_cost"]) == 280


async def test_first_cost_fills_records_without_price(client, seed, manager_headers):
    """Списания продукта без цены получают её, когда цена впервые задана."""
    await client.post("/api/waste/", json=waste_payload(seed, product="cheese", quantity=0.5), headers=TERMINAL)
    before = await client.get("/api/analytics/summary", params={"days": 7}, headers=manager_headers)
    assert float(before.json()["total_cost"]) == 0

    await client.patch(f"/api/products/{seed['cheese']}", json={"cost": 900}, headers=manager_headers)
    after = await client.get("/api/analytics/summary", params={"days": 7}, headers=manager_headers)
    assert float(after.json()["total_cost"]) == 450


async def test_reasons_list_and_create(client, seed, manager_headers):
    """F_reason_1: новая причина, в том числе с обязательным комментарием."""
    r = await client.post("/api/reasons/", json={"name": "Возврат", "requires_comment": True}, headers=manager_headers)
    assert r.status_code == 201
    assert r.json()["requires_comment"] is True
    names = [x["name"] for x in (await client.get("/api/reasons/")).json()]
    assert "Возврат" in names


async def test_duplicate_reason_rejected(client, seed, manager_headers):
    r = await client.post("/api/reasons/", json={"name": "Прочее"}, headers=manager_headers)
    assert r.status_code == 400


async def test_frozen_reason_hidden(client, seed, manager_headers):
    """F_reason_3, NF_data_18: замороженная причина не показывается в форме списания."""
    r = await client.patch(f"/api/reasons/{seed['dropped']}", json={"status": "frozen"}, headers=manager_headers)
    assert r.status_code == 200
    names = [x["name"] for x in (await client.get("/api/reasons/")).json()]
    assert "Упало на пол" not in names


async def test_delete_reason_with_records_refused(client, seed, manager_headers):
    """F_reason_4, NF_sec_6: причину со списаниями удалить нельзя."""
    await client.post("/api/waste/", json=waste_payload(seed, reason="dropped"), headers=TERMINAL)
    r = await client.delete(f"/api/reasons/{seed['dropped']}", headers=manager_headers)
    assert r.status_code >= 400
