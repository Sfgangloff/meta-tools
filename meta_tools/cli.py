from __future__ import annotations
import json
import subprocess
from typing import Any

from .config import ANALYZER_MODEL

# Base flags applied to every `claude -p` invocation we make.
#
# - --strict-mcp-config + empty mcpServers: prevent recursive load of meta-tools
#   (and every other MCP server) into the subprocess. Without this, calling out
#   from inside the meta-tools MCP would re-instantiate the whole MCP shelf.
# - --disable-slash-commands: don't drag in skills we don't need.
# - --no-session-persistence: this is a one-shot call, not a resumable session.
_BASE_FLAGS: list[str] = [
    "-p",
    "--output-format", "json",
    "--no-session-persistence",
    "--disable-slash-commands",
    "--strict-mcp-config",
    "--mcp-config", '{"mcpServers":{}}',
]


class CliError(RuntimeError):
    pass


def _run(args: list[str], user_prompt: str) -> dict:
    """Invoke `claude -p ...` and return the parsed JSON envelope."""
    proc = subprocess.run(
        ["claude", *args, user_prompt],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise CliError(
            f"claude CLI exited with code {proc.returncode}: "
            f"{(proc.stderr or proc.stdout or '').strip()[:500]}"
        )

    try:
        envelope = json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        raise CliError(
            f"claude CLI did not return valid JSON: {e}. "
            f"Output head: {proc.stdout[:300]!r}"
        )

    if envelope.get("is_error"):
        raise CliError(
            f"claude CLI returned error: {envelope.get('result', '<no message>')[:500]}"
        )
    return envelope


def complete_json(
    system_prompt: str,
    user_prompt: str,
    json_schema: dict[str, Any],
    model: str | None = None,
) -> dict:
    """
    Run a structured-output completion via the Claude Code CLI. Returns the
    object that matches `json_schema` (i.e. the envelope's `structured_output`).
    """
    args = [
        *_BASE_FLAGS,
        "--model", model or ANALYZER_MODEL,
        "--system-prompt", system_prompt,
        "--json-schema", json.dumps(json_schema),
    ]
    envelope = _run(args, user_prompt)

    structured = envelope.get("structured_output")
    if not isinstance(structured, dict):
        raise CliError(
            f"claude CLI returned no structured_output. "
            f"Envelope keys: {sorted(envelope.keys())}. "
            f"result head: {str(envelope.get('result', ''))[:300]!r}"
        )
    return structured


def complete_text(
    system_prompt: str,
    user_prompt: str,
    model: str | None = None,
) -> str:
    """Run a free-form text completion via the Claude Code CLI. Returns the model's text."""
    args = [
        *_BASE_FLAGS,
        "--model", model or ANALYZER_MODEL,
        "--system-prompt", system_prompt,
    ]
    envelope = _run(args, user_prompt)
    text = envelope.get("result")
    if not isinstance(text, str) or not text.strip():
        raise CliError(
            f"claude CLI returned empty result. Envelope keys: {sorted(envelope.keys())}."
        )
    return text
