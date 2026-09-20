# ABOUTME: Stage 4 metrics of the URL shortener: HTTP counters and histogram with templated path,
# ABOUTME: and the business metric redirects_total growing on each 307.
import httpx

from contract_tests.helpers import metric_samples, metric_sum, require, unique_suffix


def create(client: httpx.Client) -> str:
    resp = client.post("/links", json={"url": f"https://example.com/metrics/{unique_suffix()}"})
    require(resp.status_code == 201, f"POST /links: ожидали 201, получили {resp.status_code}.")
    return str(resp.json()["code"])


def test_http_requests_total_uses_route_template(client: httpx.Client) -> None:
    code = create(client)
    before = metric_sum(
        metric_samples(client), "http_requests_total", method="GET", path="/links/{code}"
    )
    for _ in range(5):
        client.get(f"/links/{code}")
    samples = metric_samples(client)
    after = metric_sum(samples, "http_requests_total", method="GET", path="/links/{code}")
    raw_paths = {labels.get("path") for name, labels, _ in samples if name == "http_requests_total"}
    require(
        f"/links/{code}" not in raw_paths,
        f"В метке path метрики http_requests_total сырой путь /links/{code}. Нужен шаблон "
        "маршрута (/links/{code}): иначе каждая ссылка порождает свой временной ряд.",
    )
    require(
        after - before >= 5,
        f'После 5 запросов GET /links/{{code}} счётчик http_requests_total{{method="GET", '
        f'path="/links/{{code}}"}} вырос на {after - before:g}, ждали не меньше 5.',
    )


def test_unknown_paths_do_not_create_series(client: httpx.Client) -> None:
    raw = f"/no/such/page-{unique_suffix()}"
    before_404 = metric_sum(metric_samples(client), "http_requests_total", status="404")
    client.get(raw)
    samples = metric_samples(client)
    paths = {labels.get("path") for name, labels, _ in samples if name == "http_requests_total"}
    require(
        raw not in paths,
        f"Запрос на несуществующий путь {raw} создал в http_requests_total метку path с сырым "
        "путём. В path — только шаблон маршрута; для запросов мимо маршрутов — одно общее "
        "значение, иначе любой сканер создаст тысячи временных рядов.",
    )
    after_404 = metric_sum(samples, "http_requests_total", status="404")
    require(
        after_404 - before_404 >= 1,
        'Ответ 404 не попал в http_requests_total с меткой status="404". Считайте метрики для '
        "любого ответа, включая ошибки, — иначе доля 5xx и алерт HighErrorRate не работают.",
    )


def test_request_duration_histogram(client: httpx.Client) -> None:
    client.get("/health")
    names = {name for name, _, _ in metric_samples(client)}
    require(
        "http_request_duration_seconds_bucket" in names,
        "В /metrics нет гистограммы http_request_duration_seconds (сэмплов *_bucket). "
        "Используйте Histogram из prometheus-client с метками method и path.",
    )


def test_redirects_total_grows(client: httpx.Client) -> None:
    code = create(client)
    before = metric_sum(metric_samples(client), "redirects_total")
    client.get(f"/{code}", follow_redirects=False)
    after = metric_sum(metric_samples(client), "redirects_total")
    require(
        after - before >= 1,
        f"После перехода по /{code} бизнес-метрика redirects_total выросла на "
        f"{after - before:g}, ждали 1. Метрика — counter, увеличивается на каждый ответ 307.",
    )
