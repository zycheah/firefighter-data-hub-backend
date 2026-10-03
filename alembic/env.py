import os
import sys
from pathlib import Path

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

# Load .env from Backend/.env
load_dotenv(BASE_DIR / ".env")

from app.db.base import Base
from app.db import base_class  # noqa: F401

config = context.config

# Prefer DATABASE_URL, but also support old DB_CONNECTION name
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("DB_CONNECTION")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL or DB_CONNECTION is not set. "
        "Add it to Backend/.env or export it before running Alembic."
    )

config.set_main_option("sqlalchemy.url", DATABASE_URL)

target_metadata = Base.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()