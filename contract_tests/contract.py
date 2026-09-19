# ABOUTME: API contract of the topic as data: operations and status codes the service must provide.
# ABOUTME: Stage 1 checks docs/openapi.yaml against it; stage 2+ tests exercise it over HTTP.

# Операции этапа 2 (docs/openapi.yaml пишется под них на этапе 1):
# (метод, путь) -> коды ответов, которые обязательно описаны в спецификации.
STAGE_2_OPERATIONS: dict[tuple[str, str], set[str]] = {
    ("post", "/links"): {"201", "422"},
    ("get", "/{code}"): {"307", "404"},
    ("get", "/links/{code}"): {"200", "404"},
    ("get", "/health"): {"200"},
}

# Длина docs/ARCHITECTURE.md в шаблоне, символов без пробельных. Заполненный
# документ должен быть длиннее хотя бы на ARCHITECTURE_MIN_ADDED.
ARCHITECTURE_TEMPLATE_LENGTH = 0
ARCHITECTURE_MIN_ADDED = 1500
