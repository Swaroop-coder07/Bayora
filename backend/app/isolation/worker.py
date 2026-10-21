"""Runs INSIDE the sandbox (a Docker container, or a fresh Python process).

Reads one JSON job from stdin, builds a brand-new single-message context, calls the
model and prints one JSON result. It imports no database code and keeps no state.
Run as:  python -m app.isolation.worker
"""
import hashlib
import json
import os
import sys
import tempfile

from app.services.llm_service import generate


def messages_fingerprint(system: str, prompt: str) -> str:
    body = {"system": system, "messages": [{"role": "user", "content": prompt}]}
    return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()


def main() -> None:
    job = json.loads(sys.stdin.read())
    system, prompt = job["system_prompt"], job["prompt"]
    workdir = job.get("workdir") or tempfile.mkdtemp(prefix="bayora-")
    os.makedirs(workdir, exist_ok=True)

    messages = [{"role": "user", "content": prompt}]  # fresh context: exactly one message
    with open(os.path.join(workdir, "scratch.json"), "w") as f:  # temporary state to be cleaned up
        json.dump({"messages": messages}, f)

    llm = job.get("llm", {})
    try:
        res = generate(system, prompt, llm.get("provider", "mock"), llm.get("api_key", ""), llm.get("model", ""))
    except Exception as exc:  # noqa: BLE001 - report any provider failure to the referee
        print(json.dumps({"error": f"{type(exc).__name__}: {exc}"}))
        sys.exit(1)

    print(
        json.dumps(
            {
                "text": res.text,
                "model_version": res.model_version,
                "pid": os.getpid(),
                "workdir": workdir,
                "message_count": len(messages),
                "messages_sha256": messages_fingerprint(system, prompt),
            }
        )
    )


if __name__ == "__main__":
    main()
