# Материалы к этапу 2. MVP

## Что почитать

- [FastAPI: Handling Errors](https://fastapi.tiangolo.com/tutorial/handling-errors/) — `HTTPException`, коды ответов и формат `{"detail": ...}`, ошибки валидации 422.
- [FastAPI: Custom Response](https://fastapi.tiangolo.com/advanced/custom-response/) — `RedirectResponse` и другие классы ответов.
- [SQLAlchemy 2.0: ORM Quick Start](https://docs.sqlalchemy.org/en/20/orm/quickstart.html) — модели через `Mapped` и `mapped_column`, сессия, `select`.
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html) — `alembic init`, первая миграция, `upgrade head`.
- [Docker Compose: Control startup order](https://docs.docker.com/compose/how-tos/startup-order/) — `healthcheck` и `depends_on` с `condition: service_healthy`, чтобы сервис не стартовал раньше базы.
- [Двенадцать факторов: конфигурация](https://12factor.net/ru/config) — почему настройки живут в переменных окружения, а не в коде.

## Вопросы для самопроверки

1. Что произойдёт, если два запроса одновременно сгенерируют один и тот же код? Где это ловится — в коде или в БД?
2. Почему `/health` должен ходить в базу, а не просто возвращать 200?
3. Чем миграция alembic лучше `Base.metadata.create_all()`? Что будет с данными при изменении схемы в каждом из вариантов?
4. Что делает каждый из трёх слоёв api / service / repository и что сломается, если перенести валидацию URL в роутер?
5. Почему внутри контейнера сервис должен слушать `0.0.0.0`, а не `127.0.0.1`?
