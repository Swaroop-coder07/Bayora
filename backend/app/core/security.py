"""Password hashing and JWT helpers (no database access here)."""
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 200_000)
    return f"{salt}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, digest = stored.split("$")
    except ValueError:
        return False
    return hmac.compare_digest(hash_password(password, salt).split("$")[1], digest)


def create_token(email: str, role: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.token_ttl_minutes)
    return jwt.encode({"sub": email, "role": role, "exp": exp}, settings.secret_key, algorithm="HS256")


def decode_token(token: str) -> dict:
    """Raises jwt.PyJWTError on invalid / expired tokens."""
    return jwt.decode(token, settings.secret_key, algorithms=["HS256"])


def hmac_hex(value: str) -> str:
    """Keyed hash used for fingerprints of secrets (e.g. canaries) in config hashes."""
    return hmac.new(settings.secret_key.encode(), value.encode(), hashlib.sha256).hexdigest()
