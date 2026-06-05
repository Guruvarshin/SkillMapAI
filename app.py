import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="SkillMap AI",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "SkillMap AI, Personalised learning roadmaps powered by Claude AI",
    },
)


def check_env_vars() -> None:
    required = {
        "ANTHROPIC_API_KEY": "https://console.anthropic.com/",
        "YOUTUBE_API_KEY": "https://console.cloud.google.com/ → YouTube Data API v3",
        "TAVILY_API_KEY": "https://tavily.com/",
        "MONGODB_URI": "https://cloud.mongodb.com/",
    }

    missing = [
        f"- `{key}`, get it at {url}"
        for key, url in required.items()
        if not os.environ.get(key) or os.environ.get(key, "").startswith("your_")
    ]

    if missing:
        st.error(
            "**⚠️ Missing API keys.** Add these to your `.env` file "
            "(local) or Streamlit Cloud Secrets (deployed):\n\n" + "\n".join(missing)
        )
        st.stop()


def init_session_state() -> None:
    defaults = {
        "logged_in": False,
        "user_id": None,
        "user_name": None,
        "user_email": None,
        "current_page": "dashboard",
        "current_roadmap_id": None,
        "current_roadmap": None,
        "generation_running": False,
        "current_subtopic_id": None,
        "current_subtopic_name": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def rehydrate_session() -> None:
    user_id = st.session_state.get("user_id")
    logged_in = st.session_state.get("logged_in", False)

    if user_id and not logged_in:
        from db.users import get_user_by_id

        user = get_user_by_id(user_id)
        if user:
            st.session_state.logged_in = True
            st.session_state.user_name = user["name"]
            st.session_state.user_email = user["email"]
        else:
            st.session_state.user_id = None


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("# 🗺️ SkillMap AI")
        st.caption("Your AI-powered learning companion")
        st.divider()

        if not st.session_state.get("logged_in"):
            st.info("Login or create an account to get started.")
            return

        user_name = st.session_state.get("user_name", "User")
        st.markdown(f"👤 **{user_name}**")
        st.divider()

        nav_items = [
            ("🏠 Dashboard", "dashboard"),
            ("✨ Generate Roadmap", "generate"),
        ]

        if st.session_state.get("current_roadmap_id"):
            nav_items += [
                ("📋 My Roadmap", "roadmap"),
                ("🚀 Projects", "projects"),
                ("❓ Quiz", "quiz"),
            ]

        for label, page in nav_items:
            is_active = st.session_state.get("current_page") == page
            if st.button(
                label,
                key=f"nav_{page}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                if page == "quiz" and not st.session_state.get("current_subtopic_id"):
                    st.session_state.current_subtopic_id = "final"
                    st.session_state.current_subtopic_name = "Final Quiz"
                st.session_state.current_page = page
                st.rerun()

        st.divider()

        current_roadmap = st.session_state.get("current_roadmap")
        if current_roadmap:
            skill = current_roadmap.get("skill", "")
            st.caption(f"📋 Current: **{skill}**")
            st.divider()

        if st.button("🚪 Logout", use_container_width=True):
            from ui.auth import clear_session

            clear_session()
            st.rerun()


def route_page() -> None:
    logged_in = st.session_state.get("logged_in", False)
    current_page = st.session_state.get("current_page", "dashboard")

    if not logged_in:
        from ui.auth import render_auth

        render_auth()
        return

    roadmap_required = {"roadmap", "quiz", "projects"}
    if current_page in roadmap_required and not st.session_state.get("current_roadmap_id"):
        st.warning("Please select a roadmap from your dashboard first.")
        st.session_state.current_page = "dashboard"
        from ui.dashboard import render_dashboard

        render_dashboard()
        return

    if current_page == "dashboard":
        from ui.dashboard import render_dashboard

        render_dashboard()

    elif current_page == "generate":
        from ui.generate import render_generate

        render_generate()

    elif current_page == "roadmap":
        from ui.roadmap_view import render_roadmap

        render_roadmap()

    elif current_page == "quiz":
        from ui.quiz_ui import render_quiz

        render_quiz()

    elif current_page == "projects":
        from ui.projects_view import render_projects

        render_projects()

    else:
        st.session_state.current_page = "dashboard"
        from ui.dashboard import render_dashboard

        render_dashboard()


def main() -> None:
    check_env_vars()

    try:
        from db.mongo import ensure_indexes

        ensure_indexes()
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        st.stop()

    init_session_state()

    rehydrate_session()

    render_sidebar()

    route_page()


main()
