"""D. Session Isolation Sandbox - executes one job per process / container.

DOCKER_ENABLED=true  -> `docker run --rm` with no capabilities, read-only FS, memory/pid limits
DOCKER_ENABLED=false -> a fresh Python subprocess with a minimal env and a private temp dir

Both modes give a new process per test and delete temporary state afterwards. Neither is a
substitute for hardware-level isolation (see README, "Limits").
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from app.core.config import settings
from app.isolation.worker import messages_fingerprint  # noqa: F401  (re-exported)

BACKEND_ROOT = str(Path(__file__).resolve().parents[2])


@dataclass
class SandboxResult:
    mode: str
    output: dict = field(default_factory=dict)
    workdir: str | None = None
    error: str | None = None


def run_sandboxed(job: dict) -> SandboxResult:
    mode = "docker" if settings.docker_enabled else "subprocess"
    job = dict(job)
    job.setdefault(
        "llm",
        {"provider": settings.llm_provider, "api_key": settings.anthropic_api_key, "model": settings.llm_model},
    )  # credentials travel over stdin only, never argv/env
    workdir = None
    try:
        if mode == "docker":
            offline = job["llm"]["provider"] == "mock"
            cmd = [
                "docker", "run", "--rm", "-i", "--read-only", "--tmpfs", "/tmp:rw,size=16m",
                "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
                "--memory", "256m", "--pids-limit", "64",
                "--network", "none" if offline else "bridge",
                settings.sandbox_image, "python", "-m", "app.isolation.worker",
            ]
            job["workdir"] = "/tmp/run"
            kwargs = {}
        else:
            workdir = tempfile.mkdtemp(prefix="bayora-run-")
            job["workdir"] = workdir
            cmd = [sys.executable, "-m", "app.isolation.worker"]
            env = {"PATH": os.environ.get("PATH", ""), "PYTHONPATH": BACKEND_ROOT,
                   "PYTHONDONTWRITEBYTECODE": "1", "HOME": workdir}
            kwargs = {"cwd": BACKEND_ROOT, "env": env}

        proc = subprocess.run(cmd, input=json.dumps(job), capture_output=True, text=True,
                              timeout=settings.sandbox_timeout, **kwargs)
        lines = proc.stdout.strip().splitlines()
        output = json.loads(lines[-1]) if lines else {}
        if proc.returncode != 0 or "error" in output or not output:
            err = output.get("error") or proc.stderr.strip()[-300:] or "sandbox exited with an error"
            return SandboxResult(mode, {}, workdir, err)
        return SandboxResult(mode, output, workdir)
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError) as exc:
        return SandboxResult(mode, {}, workdir, f"{type(exc).__name__}: {exc}")


def cleanup_sandbox(res: SandboxResult) -> dict:
    """Deletes temporary state and PROVES it is gone (docker mode: container ran with --rm)."""
    if not res.workdir:
        return {"ok": True, "error": None}
    try:
        shutil.rmtree(res.workdir)
    except OSError as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
    if os.path.exists(res.workdir):
        return {"ok": False, "error": "temporary directory still exists after cleanup"}
    return {"ok": True, "error": None}
