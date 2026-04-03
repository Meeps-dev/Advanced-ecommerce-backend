
import os
import uuid
import pytest
from fastapi.testclient import TestClient


def _load_test_env_early() -> None:
    env_file = ".test.env"
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                os.environ.setdefault(key, value)

    # Keep tests deterministic and quiet regardless of local .env values.
    os.environ.setdefault("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/ecommerce_test")
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
    os.environ["SECRET_KEY"] = "test-secret-key-at-least-32-characters-long"
    os.environ["SENTRY_DSN"] = ""


_load_test_env_early()


@pytest.fixture(scope="session", autouse=True)
def load_test_env():
    _load_test_env_early()


@pytest.fixture
def random_email():
    return f"test_{uuid.uuid4().hex}@example.com"


@pytest.fixture
def client(load_test_env):
    from app.main import app
    return TestClient(app)
