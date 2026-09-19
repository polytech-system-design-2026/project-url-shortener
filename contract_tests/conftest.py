# ABOUTME: Shared fixtures for teacher's contract tests: HTTP client and service readiness wait.
# ABOUTME: Do not edit — CI replaces contract_tests/ with the template copy at tag reference-v1.
"""Контрактные тесты преподавателя. Не редактировать.

CI перед прогоном заменяет всю папку contract_tests/ копией из шаблона
по тегу reference-v1 (см. .github/workflows/ci.yml), правки здесь на
результат не влияют.
"""

import os
import time
from collections.abc import Iterator

import httpx
import pytest

BASE_URL = os.environ.get("APP_URL", "http://localhost:8000")


def wait_until_healthy(client: httpx.Client, timeout: float = 120.0) -> None:
    """Ждёт 200 от GET /health, иначе падает с подсказкой, куда смотреть."""
    deadline = time.monotonic() + timeout
    last = "нет ответа"
    while time.monotonic() < deadline:
        try:
            resp = client.get("/health")
            if resp.status_code == 200:
                return
            last = f"HTTP {resp.status_code}: {resp.text[:200]}"
        except httpx.HTTPError as exc:
            last = f"{type(exc).__name__}: {exc}"
        time.sleep(2)
    pytest.fail(
        f"Сервис на {BASE_URL} не ответил 200 на GET /health за {timeout:.0f} с "
        f"(последний ответ: {last}). Поднимите сервис (make up) и посмотрите "
        "docker compose logs app.",
        pytrace=False,
    )


@pytest.fixture(scope="session")
def client() -> Iterator[httpx.Client]:
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as c:
        wait_until_healthy(c)
        yield c
