from enum import Enum


class NodeType(str, Enum):
    PERSON = "person"
    AUTOMATION = "automation"
    MIXED = "mixed"
    DECISION = "decision"
    UNKNOWN = "unknown"
