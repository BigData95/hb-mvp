from typing import Literal

from pydantic import BaseModel, Field


class GraphNodeCreate(BaseModel):
    id: str = Field(description="A unique stable identifier for the step, like step_1")
    title: str = Field(description="A short title for the step")
    description: str | None = Field(default=None, description="Optional longer description")
    type: Literal["person", "automation", "mixed", "decision", "unknown"] = "unknown"
    assignee_name: str | None = Field(
        default=None,
        description="The person, role, or automation name responsible for the step",
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {"additionalProperties": False},
    }


class GraphEdgeCreate(BaseModel):
    source: str
    target: str
    label: str | None = None

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {"additionalProperties": False},
    }


class ProcessGraphLLMResponse(BaseModel):
    title: str
    summary: str
    nodes: list[GraphNodeCreate]
    edges: list[GraphEdgeCreate]

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {"additionalProperties": False},
    }


class ProcessGraphResponse(BaseModel):
    process_id: str
    title: str
    summary: str
    nodes: list[dict]
    edges: list[dict]
