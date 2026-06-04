import streamlit as st
from db.users import register, login


def init_auth_state() -> None:

    st.session_state.setdefault("logged_in", False)
    st.session_state.setdefault("user_id", None)
    st.session_state.setdefault("user_name", None)
    st.session_state.setdefault("user_email", None)


def set_session(user: dict) -> None:

    st.session_state.logged_in = True
    st.session_state.user_id = user["_id"]
    st.session_state.user_name = user["name"]
    st.session_state.user_email = user["email"]


def clear_session() -> None:

    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_name = None
    st.session_state.user_email = None
    st.session_state.pop("current_roadmap_id", None)
    st.session_state.pop("current_roadmap", None)
    st.session_state.pop("current_page", None)


def is_logged_in() -> bool:

    return bool(st.session_state.get("logged_in", False))


def render_auth() -> None:

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("## 🗺️ SkillMap AI")
        st.markdown(
            "Generate a complete, personalised learning roadmap "
            "for any skill — with videos, courses, projects, and quizzes."
        )
        st.divider()

        login_tab, register_tab = st.tabs(["🔐 Login", "✨ Create Account"])

        with login_tab:
            _render_login_form()

        with register_tab:
            _render_register_form()


def _render_login_form() -> None:

    with st.form("login_form", clear_on_submit=False):
        st.subheader("Welcome back")

        email = st.text_input(
            "Email",
            placeholder="you@example.com",
            key="login_email",
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Your password",
            key="login_password",
        )

        submitted = st.form_submit_button(
            "Login",
            use_container_width=True,
            type="primary",
        )

    if submitted:

        if not email or not password:
            st.error("Please enter both email and password.")
            return

        with st.spinner("Logging in..."):
            user = login(email.strip().lower(), password)

        if user is None:

            st.error("Incorrect email or password. Please try again.")
        else:
            set_session(user)
            st.success(f"Welcome back, {user['name']}!")
            st.rerun()


def _render_register_form() -> None:

    with st.form("register_form", clear_on_submit=False):
        st.subheader("Create your account")

        name = st.text_input(
            "Full name",
            placeholder="Alice Smith",
            key="reg_name",
        )
        email = st.text_input(
            "Email",
            placeholder="you@example.com",
            key="reg_email",
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="At least 6 characters",
            key="reg_password",
        )
        confirm = st.text_input(
            "Confirm password",
            type="password",
            placeholder="Repeat your password",
            key="reg_confirm",
        )

        submitted = st.form_submit_button(
            "Create Account",
            use_container_width=True,
            type="primary",
        )

    if submitted:

        error = _validate_register_inputs(name, email, password, confirm)
        if error:
            st.error(error)
            return

        with st.spinner("Creating your account..."):
            result = register(name.strip(), email.strip().lower(), password)

        if isinstance(result, str):
            st.error(result)
        else:

            set_session(result)
            st.success(f"Account created! Welcome, {result['name']}!")
            st.rerun()


def _validate_register_inputs(
    name: str,
    email: str,
    password: str,
    confirm: str,
) -> str | None:

    if not name.strip():
        return "Please enter your name."
    if not email.strip() or "@" not in email:
        return "Please enter a valid email address."
    if len(password) < 6:
        return "Password must be at least 6 characters."
    if password != confirm:
        return "Passwords do not match."
    return None
