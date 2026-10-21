from pydantic import BaseModel, ConfigDict, Field


class LoginIn(BaseModel):
    email: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    email: str
    role: str


class UserOut(BaseModel):
    email: str
    role: str


class TestIn(BaseModel):
    prompt: str = Field(min_length=1, max_length=4000)
    category: str = "prompt_injection"


class TestResultOut(BaseModel):
    run_id: str
    session_id: str
    verdict: str
    feedback_level: str
    response: str | None
    risk_score: float
    similar_count: int
    budget_total: int
    budget_remaining: int
    budget_level: str
    canary_detected: bool
    paused: bool
    model_version: str


class GuardrailRule(BaseModel):
    name: str
    pattern: str


class ConfigIn(BaseModel):
    system_prompt: str = Field(min_length=1)
    allowed_topics: list[str] = []
    blocked_topics: list[str] = []
    guardrail_rules: list[GuardrailRule] = []
    canaries: list[str] = []  # empty -> keep canaries of the current version
    activate: bool = False


class ConfigOut(BaseModel):
    id: int
    version: int
    system_prompt: str
    allowed_topics: list[str]
    blocked_topics: list[str]
    guardrail_rules: list[GuardrailRule]
    canaries_masked: list[str]
    config_hash: str
    is_active: bool
    created_by: str
    created_at: str


class RunOut(BaseModel):
    id: str
    created_at: str
    category: str
    user_email: str
    verdict: str
    feedback_level: str
    risk_score: float
    canary_hit: bool
    guardrail_violation: bool
    prompt_hash: str
    config_hash: str
    config_version: int
    model_version: str
    fingerprint: str
    session_id: str


class RunDetailOut(RunOut):
    prompt: str | None
    response: str | None
    leak_score: float
    similar_count: int
    budget_remaining: int
    budget_total: int
    audit_log: list[dict]
    audit_chain_ok: bool


class VerifyOut(BaseModel):
    run_id: str
    status: str  # "Verified" | "Verification Failed"
    expected: str
    actual: str
    checked_at: str


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    type: str
    severity: str
    message: str
    run_id: str | None
    created_at: str
    acknowledged: bool


class SessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    state: str
    run_id: str | None
    fresh_context: bool
    isolation_mode: str
    created_at: str
    started_at: str | None
    cleaned_at: str | None
    cleanup_ok: bool | None
    cleanup_error: str | None
    context_reuse_check: str | None
