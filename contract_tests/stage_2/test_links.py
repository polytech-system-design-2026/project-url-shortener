# ABOUTME: Stage 2 contract of the URL shortener: create links, redirect, link info, persistence.
# ABOUTME: Black-box HTTP tests; every test creates its own links.
import re
from datetime import datetime

import httpx
import pytest

from contract_tests.helpers import compose, require, unique_suffix, wait_until_healthy

CODE_RE = re.compile(r"^[A-Za-z0-9]{4,10}$")


def long_url() -> str:
    return f"https://example.com/articles/{unique_suffix()}?utm_source=test&page=2"


def create(client: httpx.Client, url: str) -> dict[str, str]:
    resp = client.post("/links", json={"url": url})
    require(
        resp.status_code == 201,
        f"POST /links {{'url': '{url}'}}: ожидали 201, получили {resp.status_code}: "
        f"{resp.text[:300]}",
    )
    body: dict[str, str] = resp.json()
    return body


def unknown_code() -> str:
    return "zz" + unique_suffix()[:8]


def test_create_link(client: httpx.Client) -> None:
    url = long_url()
    body = create(client, url)
    code = body.get("code", "")
    require(
        CODE_RE.match(str(code)),
        f"POST /links: code должен быть 4–10 символов [A-Za-z0-9], получили {code!r}.",
    )
    require(
        body.get("url") == url, f"POST /links: url в ответе {body.get('url')!r}, ждали {url!r}."
    )
    short_url = str(body.get("short_url", ""))
    require(
        short_url.startswith("http") and short_url.endswith(f"/{code}"),
        f"POST /links: short_url должен быть полной ссылкой, оканчивающейся на /{code}, "
        f"получили {short_url!r}.",
    )


@pytest.mark.parametrize("url", ["http://example.com/plain", "https://example.com"])
def test_create_accepts_http_and_https(client: httpx.Client, url: str) -> None:
    create(client, url)


@pytest.mark.parametrize(
    "url",
    [
        "ftp://example.com/file.txt",
        "javascript:alert(1)",
        "example.com/no-scheme",
        "not a url",
        "http://",
        "",
    ],
)
def test_create_rejects_invalid_url(client: httpx.Client, url: str) -> None:
    resp = client.post("/links", json={"url": url})
    require(
        resp.status_code == 422,
        f"POST /links {{'url': {url!r}}}: ожидали 422 (допустимы только http:// и https:// "
        f"с хостом), получили {resp.status_code}.",
    )


@pytest.mark.parametrize("payload", [None, {}, {"link": "https://example.com"}])
def test_create_rejects_bad_body(client: httpx.Client, payload: dict[str, str] | None) -> None:
    resp = client.post("/links", json=payload)
    require(
        resp.status_code == 422,
        f"POST /links с телом {payload!r}: ожидали 422, получили {resp.status_code}.",
    )


def test_redirect(client: httpx.Client) -> None:
    url = long_url()
    code = create(client, url)["code"]
    resp = client.get(f"/{code}", follow_redirects=False)
    require(
        resp.status_code == 307,
        f"GET /{code}: ожидали редирект 307, получили {resp.status_code}.",
    )
    require(
        resp.headers.get("location") == url,
        f"GET /{code}: заголовок Location = {resp.headers.get('location')!r}, ждали {url!r}.",
    )


def test_redirect_unknown_code(client: httpx.Client) -> None:
    code = unknown_code()
    resp = client.get(f"/{code}", follow_redirects=False)
    require(
        resp.status_code == 404,
        f"GET /{code} (нет такого кода): ждали 404, получили {resp.status_code}.",
    )
    require("detail" in resp.json(), f'GET /{code}: тело ошибки должно быть {{"detail": ...}}.')


def test_link_info(client: httpx.Client) -> None:
    url = long_url()
    code = create(client, url)["code"]
    resp = client.get(f"/links/{code}")
    require(
        resp.status_code == 200, f"GET /links/{code}: ожидали 200, получили {resp.status_code}."
    )
    body = resp.json()
    require(
        body.get("code") == code and body.get("url") == url,
        f"GET /links/{code}: ждали code={code!r} и url={url!r}, получили {body}.",
    )
    created_at = str(body.get("created_at", ""))
    try:
        datetime.fromisoformat(created_at)
        parsed = True
    except ValueError:
        parsed = False
    require(
        parsed,
        f"GET /links/{code}: created_at должен быть датой ISO 8601, получили {created_at!r}.",
    )


def test_link_info_unknown_code(client: httpx.Client) -> None:
    resp = client.get(f"/links/{unknown_code()}")
    require(
        resp.status_code == 404,
        f"GET /links/<нет такого кода>: ждали 404, получили {resp.status_code}.",
    )


def test_many_links_have_unique_codes(client: httpx.Client) -> None:
    codes = [create(client, long_url())["code"] for _ in range(50)]
    require(
        len(set(codes)) == len(codes),
        f"50 разных ссылок получили только {len(set(codes))} разных кодов — коды повторяются.",
    )


@pytest.mark.restarts_containers
def test_links_survive_app_restart(client: httpx.Client) -> None:
    url = long_url()
    code = create(client, url)["code"]
    compose("restart", "app")
    wait_until_healthy(client)
    resp = client.get(f"/{code}", follow_redirects=False)
    require(
        resp.status_code == 307 and resp.headers.get("location") == url,
        f"После docker compose restart app GET /{code} вернул {resp.status_code}, ждали 307 "
        "с исходным URL в Location. Если 404 — ссылки хранятся в памяти процесса, а должны "
        "в PostgreSQL.",
    )
