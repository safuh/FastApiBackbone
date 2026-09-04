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
    command = [sys.executable, "-m", "alembic"]
    subprocess.run([*command, "upgrade", "head"], check=True, env=env)
    subprocess.run([*command, "downgrade", "base"], check=True, env=env)
    subprocess.run([*command, "upgrade", "head"], check=True, env=env)
