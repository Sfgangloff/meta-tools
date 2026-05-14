from __future__ import annotations
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field


class ToolSpec(BaseModel):
    name: str = Field(description="snake_case tool name")
    one_liner: str = Field(description="One-sentence description of what the tool does")
    rationale: str = Field(description="Specific friction this removes and why it recurred")
    input_schema: dict[str, Any] = Field(description="JSON Schema object for tool inputs")
    output_description: str = Field(description="What the tool returns")
    implementation_approach: str = Field(description="How the tool would be implemented internally")
    effort_estimate: Literal["low", "medium", "high"]


class AnalysisInput(BaseModel):
    goals: str
    trajectory: str
    available_tools: list[str] = Field(default_factory=list)


class AnalysisOutput(BaseModel):
    tool_needed: bool
    reason: Optional[str] = None        # populated when tool_needed is False
    confidence: Optional[float] = None  # populated when tool_needed is True
    spec: Optional[ToolSpec] = None     # populated when tool_needed is True


class ToolSuggestion(BaseModel):
    name: str = Field(description="snake_case tool name")
    one_liner: str = Field(description="One-sentence description of what the tool does")
    rationale: str = Field(description="Why this tool would help — what friction or gap it addresses")
    input_schema: dict[str, Any] = Field(description="JSON Schema object for tool inputs")
    output_description: str = Field(description="What the tool returns")
    implementation_approach: str = Field(description="How the tool would be implemented internally")
    effort_estimate: Literal["low", "medium", "high"]
    priority: Literal["high", "medium", "low"] = Field(
        description="How strongly this tool is suggested — high = clear win, low = speculative"
    )
    would_use_now: bool = Field(
        description="Whether this tool, if it existed, would plausibly be called as the next action"
    )


class SuggestionsInput(BaseModel):
    goals: str
    trajectory: str
    available_tools: list[str] = Field(default_factory=list)


class SuggestionsOutput(BaseModel):
    suggestions: list[ToolSuggestion] = Field(default_factory=list)
    notes: Optional[str] = None


class DevelopmentResult(BaseModel):
    success: bool
    tool_name: str
    file_path: Optional[str] = None
    error: Optional[str] = None
    code_preview: Optional[str] = None
    registered: bool = False
    register_error: Optional[str] = None
    message: str
