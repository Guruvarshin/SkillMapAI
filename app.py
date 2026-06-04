"""
app.py
──────
SkillMap AI — Streamlit entry point.

Runs on every user interaction (Streamlit's rerun model).
Execution order on every rerun:
  1. set_page_config()     — must be first st call
  2. check_env_vars()      — fail fast if API keys missing
  3. ensure_indexes()      — idempotent DB index creation
  4. init_session_state()  — safe defaults via setdefault
  5. rehydrate_session()   — restore auth on page reload
  6. render_sidebar()      — navigation always visible
  7. route_page()          — render correct ui/ module

Pages:
  dashboard  → ui/dashboard.py  (requires login)
  generate   → ui/generate.py   (requires login)
  roadmap    → ui/roadmap_view.py (requires login + roadmap selected)
  quiz       → ui/quiz_ui.py    (requires login + roadmap + subtopic)
  projects   → ui/projects_view.py (requires login + roadmap)
  auth       → ui/auth.py       (shown when not logged in)
"""

import os
import streamlit as st
from dotenv import load_dotenv

# Load .env for local development.
# On Streamlit Cloud, env vars come from Secrets dashboard.
load_dotenv()


# ─────────────────────────────────────────────
# PAGE CONFIG — must be the very first st call
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="SkillMap AI",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "SkillMap AI — Personalised learning roadmaps powered by Claude AI",
    },
)


# ─────────────────────────────────────────────
# ENVIRONMENT CHECK
# ─────────────────────────────────────────────

def check_env_vars() -> None:
    """
    Verify all required environment variables are set.

    Called once at startup. Uses st.stop() to halt the app with a
    clear error message rather than letting a cryptic KeyError appear
    somewhere deep in the codebase.
    """
    required = {
        "ANTHROPIC_API_KEY": "https://console.anthropic.com/",
        "YOUTUBE_API_KEY": "https://console.cloud.google.com/ → YouTube Data API v3",
        "TAVILY_API_KEY": "https://tavily.com/",
        "MONGODB_URI": "https://cloud.mongodb.com/",
    }

    missing = [
        f"- `{key}` — get it at {url}"
        for key, url in required.items()
        if not os.environ.get(key) or os.environ.get(key, "").startswith("your_")
    ]

    if missing:
        st.error(
            "**⚠️ Missing API keys.** Add these to your `.env` file "
            "(local) or Streamlit Cloud Secrets (deployed):\n\n"
            + "\n".join(missing)
        )
        st.stop()


# ─────────────────────────────────────────────
# SESSION STATE INITIALISATION
# ─────────────────────────────────────────────

