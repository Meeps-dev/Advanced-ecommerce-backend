#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}[*] Entrypoint script starting...${NC}"

# Wait for database to be ready using pg_isready
echo -e "${YELLOW}[*] Waiting for PostgreSQL to be ready...${NC}"
DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-5432}
DB_USER=${POSTGRES_USER:-postgres}
DB_NAME=${POSTGRES_DB:-ecommerce_db}

for i in {1..30}; do
    if pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME"; then
        echo -e "${GREEN}[✓] PostgreSQL is ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}[!] PostgreSQL failed to become ready after 30 retries${NC}"
        exit 1
    fi
    echo -e "${YELLOW}[*] Attempt $i/30: PostgreSQL not ready yet, retrying...${NC}"
    sleep 1
done

# Wait for Redis to be ready
echo -e "${YELLOW}[*] Waiting for Redis to be ready...${NC}"
REDIS_HOST=${REDIS_HOST:-redis}
REDIS_PORT=${REDIS_PORT:-6379}

for i in {1..30}; do
    if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping >/dev/null 2>&1; then
        echo -e "${GREEN}[✓] Redis is ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}[!] Redis failed to become ready after 30 retries${NC}"
        exit 1
    fi
    echo -e "${YELLOW}[*] Attempt $i/30: Redis not ready yet, retrying...${NC}"
    sleep 1
done

# Run Alembic migrations
if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo -e "${YELLOW}[*] Running database migrations...${NC}"
    if alembic upgrade head; then
        echo -e "${GREEN}[✓] Migrations completed successfully${NC}"
    else
        echo -e "${RED}[!] Migrations failed${NC}"
        exit 1
    fi
fi

# Seed data if seed_database.py exists and SEED_DATA=true
if [ "$SEED_DATA" = "true" ] && [ -f "/app/seed_database.py" ]; then
    echo -e "${YELLOW}[*] Seeding test data...${NC}"
    if python /app/seed_database.py; then
        echo -e "${GREEN}[✓] Test data seeded successfully${NC}"
    else
        echo -e "${RED}[!] Seeding failed (non-critical, continuing...)${NC}"
    fi
fi

echo -e "${GREEN}[✓] Entrypoint setup completed${NC}"

# Execute the main command
exec "$@"