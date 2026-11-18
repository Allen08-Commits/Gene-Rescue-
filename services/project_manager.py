
"""Temporary research project management."""

from datetime import datetime, timezone
from uuid import uuid4

import streamlit as st


def _projects():
    if "research_projects" not in st.session_state:
        st.session_state["research_projects"] = []

    return st.session_state["research_projects"]


def create_project(
    project_name,
    description="",
    organism="",
    crop="",
):
    """Create a research project."""

    name = str(project_name).strip()

    if not name:
        raise ValueError("Project name cannot be empty.")

    now = datetime.now(timezone.utc).isoformat()

    project = {
        "project_id": str(uuid4()),
        "project_name": name,
        "description": str(description),
        "organism": str(organism),
        "crop": str(crop),
        "created_at": now,
        "updated_at": now,
    }

    _projects().insert(0, project)

    return project


def list_projects():
    return _projects()


def get_project(project_id):
    return next(
        (
            project for project in _projects()
            if project["project_id"] == project_id
        ),
        None,
    )


def update_project(project_id, updates):
    """Update permitted project fields."""

    allowed = {
        "project_name",
        "description",
        "organism",
        "crop",
    }

    for project in _projects():
        if project["project_id"] == project_id:

            for key, value in updates.items():
                if key in allowed:
                    project[key] = str(value)

            project["updated_at"] = (
                datetime.now(timezone.utc).isoformat()
            )

            return project

    return None


def delete_project(project_id):
    """Delete a project from the current session."""

    projects = _projects()
    original_length = len(projects)

    st.session_state["research_projects"] = [
        project for project in projects
        if project["project_id"] != project_id
    ]

    return len(st.session_state["research_projects"]) < original_length
