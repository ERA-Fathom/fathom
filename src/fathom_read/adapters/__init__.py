"""Adapters turn what a framework already records into the op stream the read consumes."""
from . import events, edits, openinference, langgraph, crewai, letta, dbos  # noqa: F401

FORMATS = {
    "events": events,
    "edits": edits,
    "openinference": openinference,
    "langgraph": langgraph,
    "crewai": crewai,
    "letta": letta,
    "dbos": dbos,
}


def detect(doc) -> str:
    """Guess the format of a loaded JSON document."""
    if isinstance(doc, dict):
        if "ops" in doc:
            return "events"
        if "spans" in doc or "resourceSpans" in doc:
            return "openinference"
        if "edits" in doc or "initial_files" in doc:
            return "edits"
        if "blocks" in doc or "passages" in doc:
            return "letta"
        if "steps" in doc and "workflow_id" in doc:
            return "dbos"
        if "events" in doc:
            return "crewai"
        if "snapshots" in doc or "history" in doc:
            return "langgraph"
    if isinstance(doc, list) and doc:
        first = doc[0]
        if isinstance(first, dict):
            if "op" in first and "key" in first:
                return "events"
            if "attributes" in first or "span_kind" in first:
                return "openinference"
            if "values" in first and ("next" in first or "config" in first or "metadata" in first or "step" in first):
                return "langgraph"
            if "type" in first and ("tool_name" in first or "task_name" in first or first.get("type", "").startswith(("tool_", "task_"))):
                return "crewai"
            if "step_name" in first:
                return "dbos"
            if "tool" in first and "args" in first:
                return "edits"
    raise ValueError("could not detect the trace format; pass --format")
