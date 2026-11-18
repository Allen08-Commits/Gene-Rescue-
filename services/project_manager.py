
"""Session-only research project management."""

import uuid
from datetime import datetime, timezone

import streamlit as st


def create_project(
    project_name: str,
    description: str = "",
    organism: str = "",
    crop: str = "",
) -> dict:
    """Create a research project in the current session."""

    if not project_name or not project_name.strip():
        raise ValueError("Project name is required.")

    project = {
        "id": str(uuid.uuid4()),
        "project_name": project_name.strip(),
        "description": description.strip(),
        "organism": organism.strip(),
        "crop": crop.strip(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    if "research_projects" not in st.session_state:
        st.session_state["research_projects"] = []

    st.session_state["research_projects"].insert(0, project)

    return project


def list_projects() -> list[dict]:
    """List projects in the current session."""

    return st.session_state.get("research_projects", [])


def get_project(project_id: str) -> dict | None:
    """Retrieve a project by its local ID."""

    for project in list_projects():
        if project.get("id") == project_id:
            return project

    return None


def update_project(project_id: str, updates: dict) -> dict:
    """Update a project in the current session."""

    allowed = {
        "project_name",
        "description",
        "organism",
        "crop",
    }

    payload = {
        key: value
        for key, value in updates.items()
        if key in allowed
    }

    if not payload:
        raise ValueError("No valid project fields were supplied.")

    for project in st.session_state.get("research_projects", []):
        if project.get("id") == project_id:
            project.update(payload)
            return project

    raise ValueError("Project was not found.")


def delete_project(project_id: str) -> bool:
    """Delete a project from the current session."""

    projects = st.session_state.get("research_projects", [])
    remaining = [
        project for project in projects
        if project.get("id") != project_id
    ]

    deleted = len(remaining) != len(projects)
    st.session_state["research_projects"] = remaining

    return deleted
