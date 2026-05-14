from __future__ import annotations
import ast
from pathlib import Path

from .schemas import ToolSpec, DevelopmentResult
from .prompt_templates import DEVELOPER_SYSTEM_PROMPT, build_developer_prompt
from .cli import complete_text

GENERATED_DIR: Path = Path(__file__).parent.parent / "generated_tools"

# Source-level patterns rejected outright. The developer prompt forbids these,
# but we double-check at the gate.
_FORBIDDEN_PATTERNS: list[tuple[str, str]] = [
    ("os.system(", "os.system call"),
    ("eval(", "eval call"),
    ("exec(", "exec call"),
    ("__import__(", "__import__ call"),
    ("shell=True", "subprocess shell=True"),
]


def develop(spec: ToolSpec) -> DevelopmentResult:
    """Generate, validate, and write a tool from its spec."""
    code = _generate_code(spec)

    ok, msg = _safety_check(code, spec.name)
    if not ok:
        return DevelopmentResult(
            success=False,
            tool_name=spec.name,
            error=f"Safety gate rejected the generated code: {msg}",
            code_preview=code[:600],
            message="Code generation produced unsafe or invalid code; nothing was written.",
        )

    target = _write_tool(spec.name, code)

    return DevelopmentResult(
        success=True,
        tool_name=spec.name,
        file_path=str(target),
        code_preview=code[:600],
        message=(
            f"Tool written to {target.relative_to(GENERATED_DIR.parent)}. "
            f"Restart the MCP server to load it."
        ),
    )


def _generate_code(spec: ToolSpec) -> str:
    text = complete_text(
        system_prompt=DEVELOPER_SYSTEM_PROMPT,
        user_prompt=build_developer_prompt(spec),
    )

    # Defensive: strip markdown fences if the model added them despite instructions
    if "```python" in text:
        text = text.split("```python", 1)[1].split("```", 1)[0]
    elif "```" in text:
        text = text.split("```", 1)[1].split("```", 1)[0]

    return text.strip() + "\n"


def _safety_check(code: str, expected_name: str) -> tuple[bool, str]:
    # Must be syntactically valid Python
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, f"syntax error at line {e.lineno}: {e.msg}"

    # Must define the expected function at top level
    top_level_funcs = [n.name for n in tree.body if isinstance(n, ast.FunctionDef)]
    if expected_name not in top_level_funcs:
        return (
            False,
            f"function '{expected_name}' not found at top level. Got: {top_level_funcs}",
        )

    # Reject obvious dangerous patterns
    for needle, label in _FORBIDDEN_PATTERNS:
        if needle in code:
            return False, f"{label} is not allowed"

    return True, "OK"


def _write_tool(name: str, code: str) -> Path:
    GENERATED_DIR.mkdir(exist_ok=True)
    init_file = GENERATED_DIR / "__init__.py"
    if not init_file.exists():
        init_file.write_text("")
    target = GENERATED_DIR / f"{name}.py"
    target.write_text(code)
    return target
