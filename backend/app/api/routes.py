from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models.chat import ChatSession
from app.models.process import Process
from app.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatSessionRead,
    CreateSessionRequest,
)
from app.schemas.graph import ProcessGraphResponse
from app.services.openai_service import OpenAIProcessService, ProcessParsingError
from app.services.process_service import ProcessService

router = APIRouter()


@router.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/chat/sessions", response_model=ChatSessionRead, status_code=status.HTTP_201_CREATED)
def create_session(payload: CreateSessionRequest, db: Session = Depends(get_db)) -> ChatSession:
    session = ChatSession(title=payload.title or "New process chat")
    db.add(session)
    db.commit()
    db.refresh(session)
    return session




@router.get("/chat/sessions/{session_id}", response_model=ChatSessionRead)
def get_session(session_id: str, db: Session = Depends(get_db)) -> ChatSession:
    session = (
        db.query(ChatSession)
        .options(joinedload(ChatSession.messages))
        .filter(ChatSession.id == session_id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.post("/chat/sessions/{session_id}/messages", response_model=ChatMessageResponse)
def send_message(
    session_id: str,
    payload: ChatMessageRequest,
    db: Session = Depends(get_db),
) -> ChatMessageResponse:
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        llm_graph = OpenAIProcessService().parse_process(payload.content)
    except ProcessParsingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    process = None
    if payload.persist_process:
        process = ProcessService.persist_graph(
            db,
            session=session,
            original_text=payload.content,
            graph=llm_graph,
        )

    assistant_text = ProcessService.build_assistant_text(llm_graph)
    user_message, assistant_message = ProcessService.attach_messages(
        db,
        session=session,
        user_content=payload.content,
        assistant_content=assistant_text,
        process=process,
    )
    db.commit()

    if process:
        db.refresh(process)
        graph_response = ProcessService.to_graph_response(process)
    else:
        graph_response = ProcessGraphResponse(
            process_id="temporary",
            title=llm_graph.title,
            summary=llm_graph.summary,
            nodes=[node.model_dump() for node in llm_graph.nodes],
            edges=[edge.model_dump() for edge in llm_graph.edges],
        )

    return ChatMessageResponse(
        user_message_id=user_message.id,
        assistant_message_id=assistant_message.id,
        assistant_text=assistant_text,
        graph=graph_response,
    )


#@router.post("/processes/parse", response_model=ProcessGraphResponse)
# Parses a process and persists it directly, without going through chat session messaging.


#@router.get("/processes", response_model=list[ProcessGraphResponse])
# Returns all saved process


#@router.get("/processes/{process_id}", response_model=ProcessGraphResponse)
# Returns one saved process graph id


#PATCH /processes/{process_id}  ui
