# ABOUTME: Stage 3 contract of the URL shortener: asynchronous click counting via a Redis queue
# ABOUTME: and redirects served from the Redis cache while PostgreSQL is stopped.
import httpx
import pytest

from contract_tests.helpers import (
    compose,
    eventually,
    require,
    stopped_service,
    unique_suffix,
    wait_until_healthy,
)

CLICKS_DEADLINE = 5.0


def create(client: httpx.Client) -> tuple[str, str]:
    url = f"https://example.com/stage3/{unique_suffix()}"
    resp = client.post("/links", json={"url": url})
    require(resp.status_code == 201, f"POST /links: ожидали 201, получили {resp.status_code}.")
    return resp.json()["code"], url


def clicks(client: httpx.Client, code: str) -> int | None:
    resp = client.get(f"/links/{code}/stats")
    if resp.status_code != 200:
        return None
    value = resp.json().get("clicks")
    return value if isinstance(value, int) else None


def test_stats_of_new_link(client: httpx.Client) -> None:
    code, _ = create(client)
    resp = client.get(f"/links/{code}/stats")
    require(
        resp.status_code == 200,
        f"GET /links/{code}/stats: ожидали 200, получили {resp.status_code}: {resp.text[:200]}",
    )
    body = resp.json()
    require(
        body == {"code": code, "clicks": 0},
        f"GET /links/{code}/stats у новой ссылки: ждали {{'code': '{code}', 'clicks': 0}}, "
        f"получили {body}.",
    )


def test_stats_unknown_code(client: httpx.Client) -> None:
    resp = client.get(f"/links/zz{unique_suffix()[:8]}/stats")
    require(
        resp.status_code == 404, f"stats неизвестного кода: ждали 404, получили {resp.status_code}."
    )


def test_clicks_are_counted(client: httpx.Client) -> None:
    code, _ = create(client)
    transitions = 7
    for _ in range(transitions):
        resp = client.get(f"/{code}", follow_redirects=False)
        require(resp.status_code == 307, f"GET /{code}: ожидали 307, получили {resp.status_code}.")
    counted = eventually(lambda: clicks(client, code) == transitions, CLICKS_DEADLINE)
    require(
        counted,
        f"После {transitions} переходов по /{code} за {CLICKS_DEADLINE:.0f} с clicks = "
        f"{clicks(client, code)}, ждали {transitions}. Проверьте, что воркер запущен "
        "(docker compose ps), читает очередь и сохраняет счётчик в БД.",
    )


@pytest.mark.restarts_containers
def test_redirect_without_database(client: httpx.Client) -> None:
    code, url = create(client)
    first = client.get(f"/{code}", follow_redirects=False)
    require(first.status_code == 307, f"GET /{code}: ожидали 307, получили {first.status_code}.")
    # Перезапуск app стирает кэш внутри процесса: пройти тест можно только с Redis.
    compose("restart", "app")
    wait_until_healthy(client)
    with stopped_service(client, "db"):
        resp = client.get(f"/{code}", follow_redirects=False)
    require(
        resp.status_code == 307 and resp.headers.get("location") == url,
        f"При остановленном PostgreSQL (docker compose stop db) GET /{code} вернул "
        f"{resp.status_code} вместо 307. Переход по уже открытой ссылке должен "
        "обслуживаться из кэша в Redis.",
    )
