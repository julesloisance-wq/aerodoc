from aerodoc.config import Settings


def test_defaults_point_to_local_database():
    settings = Settings(_env_file=None)
    assert settings.database_url.startswith("postgresql://")
    assert settings.llm_provider == "gemini"


def test_environment_overrides(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@example:5432/x")
    assert Settings(_env_file=None).database_url == "postgresql://u:p@example:5432/x"
