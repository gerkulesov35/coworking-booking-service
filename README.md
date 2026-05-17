# Coworking Booking Service

Курсовая работа 3 курса. Сервис бронирования переговорных коворкингов: пользователи находят свободные переговорные и бронируют их по часам, менеджеры управляют комнатами и подтверждают/отклоняют брони.

## Стек

- **Backend:** Django 6, Django REST Framework, drf-spectacular
- **Хранилище:** PostgreSQL (prod / docker), SQLite (локально по умолчанию)
- **Кэш / сессии:** Redis
- **UI:** Django Templates + Bootstrap 5 (через CDN)
- **DevOps:** Docker, docker-compose, gunicorn, whitenoise, GitHub Actions, JSON-логирование, graceful shutdown

## Структура

```
.
├── config/                  Django-конфиг (settings, urls, middleware, logging, api_urls)
├── rooms/                   Переговорные + бронирования (модели, views, API, formы, команды)
│   ├── api_views.py         DRF endpoints
│   ├── api_permissions.py   IsManagerOrReadOnly
│   ├── management/commands/ seed_data
│   └── ...
├── users/                   Профиль пользователя и роли
├── templates/               base.html + страницы (Bootstrap)
├── docs/                    architecture, structure, diagrams
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── Procfile                 для Render
└── manage.py
```

## Запуск локально (без Docker)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env       # отредактировать при необходимости
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_data
python manage.py runserver
```

Открыть [http://localhost:8000/](http://localhost:8000/).

## Запуск через docker compose

```bash
docker compose up --build -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py seed_data
```

`docker-compose.yml` поднимает три сервиса: `web` (Django), `db` (PostgreSQL 16), `redis`.

## Полезные команды

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_data           # идемпотентные тестовые данные
python manage.py test                # запуск тестов (20 шт.)
python manage.py runserver
```

## Тестовые учётки (после `seed_data`)

| Логин     | Пароль          | Роль     |
|-----------|-----------------|----------|
| `user1`   | `user12345`     | user     |
| `manager1`| `manager12345`  | manager  |
| `admin1`  | `admin12345`    | admin (superuser) |

## API

- `GET  /api/rooms/` — список переговорных
- `GET  /api/rooms/{id}/` — детали переговорной
- `POST /api/rooms/` — создать переговорную (manager/admin)
- `GET  /api/bookings/` — список бронирований (пользователь видит свои, менеджер — все)
- `POST /api/bookings/` — создать бронирование (login required)
- `GET  /api/schema/` — OpenAPI 3.0 YAML
- `GET  /api/docs/` — Swagger UI

## Фаззинг (Schemathesis)

```bash
pip install schemathesis
schemathesis run http://localhost:8000/api/schema/ --base-url=http://localhost:8000
```

Schemathesis возьмёт OpenAPI-схему и автоматически прогонит набор фаззинг-запросов.

## Деплой на Render

1. Создать в Render новый Web Service из этого репозитория.
2. Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
3. Start command: `gunicorn config.wsgi:application` (либо использовать `Procfile`).
4. Подключить PostgreSQL и Redis (Render-managed). Render выдаст `DATABASE_URL` и `REDIS_URL`.
5. Задать переменные окружения:
   - `SECRET_KEY` — длинная случайная строка
   - `DEBUG=False`
   - `ALLOWED_HOSTS=<your-app>.onrender.com`
   - `DATABASE_URL=<выдан Render>`
   - `REDIS_URL=<выдан Render>`

`settings.py` распознаёт `DATABASE_URL` через `dj-database-url`, статика обслуживается `whitenoise`.

## Документация курсовой работы

В каталоге `docs/`:
- [docs/architecture.md](docs/architecture.md) — архитектура и обоснование решений
- [docs/project_structure.md](docs/project_structure.md) — структура проекта по модулям
- [docs/diagrams.md](docs/diagrams.md) — ER, deployment, component, sequence (Mermaid)
