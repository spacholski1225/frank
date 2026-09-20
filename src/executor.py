"""Shared Codex CLI runner for chat and digest jobs."""
import json
import os
import subprocess
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def execute_codex(prompt: str, session_id: str | None = None, *,
                  timeout: int | None = None, web_search: bool = False,
                  cwd: Path | None = None) -> tuple[str, str]:
    """Run a bounded CLI job and return its final answer and conversation ID.

    Prompts go through stdin; progress events never become digest content.
    Codex reads source files; callers are responsible for saving reports.
    """
    timeout = timeout if timeout is not None else int(os.getenv("CODEX_TIMEOUT", "600"))
    with tempfile.TemporaryDirectory(prefix="frank-codex-") as temp:
        output = Path(temp) / "answer.md"
        cmd = [os.getenv("CODEX_BIN", "codex"), "-a", "never", "-s", "read-only",
               "-c", 'web_search="live"' if web_search else 'web_search="disabled"',
               "exec"]
        if session_id:
            cmd.extend(["resume", session_id])
        cmd.extend(["--json", "--output-last-message", str(output)])
        model = os.getenv("CODEX_MODEL")
        if model:
            cmd.extend(["--model", model])
        cmd.append("-")
        try:
            result = subprocess.run(cmd, input=prompt, capture_output=True,
                                    text=True, timeout=timeout,
                                    cwd=str(cwd or PROJECT_ROOT))
        except FileNotFoundError as exc:
            raise RuntimeError("Codex CLI not found; install it or set CODEX_BIN") from exc
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError(f"Codex timeout after {timeout}s") from exc
        if result.returncode != 0:
            raise RuntimeError(f"Codex execution failed (exit {result.returncode}): {result.stderr[-2000:]}")
        thread_id = session_id or ""
        for line in result.stdout.splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError("Invalid JSON event from Codex") from exc
            if not isinstance(event, dict):
                raise ValueError("Invalid JSON event from Codex")
            if event.get("type") == "thread.started":
                thread_id = event.get("thread_id", thread_id)
            if event.get("type") in ("turn.failed", "error"):
                raise RuntimeError(f"Codex execution failed: {event.get('error', event.get('message', 'unknown error'))}")
        answer = output.read_text(encoding="utf-8").strip() if output.exists() else ""
        if not answer:
            raise ValueError("Codex returned no final answer")
        if not thread_id:
            raise ValueError("Codex returned no conversation ID")
        return answer, thread_id
