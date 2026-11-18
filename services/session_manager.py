
"""Session-only research history for GeneRescue AI."""

import uuid
from datetime import datetime, timezone

import streamlit as st


def create_research_session(
    tool_name: str,
    session_title: str,
    input_summary: str = "",
    result_summary: str = "",
    project_id: str | None = None,
    status: str = "completed",
) -> dict:
    """Add a research activity to the current browser session."""

    if not tool_name.strip() or not session_title.strip():
        raise ValueError("Tool name and title are required.")

    if status not in {"completed", "in_progress", "failed"}:
        raise ValueError("Invalid session status.")

    record = {
        "id": str(uuid.uuid4()),
        "tool_name": tool_name.strip(),
        "session_title": session_title.strip(),
        "input_summary": input_summary,
        "result_summary": result_summary,
        "project_id": project_id,
        "status": status,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    if "research_history" not in st.session_state:
        st.session_state["research_history"] = []

    st.session_state["research_history"].insert(0, record)

    return record


def list_research_sessions(
    user_id: str | None = None,
    limit: int = 50,
) -> list[dict]:
    """Return the current session's research history."""

    if not 1 <= limit <= 200:
        raise ValueError("Limit must be between 1 and 200.")

    return st.session_state.get("research_history", [])[:limit]


def get_research_session(session_id: str) -> dict | None:
    """Find a research session by its local ID."""

    for record in st.session_state.get("research_history", []):
        if record.get("id") == session_id:
            return record

    return None


def clear_research_history() -> None:
    """Clear research history from the current session."""

    st.session_state["research_history"] = []
