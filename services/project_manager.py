
"""Temporary research project management using Streamlit session state."""
import streamlit as st
from uuid import uuid4
from datetime import datetime, timezone


def _projects():
    if "research_projects" not in st.session_state:
        st.session_state["research_projects"] = []
    return st.session_state["research_projects"]


def create_project(project_name, description="", organism="", crop=""):
    name = str(project_name).strip()

    if not name:
        raise ValueError("Enter a project name.")

    project = {
        "project_id": str(uuid4()),
        "project_name": name,
        "description": str(description),
        "organism": str(organism),
        "crop": str(crop),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    _projects().insert(0, project)
    return project


def list_projects():
    return _projects()


def get_project(project_id):
    return next(
        (p for p in _projects() if p["project_id"] == project_id),
        None,
    )


def update_project(project_id, updates):
    allowed = {"project_name", "description", "organism", "crop"}

    for project in _projects():
        if project["project_id"] == project_id:
            for key, value in updates.items():
                if key in allowed:
                    project[key] = str(value)

            project["updated_at"] = datetime.now(timezone.utc).isoformat()
            return project

    return None


def delete_project(project_id):
    projects = _projects()
    before = len(projects)

    st.session_state["research_projects"] = [
        p for p in projects if p["project_id"] != project_id
    ]

    return len(st.session_state["research_projects"]) < before
