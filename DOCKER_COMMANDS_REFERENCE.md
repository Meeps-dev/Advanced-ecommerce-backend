# Docker Commands Reference

## Profile presets

```bash
# development
docker compose up --build -d

# production-like
SEED_DATA=false LOG_FORMAT=json docker compose up --build -d
```

## Core lifecycle

```bash
docker compose up --build -d
docker compose ps
docker compose logs -f --no-log-prefix
docker compose down
```

## Gateway endpoints

```bash
open http://localhost/docs
open http://localhost/redoc
open http://localhost/openapi.json
open http://localhost:8080
curl -i http://localhost/api
```

## Service logs

```bash
docker compose logs -f api
docker compose logs -f worker
docker compose logs -f beat
docker compose logs -f flower
docker compose logs traefik --tail=200
```

## Rebuild/restart

```bash
docker compose restart
docker compose restart api
docker compose build api --no-cache
docker compose up -d api
```

## Database

```bash
docker compose exec db pg_isready
docker compose exec db psql -U postgres -d ecommerce_db
docker compose exec db psql -U postgres -d ecommerce_db -c "SELECT COUNT(*) FROM users;"
docker compose exec db psql -U postgres -d ecommerce_db -c "SELECT COUNT(*) FROM products;"
```

## Redis

```bash
docker compose exec redis redis-cli ping
docker compose exec redis redis-cli
docker compose exec redis redis-cli INFO memory
```

## Migrations and seed

```bash
docker compose exec api alembic upgrade head
docker compose exec api alembic current
docker compose exec api python seed_database.py
```

## Testing

```bash
/Users/user/advanced-ecommerce/.venv/bin/python -m pytest -q tests/integration
/Users/user/advanced-ecommerce/.venv/bin/python -m pytest -q tests/unit
/Users/user/advanced-ecommerce/.venv/bin/python -m pytest -q tests
```

## Cleanup

```bash
docker compose down
docker compose down -v
docker system prune -f
```

## Debug snippets

```bash
docker compose exec api env | sort
docker compose logs traefik --tail=300
curl -i http://localhost/docs
```
