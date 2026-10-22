
"""Tests for application configuration."""

import pytest
from pydantic import ValidationError

from aquaops.config import Settings


def make_settings(**overrides: object) -> Settings:
    """Create isolated settings without reading a local .env file."""
    values: dict[str, object] = {
        "app_env": "testing",
        "log_level": "INFO",
        "postgres_db": "aquaops",
        "postgres_user": "aquaops_app",
        "postgres_password": "test_password",
        "db_host": "localhost",
        "db_port": 5432,
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)


def test_database_url_uses_psycopg_driver() -> None:
    settings = make_settings()

    assert settings.database_url.drivername == "postgresql+psycopg"
    assert settings.database_url.host == "localhost"
    assert settings.database_url.port == 5432
    assert settings.database_url.database == "aquaops"


def test_database_url_handles_special_password_characters() -> None:
    settings = make_settings(postgres_password="p@ss:/word#1")

    assert settings.database_url.password == "p@ss:/word#1"


def test_invalid_database_port_is_rejected() -> None:
    with pytest.raises(ValidationError):
        make_settings(db_port=70000)


def test_empty_database_name_is_rejected() -> None:
    with pytest.raises(ValidationError):
        make_settings(postgres_db="")


def test_production_environment_is_accepted() -> None:
    settings = make_settings(app_env="production")

    assert settings.app_env == "production"
