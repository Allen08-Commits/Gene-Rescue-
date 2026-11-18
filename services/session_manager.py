
"""Session-based research activity management."""
from datetime import datetime, timezone
from uuid import uuid4
import streamlit as st


def _history():
    if "research_history" not in st.session_state:
        st.session_state["research_history"] = []
    return st.session_state["research_history"]


def create_research_session(
    tool_name,
    session_title,
    input_summary="",
    result_summary="",
    project_id=None,
    status="completed",
):
    record = {
        "session_id": str(uuid4()),
        "tool_name": str(tool_name),
        "session_title": str(session_title),
        "input_summary": str(input_summary),
        "result_summary": str(result_summary),
        "project_id": project_id,
        "status": str(status),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _history().insert(0, record)
    return record


def list_research_sessions(user_id=None, limit=50):
    # user_id is accepted for compatibility; this version has no accounts.
    return _history()[:max(0, int(limit))]


def get_research_session(session_id):
    return next(
        (item for item in _history()
         if item["session_id"] == session_id),
        None,
    )


def clear_research_history():
    st.session_state["research_history"] = []
