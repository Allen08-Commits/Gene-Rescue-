
import streamlit as st
from services.authentication import register_user

st.markdown(
    """
    <div style="text-align:center;padding:30px 0 15px;">
        <div style="font-size:42px;">🌱</div>
        <h1>Create your GeneRescue AI account</h1>
        <p style="color:#718078;">
            Set up your personal bioinformatics research workspace.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

left, center, right = st.columns([1, 1.4, 1])

with center:
    with st.form("registration_form"):
        username = st.text_input(
            "Username",
            placeholder="Choose a username"
        )

        email = st.text_input(
            "Email address",
            placeholder="Enter your email"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Create a password"
        )

        confirm_password = st.text_input(
            "Confirm password",
            type="password",
            placeholder="Re-enter your password"
        )

        agree = st.checkbox(
            "I understand that computational findings require scientific validation."
        )

        submitted = st.form_submit_button(
            "Create Account",
            type="primary",
            use_container_width=True
        )

    if submitted:
        if not username.strip() or not email.strip():
            st.error("Username and email are required.")

        elif len(username.strip()) < 3:
            st.error("Username must contain at least 3 characters.")

        elif "@" not in email or "." not in email.split("@")[-1]:
            st.error("Enter a valid email address.")

        elif len(password) < 10:
            st.error("Password must contain at least 10 characters.")

        elif password != confirm_password:
            st.error("Passwords do not match.")

        elif not agree:
            st.error("Please acknowledge the scientific validation notice.")

        else:
            try:
                user = register_user(
                    username=username.strip(),
                    email=email.strip().lower(),
                    password=password
                )

                if user:
                    st.session_state.authenticated = True
                    st.session_state.user = user

                    st.success("Your account has been created.")
                    st.switch_page("pages/home.py")
                else:
                    st.success(
                        "Registration submitted. Please sign in after "
                        "completing any required email verification."
                    )
                    st.switch_page("pages/login.py")

            except ValueError as error:
                st.error(str(error))

            except Exception:
                st.error(
                    "Account creation could not be completed. "
                    "Please check your details and try again."
                )

    if st.button("Already have an account? Login", use_container_width=True):
        st.switch_page("pages/login.py")
