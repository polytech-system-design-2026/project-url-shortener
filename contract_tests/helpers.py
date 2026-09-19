# ABOUTME: Shared helpers for contract tests: path normalization and unique test data.
# ABOUTME: Do not edit — CI replaces contract_tests/ with the template copy at tag reference-v1.
import re
import uuid

import pytest

HTTP_METHODS = {"get", "put", "post", "delete", "patch", "head", "options", "trace"}


def normalize_path(path: str) -> str:
    """Имена параметров не важны: /links/{code} и /links/{short_code} — одна операция."""
    return re.sub(r"\{[^}]*\}", "{}", path.rstrip("/") or "/")


def unique_suffix() -> str:
    return uuid.uuid4().hex[:12]


def require(condition: object, message: str) -> None:
    """Проверка с сообщением для студента, без трейсбека тестового кода."""
    if not condition:
        pytest.fail(message, pytrace=False)
