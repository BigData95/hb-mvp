from sqlalchemy.orm import Session

from app.models.chat import ChatMessage, ChatSession
from app.models.enums import NodeType
from app.models.process import Process, ProcessEdge, ProcessNode
from app.schemas.graph import ProcessGraphLLMResponse, ProcessGraphResponse


class ProcessService:
    @staticmethod
    def persist_graph(
        db: Session,
        *,
        session: ChatSession | None,
        original_text: str,
        graph: ProcessGraphLLMResponse,
    ) -> Process:
        process = Process(
            session_id=session.id if session else None,
            title=graph.title,
            original_text=original_text,
            summary=graph.summary,
        )
        db.add(process)
        db.flush()

        node_id_map: dict[str, ProcessNode] = {}
        for idx, node in enumerate(graph.nodes):
            db_node = ProcessNode(
                process_id=process.id,
                node_key=node.id,
                title=node.title,
                description=node.description,
                node_type=NodeType(node.type),
                assignee_name=node.assignee_name,
                position_index=idx,
            )
            db.add(db_node)
            db.flush()
            node_id_map[node.id] = db_node

        for idx, edge in enumerate(graph.edges):
            source_node = node_id_map.get(edge.source)
            target_node = node_id_map.get(edge.target)
            if not source_node or not target_node:
                continue
            db.add(
                ProcessEdge(
                    process_id=process.id,
                    source_node_id=source_node.id,
                    target_node_id=target_node.id,
                    label=edge.label,
                    position_index=idx,
                )
            )

        db.flush()
        return process

    @staticmethod
    def to_graph_response(process: Process) -> ProcessGraphResponse:
        nodes = [
            {
                "id": node.id,
                "node_key": node.node_key,
                "title": node.title,
                "description": node.description,
                "type": node.node_type.value,
                "assignee_name": node.assignee_name,
                "position_index": node.position_index,
            }
            for node in process.nodes
        ]
        edges = [
            {
                "id": edge.id,
                "source": edge.source_node_id,
                "target": edge.target_node_id,
                "label": edge.label,
                "position_index": edge.position_index,
            }
            for edge in process.edges
        ]

        return ProcessGraphResponse(
            process_id=process.id,
            title=process.title,
            summary=process.summary,
            nodes=nodes,
            edges=edges,
        )

    @staticmethod
    def build_assistant_text(graph: ProcessGraphLLMResponse) -> str:
        people_steps = sum(1 for node in graph.nodes if node.type == "person")
        automation_steps = sum(1 for node in graph.nodes if node.type == "automation")
        return (
            f"I mapped this into {len(graph.nodes)} steps and {len(graph.edges)} transitions. "
            f"There are {people_steps} people-owned steps and {automation_steps} automation-owned steps."
        )

    @staticmethod
    def attach_messages(
        db: Session,
        *,
        session: ChatSession,
        user_content: str,
        assistant_content: str,
        process: Process | None,
    ) -> tuple[ChatMessage, ChatMessage]:
        user_message = ChatMessage(session_id=session.id, role="user", content=user_content)
        assistant_message = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=assistant_content,
            process_id=process.id if process else None,
        )
        db.add_all([user_message, assistant_message])
        db.flush()
        return user_message, assistant_message
