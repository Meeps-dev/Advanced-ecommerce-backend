# Docker Quick Start

Use gateway URLs for API and docs.

## Development in 60 seconds

```bash
docker compose up --build -d
docker compose logs -f --no-log-prefix
```

Open:

- http://localhost/api
- http://localhost/docs
- http://localhost/redoc
- http://localhost/openapi.json

## Production-like in 60 seconds

```bash
SEED_DATA=false LOG_FORMAT=json docker compose up --build -d
docker compose logs -f --no-log-prefix
```

Open:

- http://localhost/api
- http://localhost/docs
- http://localhost/openapi.json

## Health checks

```bash
curl -fsS http://localhost/docs >/dev/null && echo "docs ok"
curl -fsS http://localhost/openapi.json >/dev/null && echo "openapi ok"
docker compose exec db pg_isready
docker compose exec redis redis-cli ping
```

## Common commands

```bash
docker compose exec api alembic upgrade head
docker compose exec api alembic current
docker compose exec api python seed_database.py
docker compose restart
docker compose down
```

## Test users

- admin@example.com / AdminPass123!
- customer1@example.com / CustomerPass123!
- customer2@example.com / CustomerPass456!
- testing@example.com / TestPass789!
