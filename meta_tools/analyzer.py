from __future__ import annotations

from .schemas import AnalysisInput, AnalysisOutput
from .config import CONFIDENCE_THRESHOLD
from .prompt_templates import SYSTEM_PROMPT, build_user_prompt
from .cli import complete_json

_REPORT_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "tool_needed": {
            "type": "boolean",
            "description": "Whether a new tool is needed",
        },
        "reason": {
            "type": "string",
            "description": "When tool_needed is false: why existing tools suffice",
        },
        "confidence": {
            "type": "number",
            "description": "When tool_needed is true: confidence score 0.0–1.0",
        },
        "spec": {
            "type": "object",
            "description": "When tool_needed is true: the tool specification",
            "properties": {
                "name": {"type": "string"},
                "one_liner": {"type": "string"},
                "rationale": {"type": "string"},
                "input_schema": {"type": "object"},
                "output_description": {"type": "string"},
                "implementation_approach": {"type": "string"},
                "effort_estimate": {"type": "string", "enum": ["low", "medium", "high"]},
            },
            "required": [
                "name", "one_liner", "rationale", "input_schema",
                "output_description", "implementation_approach", "effort_estimate",
            ],
        },
    },
    "required": ["tool_needed"],
}


def analyze(input_data: AnalysisInput) -> AnalysisOutput:
    data = complete_json(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=build_user_prompt(input_data),
        json_schema=_REPORT_SCHEMA,
    )

    if data.get("tool_needed") and (data.get("confidence") or 0.0) < CONFIDENCE_THRESHOLD:
        raw_name = (data.get("spec") or {}).get("name", "unnamed")
        return AnalysisOutput(
            tool_needed=False,
            reason=(
                f"Candidate tool '{raw_name}' had confidence "
                f"{data.get('confidence', 0.0):.2f}, below threshold {CONFIDENCE_THRESHOLD:.2f}."
            ),
        )

    return AnalysisOutput(**data)
