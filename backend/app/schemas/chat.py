from datetime import datetime

from pydantic import BaseModel

from app.schemas.graph import ProcessGraphResponse


class CreateSessionRequest(BaseModel):
    title: str | None = None


class ChatMessageRequest(BaseModel):
    content: str
    persist_process: bool = True


class ChatMessageResponse(BaseModel):
    user_message_id: str
    assistant_message_id: str
    assistant_text: str
    graph: ProcessGraphResponse


class ChatMessageRead(BaseModel):
    id: str
    role: str
    content: str
    process_id: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatSessionRead(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime | None = None
    messages: list[ChatMessageRead]

    model_config = {"from_attributes": True}
