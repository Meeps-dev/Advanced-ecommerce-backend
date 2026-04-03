"""Alembic environment configuration."""

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys
from app.shared import enums
from app.modules.addresses.infrastructure.models import shipping_address
from app.modules.auth.infrastructure.models import refresh_token
from app.modules.cart.infrastructure.models import cart, cart_item
from app.modules.catalog.infrastructure.models import category, product, product_image
from app.modules.inventory.infrastructure.models import inventory
from app.modules.orders.infrastructure.models import order, order_item
from app.modules.payments.infrastructure.models import payment
from app.modules.reviews.infrastructure.models import review
from app.modules.users.infrastructure.models import user
# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.base import Base
from app.core.config import settings

# this is the Alembic Config object, which provides
# the values of the [alembic] section of the .ini
# file as Python dictionary for use within Python code
# that may update the environment conditionally.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically as specified in the file
# config.file_config is the Alembic config file location
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = settings.database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.database_url
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
