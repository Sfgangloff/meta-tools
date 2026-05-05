"""
End-to-end smoke test for develop_tool: generates code, applies safety gate,
writes to disk, AND registers live with the running FastMCP server.

Usage: python examples/develop_smoke_test.py
"""
import sys
import json
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from meta_tools.server import mcp, develop_tool
from meta_tools.schemas import ToolSpec

FIXTURE = Path(__file__).parent.parent / "tests" / "fixtures" / "sample_spec.json"

data = json.loads(FIXTURE.read_text())
print(f"Fixture: {data['description']}\n")

spec = ToolSpec(**data["spec"])

# Call the develop_tool function directly (same path the MCP endpoint takes)
result_dict = develop_tool.fn(spec) if hasattr(develop_tool, "fn") else develop_tool(spec)

print(json.dumps(result_dict, indent=2))
print()

if not result_dict.get("success"):
    print("FAIL —", result_dict.get("error"))
    sys.exit(1)

print(f"Generated file: {result_dict['file_path']}")
print(f"Live registered: {result_dict['registered']}")
print()
print("First 600 chars of generated code:")
print("-" * 60)
print(result_dict["code_preview"])
print("-" * 60)

# Verify the new tool actually appears in the server's tool list
tools = asyncio.run(mcp.list_tools())
names = [t.name for t in tools]
print(f"\nMCP server tool list now: {names}")
expected = result_dict["tool_name"]
if expected in names:
    print(f"\nPASS — '{expected}' is live in the MCP server.")
else:
    print(f"\nFAIL — '{expected}' was not registered.")
    sys.exit(1)
