# Материалы к этапу 1. Архитектура

## Что почитать

- [Learn OpenAPI](https://learn.openapis.org/) — официальное введение в OpenAPI: структура документа, пути, операции, ответы, компоненты. Начните отсюда, прежде чем писать `openapi.yaml`.
- [Спецификация OpenAPI 3.1.0](https://spec.openapis.org/oas/v3.1.0) — справочник: когда нужно точно узнать, какие поля есть у Response Object или Parameter Object.
- [Mermaid: Sequence diagrams](https://mermaid.js.org/syntax/sequenceDiagram.html) — синтаксис диаграмм последовательности: удобно показать, кто кого вызывает при создании ссылки и переходе. Для схемы компонентов — [flowchart](https://mermaid.js.org/syntax/flowchart.html).
- [GitHub: Creating diagrams](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams) — как GitHub рисует блоки `mermaid` прямо в Markdown.
- [System Design Primer: Design Pastebin.com (or Bit.ly)](https://github.com/donnemartin/system-design-primer/blob/master/solutions/system_design/pastebin/README.md) — разбор похожей задачи: сценарии, оценка нагрузки, генерация кода, кэширование. Там же, в [README](https://github.com/donnemartin/system-design-primer), раздел Appendix с таблицей степеней двойки и задержками — пригодится для оценки нагрузки.
- [GitHub: Creating a repository from a template](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template) — как создать свой репозиторий из шаблона.

## Вопросы для самопроверки

1. Сколько запросов в секунду в пике получит ваш сервис на чтение и на запись? Из каких допущений это следует?
2. Какой запрос к БД самый частый и какой индекс его ускоряет? Что будет с этим запросом без индекса на 3,65 млн строк?
3. Сколько различных кодов даёт ваш алфавит и длина кода? Как сервис поведёт себя при коллизии?
4. Почему редирект — 307, а не 301? Что изменится для статистики переходов, если браузер закэширует постоянный редирект?
5. Зачем писать `openapi.yaml` до кода, если FastAPI сгенерирует спецификацию сам?
