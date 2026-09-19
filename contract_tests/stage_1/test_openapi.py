# ABOUTME: Stage 1 checks for docs/openapi.yaml: valid OpenAPI 3.x, every contract operation present
# ABOUTME: with its required response codes, and every operation has a summary.
from pathlib import Path
from typing import Any

import pytest
import yaml
from openapi_spec_validator import validate
from openapi_spec_validator.validation.exceptions import OpenAPIValidationError

from contract_tests.contract import STAGE_2_OPERATIONS
from contract_tests.helpers import HTTP_METHODS, normalize_path, require

OPENAPI = Path(__file__).resolve().parents[2] / "docs" / "openapi.yaml"


def load_spec() -> dict[str, Any]:
    if not OPENAPI.exists():
        pytest.fail(
            "Не найден docs/openapi.yaml. Верните файл из шаблона и опишите в нём API "
            "(tasks/TASK-1.md).",
            pytrace=False,
        )
    raw = OPENAPI.read_text(encoding="utf-8")
    if "\t" in raw:
        line = next(n for n, s in enumerate(raw.splitlines(), start=1) if "\t" in s)
        pytest.fail(
            f"В docs/openapi.yaml табуляция (первая — строка {line}). YAML допускает только "
            "пробелы: включите в редакторе «отступ пробелами» и замените табы.",
            pytrace=False,
        )
    # pytest.fail вызывается вне except, чтобы в выводе не было исходного исключения.
    error = ""
    try:
        spec = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        error = str(exc)
    require(not error, f"docs/openapi.yaml не читается как YAML: {error}")
    if not isinstance(spec, dict):
        pytest.fail(
            "docs/openapi.yaml пустой или не является YAML-объектом. Начните с полей "
            "openapi, info и paths (пример — в самом файле шаблона).",
            pytrace=False,
        )
    return spec


def operations(spec: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for path, item in (spec.get("paths") or {}).items():
        for method, op in (item or {}).items():
            if method in HTTP_METHODS and isinstance(op, dict):
                result[(method, normalize_path(path))] = op
    return result


def test_spec_is_valid_openapi_3() -> None:
    spec = load_spec()
    version = str(spec.get("openapi", ""))
    require(
        version.startswith("3."),
        f"Поле openapi = {version!r}. Нужна спецификация OpenAPI 3.x: первая строка файла "
        "openapi: 3.1.0 (или 3.0.3).",
    )
    error = ""
    try:
        validate(spec)
    except OpenAPIValidationError as exc:
        where = " → ".join(str(p) for p in exc.absolute_path) or "корень документа"
        error = f"{exc.message}\nГде: {where}"
    require(not error, f"docs/openapi.yaml не проходит валидацию OpenAPI: {error}")


def test_contract_operations_present() -> None:
    ops = operations(load_spec())
    missing = [
        f"{m.upper()} {p}" for (m, p) in STAGE_2_OPERATIONS if (m, normalize_path(p)) not in ops
    ]
    require(
        not missing,
        "В docs/openapi.yaml не описаны операции из контракта (tasks/TASK-1.md): "
        + ", ".join(missing),
    )


def test_contract_response_codes_described() -> None:
    ops = operations(load_spec())
    problems = []
    for (method, path), codes in STAGE_2_OPERATIONS.items():
        op = ops.get((method, normalize_path(path)))
        if op is None:
            continue  # отсутствие операции проверяет test_contract_operations_present
        described = {str(code) for code in (op.get("responses") or {})}
        lacking = sorted(codes - described)
        if lacking:
            problems.append(f"{method.upper()} {path}: нет ответов {', '.join(lacking)}")
    require(
        not problems,
        "В docs/openapi.yaml описаны не все коды ответов из контракта. Ошибки — такая же "
        "часть контракта, как успешный ответ:\n  " + "\n  ".join(problems),
    )


def test_every_operation_has_summary() -> None:
    ops = operations(load_spec())
    without = [f"{m.upper()} {p}" for (m, p), op in ops.items() if not op.get("summary")]
    require(
        not without,
        "У операций нет summary (одна строка о том, что делает операция): " + ", ".join(without),
    )
