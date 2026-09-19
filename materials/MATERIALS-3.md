# Материалы к этапу 3. Масштабирование

## Что почитать

- [Redis Strings](https://redis.io/docs/latest/develop/data-types/strings/) — `GET`, `SET`, опции времени жизни ключа: всё, что нужно для кэша «код → URL».
- [Redis Streams](https://redis.io/docs/latest/develop/data-types/streams/) — поток событий, consumer group, `XREADGROUP` и `XACK`: как читать очередь и не терять события при падении воркера.
- [Шаблон «Кэш на стороне приложения» (cache-aside)](https://learn.microsoft.com/ru-ru/azure/architecture/patterns/cache-aside) — когда читать из кэша, когда из БД и как кэш наполняется. На русском.
- [redis-py](https://redis.readthedocs.io/en/stable/) — клиент Redis для Python.
- [Locust: Quick start](https://docs.locust.io/en/stable/quickstart.html) — как описать пользователя и задачи в `locustfile.py`.
- [Locust: Running without the web UI](https://docs.locust.io/en/stable/running-without-web-ui.html) — запуск `--headless` с параметрами `--users`, `--spawn-rate`, `--run-time`.

## Вопросы для самопроверки

1. Что происходит с запросом `GET /{code}`, если ключа нет в кэше? А если нет и в БД?
2. Почему для счётчика переходов нужна очередь, а не `UPDATE` прямо в обработчике редиректа?
3. Что будет с событиями перехода, если воркер упадёт после чтения из очереди, но до записи в БД? Как это решает ваша реализация?
4. Нужен ли TTL у ключей кэша ссылок? Что изменилось бы, если бы ссылки можно было удалять?
5. Как вы объясните разницу в p95 до и после Redis? Где сервис тратил время раньше?
