"""
Quick smoke test: run the analyzer directly (no MCP server needed).
Usage: python examples/smoke_test.py [positive|negative]
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from meta_tools.analyzer import analyze
from meta_tools.schemas import AnalysisInput

FIXTURES = Path(__file__).parent.parent / "tests" / "fixtures"

cases = {
    "positive": FIXTURES / "positive_fastapi_routes.json",
    "negative": FIXTURES / "negative_routine_bash.json",
    "negative2": FIXTURES / "negative_one_off.json",
}

target = sys.argv[1] if len(sys.argv) > 1 else "positive"
fixture = cases.get(target, cases["positive"])

data = json.loads(fixture.read_text())
print(f"Running fixture: {data['description']}\n")

result = analyze(AnalysisInput(**data["input"]))
print(json.dumps(result.model_dump(), indent=2))
print(f"\nExpected tool_needed: {data['expected_tool_needed']}")
print(f"Got     tool_needed: {result.tool_needed}")
print("PASS" if result.tool_needed == data["expected_tool_needed"] else "FAIL")
