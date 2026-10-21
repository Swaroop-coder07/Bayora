from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.api.deps import require_blue
from app.core.security import hmac_hex
from app.db.database import get_db
from app.models import TestConfig, User, now_iso
from app.schemas import ConfigIn, ConfigOut
from app.services import verification

router = APIRouter(prefix="/configs", tags=["configs"])


def compute_config_hash(system_prompt, allowed, blocked, rules, canaries, version) -> str:
    """Canaries enter the hash only as keyed HMACs, so the hash never reveals them."""
    return verification.sha256_hex(verification.canonical({
        "version": version, "system_prompt": system_prompt, "allowed": allowed, "blocked": blocked,
        "rules": rules, "canaries_hmac": [hmac_hex(c) for c in canaries],
    }))


def _mask(secret: str) -> str:
    return secret[:2] + "*" * 6


def to_out(c: TestConfig) -> ConfigOut:
    return ConfigOut(id=c.id, version=c.version, system_prompt=c.system_prompt, allowed_topics=c.allowed_topics,
                     blocked_topics=c.blocked_topics, guardrail_rules=c.guardrail_rules,
                     canaries_masked=[_mask(x) for x in c.canaries], config_hash=c.config_hash,
                     is_active=c.is_active, created_by=c.created_by, created_at=c.created_at)


def create_config(db: Session, body: ConfigIn, author: str) -> TestConfig:
    latest = db.scalar(select(TestConfig).order_by(TestConfig.version.desc()))
    canaries = [c.strip() for c in body.canaries if c.strip()] or (latest.canaries if latest else [])
    if any(len(c) < 8 for c in canaries):
        raise HTTPException(422, "Each canary must be at least 8 characters to avoid false positives.")
    version = (latest.version if latest else 0) + 1
    rules = [r.model_dump() for r in body.guardrail_rules]
    cfg = TestConfig(
        version=version, system_prompt=body.system_prompt, allowed_topics=body.allowed_topics,
        blocked_topics=body.blocked_topics, guardrail_rules=rules, canaries=canaries,
        config_hash=compute_config_hash(body.system_prompt, body.allowed_topics, body.blocked_topics, rules, canaries, version),
        is_active=False, created_by=author, created_at=now_iso(),
    )
    db.add(cfg)
    db.commit()
    return cfg


def _activate(db: Session, cfg: TestConfig) -> None:
    db.execute(update(TestConfig).values(is_active=False))
    cfg.is_active = True
    db.commit()


@router.get("", response_model=list[ConfigOut])
def list_configs(_: User = Depends(require_blue), db: Session = Depends(get_db)):
    return [to_out(c) for c in db.scalars(select(TestConfig).order_by(TestConfig.version.desc()))]


@router.get("/active", response_model=ConfigOut | None)
def active_config(_: User = Depends(require_blue), db: Session = Depends(get_db)):
    c = db.scalar(select(TestConfig).where(TestConfig.is_active.is_(True)))
    return to_out(c) if c else None


@router.post("", response_model=ConfigOut)
def save_config(body: ConfigIn, user: User = Depends(require_blue), db: Session = Depends(get_db)):
    cfg = create_config(db, body, user.email)
    if body.activate:
        _activate(db, cfg)
    return to_out(cfg)


@router.post("/{config_id}/activate", response_model=ConfigOut)
def activate_config(config_id: int, _: User = Depends(require_blue), db: Session = Depends(get_db)):
    cfg = db.get(TestConfig, config_id)
    if cfg is None:
        raise HTTPException(404, "Configuration not found")
    _activate(db, cfg)
    return to_out(cfg)
