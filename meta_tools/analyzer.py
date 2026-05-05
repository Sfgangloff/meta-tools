from __future__ import annotations
import anthropic
from .schemas import AnalysisInput, AnalysisOutput
from .config import ANTHROPIC_API_KEY, ANALYZER_MODEL, CONFIDENCE_THRESHOLD, MAX_TOKENS
from .prompt_templates import SYSTEM_PROMPT, build_user_prompt

_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Forced-output schema: Claude must call this tool, giving us structured data directly.
_REPORT_TOOL: dict = {
    "name": "report_analysis",
    "description": "Report the trajectory gap analysis result",
    "input_schema": {
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
                    "effort_estimate": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                    },
                },
                "required": [
                    "name", "one_liner", "rationale", "input_schema",
                    "output_description", "implementation_approach", "effort_estimate",
                ],
            },
        },
        "required": ["tool_needed"],
    },
}


def analyze(input_data: AnalysisInput) -> AnalysisOutput:
    response = _client.messages.create(
        model=ANALYZER_MODEL,
        max_tokens=MAX_TOKENS,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        tools=[_REPORT_TOOL],
        tool_choice={"type": "tool", "name": "report_analysis"},
        messages=[
            {"role": "user", "content": build_user_prompt(input_data)}
        ],
    )

    tool_use = next(b for b in response.content if b.type == "tool_use")
    data: dict = tool_use.input

    # Enforce confidence threshold: downgrade low-confidence positives to false
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
