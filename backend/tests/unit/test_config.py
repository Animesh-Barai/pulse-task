import pytest
from app.core.config import settings


class TestConfig:
    def test_settings_loads_default_values(self):
        assert settings.PULSE_ENV == "development"
        assert settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES == 30
        assert settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS == 7
        assert settings.PASSWORD_MIN_LENGTH == 8
        assert settings.ALGORITHM == "HS256"

    def test_settings_loads_mongodb_url(self):
        assert isinstance(settings.MONGODB_URL, str)
        assert "mongodb://" in settings.MONGODB_URL or "mongodb+srv://" in settings.MONGODB_URL

    def test_settings_loads_redis_url(self):
        assert isinstance(settings.REDIS_URL, str)
        assert "redis://" in settings.REDIS_URL

    def test_settings_loads_secret_key(self):
        assert isinstance(settings.SECRET_KEY, str)
        assert len(settings.SECRET_KEY) > 0

    def test_settings_loads_frontend_url(self):
        assert isinstance(settings.FRONTEND_URL, str)
        assert "http" in settings.FRONTEND_URL

    def test_settings_ai_flags(self):
        assert isinstance(settings.ENABLE_CLOUD_LLM, bool)

    def test_settings_rate_limits(self):
        assert settings.RATE_LIMIT_PER_MINUTE > 0
        assert settings.RATE_LIMIT_PER_HOUR > 0
