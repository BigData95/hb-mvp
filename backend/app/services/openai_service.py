import json

from openai import OpenAI

from app.core.config import get_settings
from app.schemas.graph import ProcessGraphLLMResponse

settings = get_settings()

PROCESS_GRAPH_SCHEMA = {
    "name": "process_graph",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "title": {"type": "string"},
            "summary": {"type": "string"},
            "nodes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "id": {"type": "string"},
                        "title": {"type": "string"},
                        "description": {"type": ["string", "null"]},
                        "type": {
                            "type": "string",
                            "enum": ["person", "automation", "mixed", "decision", "unknown"],
                        },
                        "assignee_name": {"type": ["string", "null"]},
                    },
                    "required": ["id", "title", "description", "type", "assignee_name"],
                },
            },
            "edges": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "source": {"type": "string"},
                        "target": {"type": "string"},
                        "label": {"type": ["string", "null"]},
                    },
                    "required": ["source", "target", "label"],
                },
            },
        },
        "required": ["title", "summary", "nodes", "edges"],
    },
}

SYSTEM_PROMPT = """
You convert natural-language company processes into a process graph.
Return a concise process title, a one-paragraph summary, a nodes list, and an edges list.

Rules:
- Each node is a single meaningful step.
- Use the node type 'person' when a human is responsible.
- Use the node type 'automation' when software/system performs the step.
- Use 'mixed' when both are clearly involved.
- Use 'decision' for decision or branching steps.
- Use 'unknown' when responsibility is unclear.
- Preserve ordering with the edges.
- For linear processes, connect every step in order.
- For branching, add labels like 'yes'/'no' when useful.
- Keep node titles short.
- Do not invent implementation details not implied by the user's text.
""".strip()


class ProcessParsingError(RuntimeError):
    pass


class OpenAIProcessService:
    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise ProcessParsingError(
                "OPENAI_API_KEY is missing. Add it to your backend .env file before parsing processes."
            )
        self.client = OpenAI(api_key=settings.openai_api_key)

    def parse_process(self, process_text: str) -> ProcessGraphLLMResponse:
        response = self.client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": process_text},
            ],
            response_format={"type": "json_schema", "json_schema": PROCESS_GRAPH_SCHEMA},
            temperature=0.2,
        )

        message = response.choices[0].message
        if getattr(message, "refusal", None):
            raise ProcessParsingError(f"Model refused the request: {message.refusal}")

        if not message.content:
            raise ProcessParsingError("The model returned an empty response.")

        try:
            payload = json.loads(message.content)
            parsed = ProcessGraphLLMResponse.model_validate(payload)
        except Exception as exc:  # noqa: BLE001
            raise ProcessParsingError(f"Failed to parse model output into the graph schema: {exc}") from exc

        if not parsed.nodes:
            raise ProcessParsingError("The model returned zero nodes.")

        return parsed
