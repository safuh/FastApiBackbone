import os
import subprocess
import sys

import pytest


@pytest.mark.integration
def test_alembic_upgrade_and_downgrade() -> None:
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is not configured")

    env = os.environ.copy()
    env["DATABASE_URL"] = url
    subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], check=True, env=env)
    subprocess.run([sys.executable, "-m", "alembic", "downgrade", "base"], check=True, env=env)
    subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], check=True, env=env)
