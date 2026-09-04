"""SECRET_KEY и DATABASE_URL обязаны приходить из окружения.

Раньше оба падали тихо на рабочий встроенный дефолт — реальный пароль,
реальный (общий для всех сред) ключ подписи. Настройки уже импортированы в
этом процессе pytest'ом, поэтому проверить поведение можно только новым
процессом — так же, как это увидел бы `manage.py` при реальном старте.
"""

import os
import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent

# Валидный минимум, вместе с которым Django стартует, — база для двух тестов
# ниже: каждый снимает ровно одну переменную и проверяет, что упало из-за
# именно её отсутствия, а не из-за чего-то ещё.
_BASE_ENV = {
    "DJANGO_SECRET_KEY": "test-only-not-a-real-secret",
    "DATABASE_URL": "sqlite:///:memory:",
    "DJANGO_SETTINGS_MODULE": "config.settings",
    "PATH": os.environ.get("PATH", ""),
}


def _run_with_env(env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", "import django; django.setup()"],
        cwd=BACKEND_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )


def test_missing_django_secret_key_fails_fast():
    env = dict(_BASE_ENV)
    del env["DJANGO_SECRET_KEY"]

    result = _run_with_env(env)

    assert result.returncode != 0
    assert "DJANGO_SECRET_KEY" in result.stderr
    assert "ImproperlyConfigured" in result.stderr


def test_missing_database_url_fails_fast():
    env = dict(_BASE_ENV)
    del env["DATABASE_URL"]

    result = _run_with_env(env)

    assert result.returncode != 0
    assert "DATABASE_URL" in result.stderr
    assert "ImproperlyConfigured" in result.stderr


def test_settings_start_cleanly_with_both_vars_present():
    result = _run_with_env(dict(_BASE_ENV))

    assert result.returncode == 0, result.stderr
