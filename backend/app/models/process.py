import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import NodeType



class Process(Base):
    __tablename__ = "processes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str | None] = mapped_column(ForeignKey("chat_sessions.id", ondelete="SET NULL"), nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    original_text: Mapped[str] = mapped_column(Text())
    summary: Mapped[str] = mapped_column(Text())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    nodes: Mapped[list["ProcessNode"]] = relationship(
        back_populates="process", cascade="all, delete-orphan", order_by="ProcessNode.position_index"
    )
    edges: Mapped[list["ProcessEdge"]] = relationship(
        back_populates="process", cascade="all, delete-orphan", order_by="ProcessEdge.position_index"
    )
    assistant_messages: Mapped[list["ChatMessage"]] = relationship(back_populates="process")


class ProcessNode(Base):
    __tablename__ = "process_nodes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    process_id: Mapped[str] = mapped_column(ForeignKey("processes.id", ondelete="CASCADE"), index=True)
    node_key: Mapped[str] = mapped_column(String(128), index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    node_type: Mapped[NodeType] = mapped_column(Enum(NodeType, native_enum=False), default=NodeType.UNKNOWN)
    assignee_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    position_index: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    process: Mapped["Process"] = relationship(back_populates="nodes")
    outgoing_edges: Mapped[list["ProcessEdge"]] = relationship(
        back_populates="source_node", foreign_keys="ProcessEdge.source_node_id"
    )
    incoming_edges: Mapped[list["ProcessEdge"]] = relationship(
        back_populates="target_node", foreign_keys="ProcessEdge.target_node_id"
    )


class ProcessEdge(Base):
    __tablename__ = "process_edges"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    process_id: Mapped[str] = mapped_column(ForeignKey("processes.id", ondelete="CASCADE"), index=True)
    source_node_id: Mapped[str] = mapped_column(ForeignKey("process_nodes.id", ondelete="CASCADE"))
    target_node_id: Mapped[str] = mapped_column(ForeignKey("process_nodes.id", ondelete="CASCADE"))
    label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    position_index: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    process: Mapped["Process"] = relationship(back_populates="edges")
    source_node: Mapped[ProcessNode] = relationship(
        back_populates="outgoing_edges", foreign_keys=[source_node_id]
    )
    target_node: Mapped[ProcessNode] = relationship(
        back_populates="incoming_edges", foreign_keys=[target_node_id]
    )



