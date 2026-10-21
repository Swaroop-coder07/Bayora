"""Central configuration, read once from environment variables (.env)."""
import os
from dataclasses import dataclass, field
from pathlib import Path


def _load_dotenv() -> None:
    """Tiny .env loader (cwd, then parent). Real environment variables always win."""
    for folder in (Path.cwd(), Path.cwd().parent):
        env_file = folder / ".env"
        if env_file.is_file():
            for line in env_file.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    value = value.split("  #")[0].split(" #")[0].strip().strip('"').strip("'")
                    os.environ.setdefault(key.strip(), value)
            return


_load_dotenv()


def _bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


@dataclass(frozen=True)
class Settings:
    app_name: str = "Bayora"
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./bayora.db")
    secret_key: str = os.getenv("SECRET_KEY", "change-me-in-production")
    token_ttl_minutes: int = int(os.getenv("TOKEN_TTL_MINUTES", "480"))
    cors_origins: list = field(
        default_factory=lambda: os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    )

    # LLM
    llm_provider: str = os.getenv("LLM_PROVIDER", "mock")  # mock | anthropic
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "claude-sonnet-5-5")

    # Isolation
    docker_enabled: bool = _bool("DOCKER_ENABLED", False)
    sandbox_image: str = os.getenv("SANDBOX_IMAGE", "bayora-backend")
    sandbox_timeout: int = int(os.getenv("SANDBOX_TIMEOUT", "60"))

    # Leakage budget
    similarity_threshold: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.6"))
    leakage_budget_total: int = int(os.getenv("LEAKAGE_BUDGET_TOTAL", "5"))
    leakage_window_minutes: int = int(os.getenv("LEAKAGE_WINDOW_MINUTES", "60"))

    # Audit
    audit_log_dir: str = os.getenv("AUDIT_LOG_DIR", "./audit_logs")

    # Seed users (development only - change them!)
    seed_blue_password: str = os.getenv("SEED_BLUE_PASSWORD", "blue123")
    seed_red_password: str = os.getenv("SEED_RED_PASSWORD", "red123")


settings = Settings()
