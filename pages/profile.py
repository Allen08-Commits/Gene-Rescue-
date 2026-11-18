
import streamlit as st

from services.authentication import (
    get_user_sessions,
    get_user_settings,
    update_user_settings,
    logout_user
)

if not st.session_state.get("authenticated"):
    st.warning("Please log in to view your profile.")
    st.switch_page("pages/login.py")
    st.stop()

user = st.session_state.get("user") or {}

user_id = user.get("id")
username = user.get("username", "Researcher")
email = user.get("email", "")

# Header
left, right = st.columns([4, 1])

with left:
    st.title("My Profile")
    st.caption("Manage your account and research activity.")

with right:
    if st.button("← Home", use_container_width=True):
        st.switch_page("pages/home.py")

st.divider()

# Account information
st.subheader("Account Information")

with st.container(border=True):
    st.markdown("### 👤 Personal Details")

    st.write("**Username:**", username)
    st.write("**Email:**", email)

st.divider()

# Session history
st.subheader("Research Session History")

try:
    sessions = get_user_sessions(user_id) if user_id else []

    if sessions:
        for session in sessions:
            with st.container(border=True):
                st.markdown(
                    f"**{session.get('tool_name', 'Research activity')}**"
                )

                st.caption(
                    f"Date: {session.get('created_at', 'Not available')}"
                )

                if session.get("project_name"):
                    st.write(
                        f"Project: {session['project_name']}"
                    )

                if session.get("status"):
                    st.write(
                        f"Status: {session['status']}"
                    )
    else:
        st.info(
            "No research sessions have been recorded yet. "
            "Your activity will appear here as you use the tools."
        )

except Exception:
    st.warning("Session history is temporarily unavailable.")

st.divider()

# Account settings
st.subheader("Settings")

try:
    settings = get_user_settings(user_id) if user_id else {}
    settings = settings or {}

    notifications = st.checkbox(
        "Enable research activity notifications",
        value=bool(settings.get("notifications", True))
    )

    save_settings = st.button(
        "Save Settings",
        type="primary"
    )

    if save_settings:
        update_user_settings(
            user_id,
            {"notifications": notifications}
        )
        st.success("Your settings have been saved.")

except Exception:
    st.warning("Account settings are temporarily unavailable.")

st.divider()

# Logout
st.subheader("Account Actions")

if st.button("Logout", type="secondary", use_container_width=True):
    try:
        logout_user()
    finally:
        for key in list(st.session_state.keys()):
            del st.session_state[key]

        st.switch_page("pages/welcome.py")
