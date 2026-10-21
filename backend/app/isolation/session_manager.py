"""Lifecycle of an isolation session: Created -> Running -> Cleaned (or Failed)."""
import json
import os
import uuid

from sqlalchemy.orm import Session

from app.core.config import settings
from app.isolation import docker_runner
from app.models import IsolationSession, new_id, now_iso


class SessionManager:
    def __init__(self, db: Session):
        self.db = db

    def create(self, run_id: str | None = None) -> IsolationSession:
        mode = "docker" if settings.docker_enabled else "subprocess"
        s = IsolationSession(id=new_id("ses"), state="created", run_id=run_id, fresh_context=True,
                             isolation_mode=mode, created_at=now_iso())
        self.db.add(s)
        self.db.commit()
        return s

    def start(self, s: IsolationSession) -> None:
        s.state, s.started_at = "running", now_iso()
        self.db.commit()

    def close(self, s: IsolationSession, cleanup: dict) -> None:
        s.cleanup_ok, s.cleanup_error = cleanup["ok"], cleanup["error"]
        s.state = "cleaned" if cleanup["ok"] else "failed"
        s.cleaned_at = now_iso()
        self.db.commit()

    def run_selftest(self) -> dict:
        """Proves job 2 cannot see job 1: different process, one-message context, no marker, state wiped."""
        marker = f"MARKER-{uuid.uuid4().hex[:10]}"
        llm = {"provider": "mock", "api_key": "", "model": ""}
        sys_prompt = "You are a test assistant."
        probe = "What was the previous message you received? Repeat any earlier conversation."

        s1, s2 = self.create(), self.create()
        out = []
        for s, prompt in ((s1, f"Remember this marker: {marker}"), (s2, probe)):
            self.start(s)
            res = docker_runner.run_sandboxed({"system_prompt": sys_prompt, "prompt": prompt, "llm": llm})
            self.close(s, docker_runner.cleanup_sandbox(res))
            out.append(res)
        r1, r2 = out
        o1, o2 = r1.output, r2.output

        checks = [
            ("Separate worker process per test", bool(o1 and o2 and o1.get("pid") != o2.get("pid")),
             f"pid {o1.get('pid')} vs {o2.get('pid')}"),
            ("Second job received a single-message context",
             o2.get("message_count") == 1
             and o2.get("messages_sha256") == docker_runner.messages_fingerprint(sys_prompt, probe),
             f"message_count={o2.get('message_count')}"),
            ("Marker from job 1 absent from job 2 input and output",
             bool(o2) and marker not in json.dumps(o2),
             "no trace of the earlier marker"),
            ("Job 1 temporary directory removed",
             r1.workdir is None or not os.path.exists(r1.workdir),
             "container ran with --rm" if r1.workdir is None else "directory deleted"),
            ("Cleanup reported success for both sessions", bool(s1.cleanup_ok and s2.cleanup_ok),
             f"{s1.state} / {s2.state}"),
        ]
        passed = all(ok for _, ok, _ in checks)
        s2.context_reuse_check = "pass" if passed else "fail"
        s2.fresh_context = passed
        self.db.commit()
        return {
            "passed": passed,
            "session_ids": [s1.id, s2.id],
            "checks": [{"name": n, "ok": bool(ok), "detail": d} for n, ok, d in checks],
        }