def init_session_state() -> None:
    """
    Set safe defaults for all session_state keys.

    Uses setdefault so existing values are NEVER overwritten on rerun.
    Only sets a key if it doesn't already exist.
    """
    defaults = {
        # Auth
        "logged_in": False,
        "user_id": None,
        "user_name": None,
        "user_email": None,
        # Navigation
        "current_page": "dashboard",
        # Roadmap context
        "current_roadmap_id": None,
        "current_roadmap": None,       # Cached roadmap doc
        # Generation state
        "generation_running": False,
        # Quiz context
        "current_subtopic_id": None,
        "current_subtopic_name": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


# ─────────────────────────────────────────────
# AUTH RE-HYDRATION
# ─────────────────────────────────────────────

def rehydrate_session() -> None:
    """
    Restore auth session on page reload.

    Streamlit Cloud keeps session_state alive for the browser tab session.
    But if the server restarts (deploy, idle timeout), session_state is lost.

    On reload with empty session_state, user_id is None and logged_in is False
    — user simply has to log in again (all data is safely in MongoDB).

    This function handles one edge case: if user_id IS set (shouldn't happen
    after server restart, but could happen with client-side state restoration)
    but logged_in is False, we re-verify the user from MongoDB.
    """
    user_id = st.session_state.get("user_id")
    logged_in = st.session_state.get("logged_in", False)

    if user_id and not logged_in:
        # user_id exists but logged_in is False — re-verify from DB
        from db.users import get_user_by_id
        user = get_user_by_id(user_id)
        if user:
            st.session_state.logged_in = True
            st.session_state.user_name = user["name"]
            st.session_state.user_email = user["email"]
        else:
            # User no longer exists in DB — clear session
            st.session_state.user_id = None


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

def render_sidebar() -> None:
    """
    Render the sidebar navigation.

    Shows different options based on login state.
    Navigation buttons update session_state.current_page + st.rerun().
    """
    with st.sidebar:
        st.markdown("# 🗺️ SkillMap AI")
        st.caption("Your AI-powered learning companion")
        st.divider()

        if not st.session_state.get("logged_in"):
            st.info("Login or create an account to get started.")
            return

        # ── Logged-in navigation ─────────────────────────────────────────────
        user_name = st.session_state.get("user_name", "User")
        st.markdown(f"👤 **{user_name}**")
        st.divider()

        # Main navigation
        nav_items = [
            ("🏠 Dashboard", "dashboard"),
            ("✨ Generate Roadmap", "generate"),
        ]

        # Show roadmap-specific nav if a roadmap is selected
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
                    # Quiz needs a subtopic — go to final quiz by default
                    st.session_state.current_subtopic_id = "final"
                    st.session_state.current_subtopic_name = "Final Quiz"
                st.session_state.current_page = page
                st.rerun()

        st.divider()

        # ── Current roadmap info ─────────────────────────────────────────────
        current_roadmap = st.session_state.get("current_roadmap")
        if current_roadmap:
            skill = current_roadmap.get("skill", "")
            st.caption(f"📋 Current: **{skill}**")
            st.divider()

        # ── Logout ───────────────────────────────────────────────────────────
        if st.button("🚪 Logout", use_container_width=True):
            from ui.auth import clear_session
            clear_session()
            st.rerun()


# ─────────────────────────────────────────────
# PAGE ROUTER
# ─────────────────────────────────────────────

def route_page() -> None:
    """
    Render the correct page module based on current_page and auth state.

    Auth guard: any page except "auth" redirects to auth if not logged in.
    Roadmap guard: roadmap/quiz/projects redirect to dashboard if no roadmap selected.
    """
    logged_in = st.session_state.get("logged_in", False)
    current_page = st.session_state.get("current_page", "dashboard")

    # ── Not logged in → auth page ─────────────────────────────────────────────
    if not logged_in:
        from ui.auth import render_auth
        render_auth()
        return

    # ── Roadmap-required pages guard ──────────────────────────────────────────
    roadmap_required = {"roadmap", "quiz", "projects"}
    if current_page in roadmap_required and not st.session_state.get("current_roadmap_id"):
        st.warning("Please select a roadmap from your dashboard first.")
        st.session_state.current_page = "dashboard"
        from ui.dashboard import render_dashboard
        render_dashboard()
        return

    # ── Page routing ──────────────────────────────────────────────────────────
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
        # Unknown page — fall back to dashboard
        st.session_state.current_page = "dashboard"
        from ui.dashboard import render_dashboard
        render_dashboard()


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main() -> None:
    """
    Main execution — called on every Streamlit rerun.

    Execution order is strict — do not reorder these calls.
    """
    # 1. Check API keys are set (fail fast with clear message)
    check_env_vars()

    # 2. Ensure MongoDB indexes exist (idempotent — safe on every rerun)
    try:
        from db.mongo import ensure_indexes
        ensure_indexes()
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        st.stop()

    # 3. Initialise session state with safe defaults
    init_session_state()

    # 4. Re-hydrate auth on page reload
    rehydrate_session()

    # 5. Render sidebar (always visible)
    render_sidebar()

    # 6. Route to correct page
    route_page()


# Streamlit executes this file on every rerun — call main() unconditionally.
main()
