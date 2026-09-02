"""The op stream: what an adapter produces and the hosted read consumes."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple

Ref = Tuple[str, str]


@dataclass
class Op:
    """One action the agent took.

    op:     "set" writes a value to (kind, key); "remove" deletes it; "rename" moves (kind, key)
            to (kind, to); "add" inserts an entity into a collection under (kind, key); "answer"
            is an assertion the agent made (a final answer, a report); "commit" marks a terminal
            action (an order placed, a booking confirmed).
    kind:   what sort of thing the key names: "file", "record", "block", "fact", "order", or your own.
    key:    the name of the thing.
    value:  the content written (for set/add/answer).
    to:     the new name (for rename).
    ok:     whether the tool accepted the action. False makes the op a no-op.
    refs:   facts this op depends on, as (kind, key) pairs.
    step:   the position of the op in the stream (set by the reader if omitted).
    source: where the op came from (an adapter's note).
    """
    op: str
    kind: str
    key: str
    value: Optional[str] = None
    to: Optional[str] = None
    ok: bool = True
    refs: List[Ref] = field(default_factory=list)
    step: Optional[int] = None
    source: Optional[str] = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Op":
        refs = [tuple(r) for r in d.get("refs", [])]
        return cls(op=d["op"], kind=d.get("kind", "fact"), key=str(d["key"]),
                   value=None if d.get("value") is None else str(d.get("value")),
                   to=d.get("to"), ok=bool(d.get("ok", True)), refs=refs,
                   step=d.get("step"), source=d.get("source"))

    def as_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["refs"] = [list(r) for r in self.refs]
        return d


@dataclass
class Finding:
    kind: str
    step: Optional[int]
    key: str
    detail: str
    cites: Optional[int] = None

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Verdict:
    coherent: bool
    findings: List[Finding]
    ops_read: int
    ops_rejected: int
    live_facts: int

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Verdict":
        return cls(coherent=bool(d["coherent"]), findings=[Finding(**f) for f in d.get("findings", [])],
                   ops_read=int(d.get("ops_read", 0)), ops_rejected=int(d.get("ops_rejected", 0)),
                   live_facts=int(d.get("live_facts", 0)))

    def as_dict(self) -> Dict[str, Any]:
        return {"coherent": self.coherent, "findings": [f.as_dict() for f in self.findings],
                "ops_read": self.ops_read, "ops_rejected": self.ops_rejected, "live_facts": self.live_facts}
