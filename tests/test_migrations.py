import os
import subprocess
import sys

import pytest
from sqlalchemy import create_engine, text


@pytest.mark.integration
def test_alembic_upgrade_and_downgrade() -> None:
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is not configured")

    env = os.environ.copy()
    env["DATABASE_URL"] = url
    command = [sys.executable, "-m", "alembic"]
    subprocess.run([*command, "upgrade", "head"], check=True, env=env)

    sync_url = url.replace("+asyncpg", "+psycopg")
    with create_engine(sync_url).connect() as connection:
        user_columns = {
            row[0]
            for row in connection.execute(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name = 'users'"
                )
            )
        }
    assert {"id", "identifier", "password_hash", "created_at"} <= user_columns

    subprocess.run([*command, "downgrade", "base"], check=True, env=env)
    subprocess.run([*command, "upgrade", "head"], check=True, env=env)
