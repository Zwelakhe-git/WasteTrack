"""Запись списаний с терминала (раздел 2.5.1, сценарии 5–9)."""
import pytest

from tests.helpers import TERMINAL, past_hour, waste_payload


async def grid(client, seed, created_at):
    r = await client.get(
        "/api/waste/grid",
        params={"restaurant_id": seed["restaurant"], "date": created_at[:10]},
        headers=TERMINAL,
    )
    assert r.status_code == 200
    return r.json()


async def test_create_waste_record(client, seed):
    """F_waste_1–F_waste_5: запись создаётся, себестоимость фиксируется, час — по часам ресторана."""
    when = past_hour(hour=10)
    r = await client.post("/api/waste/", json=waste_payload(seed, quantity=2, created_at=when), headers=TERMINAL)
    assert r.status_code == 201, r.text
    rec = r.json()
    assert float(rec["quantity"]) == 2
    assert float(rec["unit_cost"]) == 140          # цена продукта на момент списания
    assert rec["created_by_id"] is None              # сотрудник кухни анонимен

    cells = await grid(client, seed, when)
    assert len(cells) == 1
    assert cells[0]["hour"] == 10                    # не сдвинуто часовым поясом
    assert cells[0]["product_id"] == seed["patty"]


@pytest.mark.parametrize("quantity", [0, -1, -0.5])
async def test_quantity_must_be_positive(client, seed, quantity):
    """Сценарий 5 (F_waste_3, NF_data_6): количество 0 или отрицательное — 422."""
    r = await client.post("/api/waste/", json=waste_payload(seed, quantity=quantity), headers=TERMINAL)
    assert r.status_code == 422


async def test_quantity_more_than_two_decimals_rejected(client, seed):
    """NF_data_6: не более двух знаков после запятой."""
    r = await client.post("/api/waste/", json=waste_payload(seed, quantity=0.125), headers=TERMINAL)
    assert r.status_code == 422


async def test_fractional_quantity_accepted(client, seed):
    r = await client.post("/api/waste/", json=waste_payload(seed, product="cheese", quantity=0.25), headers=TERMINAL)
    assert r.status_code == 201
    assert float(r.json()["quantity"]) == 0.25


async def test_repeat_same_reason_same_hour_updates(client, seed):
    """Сценарий 6: повторное списание по той же причине в том же часе обновляет количество."""
    when = past_hour()
    first = await client.post("/api/waste/", json=waste_payload(seed, quantity=1, created_at=when), headers=TERMINAL)
    second = await client.post("/api/waste/", json=waste_payload(seed, quantity=3, created_at=when), headers=TERMINAL)
    assert first.status_code == second.status_code == 201
    assert first.json()["id"] == second.json()["id"]

    cells = await grid(client, seed, when)
    assert len(cells) == 1
    assert cells[0]["quantity"] == 3


async def test_different_reasons_same_hour_are_separate(client, seed):
    when = past_hour()
    await client.post("/api/waste/", json=waste_payload(seed, reason="expired", quantity=1, created_at=when), headers=TERMINAL)
    await client.post("/api/waste/", json=waste_payload(seed, reason="dropped", quantity=2, created_at=when), headers=TERMINAL)
    cells = await grid(client, seed, when)
    assert sorted(c["quantity"] for c in cells) == [1, 2]


async def test_other_reason_requires_comment(client, seed):
    """Сценарий 7 (F_waste_6): «Прочее» без комментария — 422 с пояснением."""
    r = await client.post("/api/waste/", json=waste_payload(seed, reason="other"), headers=TERMINAL)
    assert r.status_code == 422
    assert "комментарий" in r.json()["detail"]


async def test_other_reason_whitespace_comment_rejected(client, seed):
    r = await client.post("/api/waste/", json=waste_payload(seed, reason="other", comment="   "), headers=TERMINAL)
    assert r.status_code == 422


async def test_other_reason_with_comment_accepted(client, seed):
    r = await client.post(
        "/api/waste/", json=waste_payload(seed, reason="other", comment="  Гость отказался  "), headers=TERMINAL)
    assert r.status_code == 201
    assert r.json()["comment"] == "Гость отказался"   # пробелы по краям обрезаны


async def test_comment_too_long_rejected(client, seed):
    """NF_data_9: комментарий не длиннее 500 символов."""
    r = await client.post("/api/waste/", json=waste_payload(seed, comment="а" * 501), headers=TERMINAL)
    assert r.status_code == 422


async def test_zero_cancels_only_selected_reason(client, seed):
    """Сценарий 8: отмена по одной причине не затрагивает другие причины в ячейке."""
    when = past_hour()
    a = await client.post("/api/waste/", json=waste_payload(seed, reason="expired", created_at=when), headers=TERMINAL)
    await client.post("/api/waste/", json=waste_payload(seed, reason="dropped", created_at=when), headers=TERMINAL)

    r = await client.delete(f"/api/waste/{a.json()['id']}", headers=TERMINAL)
    assert r.status_code == 200

    cells = await grid(client, seed, when)
    assert [c["reason_id"] for c in cells] == [seed["dropped"]]


async def test_delete_requires_terminal_key(client, seed):
    a = await client.post("/api/waste/", json=waste_payload(seed), headers=TERMINAL)
    r = await client.delete(f"/api/waste/{a.json()['id']}", headers={"x-terminal-key": "wrong"})
    assert r.status_code == 401


async def test_future_hour_rejected(client, seed):
    """Сценарий 9: списание в час, который ещё не наступил, — 422."""
    tomorrow = past_hour(days_ago=-1, hour=12)
    r = await client.post("/api/waste/", json=waste_payload(seed, created_at=tomorrow), headers=TERMINAL)
    assert r.status_code == 422


async def test_frozen_product_rejected(client, seed, manager_headers):
    """F_product_3: замороженный продукт нельзя списать."""
    await client.patch(f"/api/products/{seed['patty']}", json={"status": "frozen"}, headers=manager_headers)
    r = await client.post("/api/waste/", json=waste_payload(seed), headers=TERMINAL)
    assert r.status_code == 400


async def test_patch_updates_quantity_and_comment(client, seed):
    a = await client.post("/api/waste/", json=waste_payload(seed, quantity=1), headers=TERMINAL)
    r = await client.patch(f"/api/waste/{a.json()['id']}", json={"quantity": 4, "comment": "уточнено"}, headers=TERMINAL)
    assert r.status_code == 200
    assert float(r.json()["quantity"]) == 4
    assert r.json()["comment"] == "уточнено"
