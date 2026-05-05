from __future__ import annotations
import importlib.util
import sys
from pathlib import Path

from fastmcp import FastMCP

from .analyzer import analyze
from .developer import develop, GENERATED_DIR
from .schemas import AnalysisInput, ToolSpec

mcp = FastMCP(
    name="meta-tools",
    instructions=(
        "Two meta-tools for self-extension. "
        "Call analyze_trajectory when you notice you are repeating the same multi-step "
        "workaround 3 or more times — it returns 'no tool needed' in most cases, and a "
        "spec only when confidence is high. "
        "If a spec is returned, review it, then call develop_tool with the spec to "
        "generate the implementation. The new tool is written to disk and becomes "
        "available on the next MCP server restart."
    ),
)


@mcp.tool()
def analyze_trajectory(
    goals: str,
    trajectory: str,
    available_tools: list[str] | None = None,
) -> dict:
    """
    Analyze a reasoning trajectory to detect if a missing tool would significantly help.
    Returns tool_needed: false in most cases. Only returns a spec when confidence >= 0.85.
    """
    result = analyze(
        AnalysisInput(
            goals=goals,
            trajectory=trajectory,
            available_tools=available_tools or [],
        )
    )
    return result.model_dump()


@mcp.tool()
def develop_tool(spec: ToolSpec) -> dict:
    """
    Generate Python source code for a tool with the given spec, run a safety gate,
    write it to generated_tools/, and register it live with the MCP server. The
    new tool becomes available immediately — Claude Code receives a tools/list_changed
    notification and re-fetches the tool list. Use the spec object returned by
    analyze_trajectory.
    """
    result = develop(spec)

    if result.success and result.file_path:
        try:
            _register_tool_from_file(Path(result.file_path), result.tool_name)
            result.registered = True
            result.message = (
                f"Tool '{result.tool_name}' is now live. Claude Code will pick it up "
                f"automatically via tools/list_changed."
            )
        except Exception as e:
            result.registered = False
            result.register_error = str(e)
            result.message = (
                f"Tool written to {result.file_path} but live registration failed: {e}. "
                f"Restart the MCP server to load it."
            )

    return result.model_dump()


def _register_tool_from_file(file_path: Path, name: str) -> None:
    """
    Import (or re-import) a generated tool file and register its top-level function
    with FastMCP. Idempotent: if a tool with the same name is already registered,
    it is removed first so the latest implementation wins.
    """
    module_name = f"generated_tools.{name}"

    # Drop any previous registration so re-development replaces cleanly
    try:
        mcp.local_provider.remove_tool(name)
    except Exception:
        pass  # not previously registered — fine

    # Force a fresh module import so re-developed code is actually re-read
    if module_name in sys.modules:
        del sys.modules[module_name]

    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    fn = getattr(module, name, None)
    if fn is None or not callable(fn):
        raise RuntimeError(
            f"file {file_path.name} does not define a callable '{name}' at module level"
        )

    mcp.tool()(fn)


def _load_generated_tools() -> int:
    """Load every Python file in generated_tools/ as a tool. Called once at startup."""
    if not GENERATED_DIR.exists():
        return 0

    count = 0
    for py_file in sorted(GENERATED_DIR.glob("*.py")):
        if py_file.name.startswith("_"):
            continue
        try:
            _register_tool_from_file(py_file, py_file.stem)
            count += 1
        except Exception as e:
            print(f"[meta-tools] failed to load {py_file.name}: {e}", file=sys.stderr)

    if count:
        print(f"[meta-tools] loaded {count} generated tool(s)", file=sys.stderr)
    return count


_load_generated_tools()


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
