from __future__ import annotations

from .schemas import SuggestionsInput, SuggestionsOutput, ToolSuggestion
from .prompt_templates import SUGGESTER_SYSTEM_PROMPT, build_suggester_user_prompt
from .cli import complete_json

_SUGGESTION_ITEM_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "one_liner": {"type": "string"},
        "rationale": {"type": "string"},
        "input_schema": {"type": "object"},
        "output_description": {"type": "string"},
        "implementation_approach": {"type": "string"},
        "effort_estimate": {"type": "string", "enum": ["low", "medium", "high"]},
        "priority": {"type": "string", "enum": ["high", "medium", "low"]},
        "would_use_now": {"type": "boolean"},
    },
    "required": [
        "name", "one_liner", "rationale", "input_schema",
        "output_description", "implementation_approach", "effort_estimate",
        "priority", "would_use_now",
    ],
}

_SUGGESTIONS_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "suggestions": {
            "type": "array",
            "items": _SUGGESTION_ITEM_SCHEMA,
            "maxItems": 3,
            "description": "Ranked suggestions, highest-priority first. May be empty.",
        },
        "notes": {
            "type": "string",
            "description": "Optional commentary — required when suggestions is empty",
        },
    },
    "required": ["suggestions"],
}


def suggest(input_data: SuggestionsInput) -> SuggestionsOutput:
    data = complete_json(
        system_prompt=SUGGESTER_SYSTEM_PROMPT,
        user_prompt=build_suggester_user_prompt(input_data),
        json_schema=_SUGGESTIONS_SCHEMA,
    )
    suggestions = [ToolSuggestion(**s) for s in data.get("suggestions", [])]
    return SuggestionsOutput(suggestions=suggestions, notes=data.get("notes"))
