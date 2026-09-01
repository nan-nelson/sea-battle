# Sea Battle

REST API для игры «Морской бой».

## Стек

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- pytest
- Docker
- Docker Compose

## Запуск проекта

Клонировать репозиторий:

```bash
git clone https://github.com/nan-nelson/sea-battle.git
cd sea-battle
```

Запустить приложение и PostgreSQL:

```bash
docker compose up -d --build
```

После запуска API доступно по адресу:

http://127.0.0.1:8000

Swagger:

http://127.0.0.1:8000/docs

## Миграции

Применить миграции:

```bash
alembic upgrade head
```

## Тесты

Запустить тесты:

```bash
python -m pytest
```

## Текущие возможности

### POST /game

Создаёт новую игру и сохраняет её в PostgreSQL.

Пример ответа:

```json
{
  "session_id": "6b846c24-b7c4-4887-8d1a-ab6e212d7048"
}
```