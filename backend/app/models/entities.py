import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


def now_iso() -> str:
    """Fixed-format UTC timestamp. Stored as text so fingerprints stay byte-stable."""
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(10))  # "red" | "blue"


class TestConfig(Base):
    __tablename__ = "test_configs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    version: Mapped[int] = mapped_column(Integer, unique=True)
    system_prompt: Mapped[str] = mapped_column(Text)
    allowed_topics: Mapped[list] = mapped_column(JSON, default=list)
    blocked_topics: Mapped[list] = mapped_column(JSON, default=list)
    guardrail_rules: Mapped[list] = mapped_column(JSON, default=list)  # [{"name","pattern"}]
    canaries: Mapped[list] = mapped_column(JSON, default=list)  # raw secrets, never returned by API
    config_hash: Mapped[str] = mapped_column(String(64))
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_by: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[str] = mapped_column(String(40), default=now_iso)


class Run(Base):
    __tablename__ = "runs"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    session_id: Mapped[str] = mapped_column(String(32), index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    user_email: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(60))
    prompt: Mapped[str] = mapped_column(Text)
    prompt_hash: Mapped[str] = mapped_column(String(64))
    response_masked: Mapped[str] = mapped_column(Text, default="")
    verdict: Mapped[str] = mapped_column(String(20))
    feedback_level: Mapped[str] = mapped_column(String(10))  # detailed | coarse | none
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    leak_score: Mapped[float] = mapped_column(Float, default=0.0)
    similar_count: Mapped[int] = mapped_column(Integer, default=0)
    budget_remaining: Mapped[int] = mapped_column(Integer, default=0)
    budget_total: Mapped[int] = mapped_column(Integer, default=0)
    canary_hit: Mapped[bool] = mapped_column(Boolean, default=False)
    guardrail_violation: Mapped[bool] = mapped_column(Boolean, default=False)
    config_id: Mapped[int] = mapped_column(Integer, index=True)
    config_version: Mapped[int] = mapped_column(Integer)
    config_hash: Mapped[str] = mapped_column(String(64))
    model_version: Mapped[str] = mapped_column(String(80))
    created_at: Mapped[str] = mapped_column(String(40), index=True)
    fingerprint: Mapped[str] = mapped_column(String(64))


class Alert(Base):
    __tablename__ = "alerts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String(60))
    severity: Mapped[str] = mapped_column(String(10))  # critical | high | medium | low
    message: Mapped[str] = mapped_column(Text)
    run_id: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    created_at: Mapped[str] = mapped_column(String(40), default=now_iso)
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)


class IsolationSession(Base):
    __tablename__ = "isolation_sessions"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    state: Mapped[str] = mapped_column(String(10))  # created | running | cleaned | failed
    run_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    fresh_context: Mapped[bool] = mapped_column(Boolean, default=True)
    isolation_mode: Mapped[str] = mapped_column(String(12))  # docker | subprocess
    created_at: Mapped[str] = mapped_column(String(40))
    started_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    cleaned_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    cleanup_ok: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    cleanup_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    context_reuse_check: Mapped[str | None] = mapped_column(String(10), nullable=True)  # pass | fail
