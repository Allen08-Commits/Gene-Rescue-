
import streamlit as st
from services.authentication import login_user

st.markdown(
    """
    <div style="text-align:center;padding:35px 0 20px;">
        <div style="font-size:45px;">🌱</div>
        <div class="brand-title" style="font-size:2.6rem;">
            GeneRescue AI
        </div>
        <p style="color:#718078;">Welcome back to your research workspace.</p>
    </div>
    """,
    unsafe_allow_html=True
)

left, center, right = st.columns([1, 1.3, 1])

with center:
    st.subheader("Sign in")

    with st.form("login_form"):
        email = st.text_input(
            "Email address",
            placeholder="Enter your registered email"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password"
        )

        submitted = st.form_submit_button(
            "Login",
            type="primary",
            use_container_width=True
        )

    if submitted:
        if not email.strip() or not password:
            st.error("Please enter your email address and password.")
        else:
            try:
                user = login_user(
                    email=email.strip().lower(),
                    password=password
                )

                if not user:
                    st.error("Your credentials could not be verified.")
                    st.info("New to GeneRescue AI? Create an account below.")
                else:
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.success("Login successful.")
                    st.switch_page("pages/home.py")

            except Exception:
                st.error(
                    "Unable to sign in. Check your credentials or try again later."
                )

    st.markdown("---")

    st.markdown(
        "<div style='text-align:center;color:#718078;'>"
        "Don't have an account?</div>",
        unsafe_allow_html=True
    )

    if st.button("Create an account", use_container_width=True):
        st.switch_page("pages/register.py")

    if st.button("Back to Welcome", use_container_width=True):
        st.switch_page("pages/welcome.py")
