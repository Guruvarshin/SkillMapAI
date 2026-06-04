import streamlit as st
from db.roadmaps import list_user_roadmaps, delete_roadmap
from db.progress import get_progress
from utils.helpers import format_level, format_status, time_ago, pct_to_display


def render_dashboard() -> None:

    user_id = st.session_state.get("user_id")
    user_name = st.session_state.get("user_name", "there")

    col_title, col_btn = st.columns([3, 1])
    with col_title:
        st.title(f"👋 Welcome back, {user_name}!")
        st.caption("Your personalised learning roadmaps")
    with col_btn:
        st.write("")
        if st.button("✨ New Roadmap", type="primary", use_container_width=True):
            st.session_state.current_page = "generate"
            st.rerun()

    st.divider()

    with st.spinner("Loading your roadmaps..."):
        roadmaps = list_user_roadmaps(user_id)

    if not roadmaps:
        _render_empty_state()
        return

    done_count = sum(1 for r in roadmaps if r.get("status") == "done")
    _render_stats(len(roadmaps), done_count)
    st.divider()

    st.subheader(f"📋 Your Roadmaps ({len(roadmaps)})")

    progress_map = {r["_id"]: get_progress(user_id, r["_id"]) for r in roadmaps}

    cols = st.columns(2, gap="medium")
    for idx, roadmap in enumerate(roadmaps):
        col = cols[idx % 2]
        with col:
            _render_roadmap_card(roadmap, progress_map.get(roadmap["_id"], {}), user_id)


def _render_stats(total: int, done: int) -> None:

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Roadmaps", total)
    c2.metric("Completed Generation", done)
    c3.metric("In Progress", total - done)


def _render_roadmap_card(roadmap: dict, progress: dict, user_id: str) -> None:

    status = roadmap.get("status", "done")
    roadmap_id = roadmap["_id"]
    overall_pct = progress.get("overall_pct", 0.0)

    with st.container(border=True):

        title_col, badge_col = st.columns([3, 1])
        with title_col:
            st.markdown(f"### {roadmap.get('skill', 'Untitled')}")
        with badge_col:
            st.markdown(
                f"<div style='text-align:right; padding-top:8px'>"
                f"{format_level(roadmap.get('level', 'beginner'))}"
                f"</div>",
                unsafe_allow_html=True,
            )

        if status == "done":
            st.progress(overall_pct, text=f"Progress: {pct_to_display(overall_pct)}")
        elif status == "generating":
            st.progress(0.0, text="⏳ Generating...")
        else:
            st.progress(0.0, text="❌ Generation failed")

        created_at = roadmap.get("created_at")
        status_str = format_status(status)
        time_str = time_ago(created_at)
        st.caption(f"{status_str}  •  {time_str}")

        if status == "failed" and roadmap.get("error_message"):
            with st.expander("See error"):
                st.code(roadmap["error_message"], language=None)

        btn_col1, btn_col2 = st.columns([3, 1])

        with btn_col1:
            view_disabled = status != "done"
            view_label = "📋 View Roadmap" if not view_disabled else "⏳ Generating..."
            if st.button(
                view_label,
                key=f"view_{roadmap_id}",
                disabled=view_disabled,
                use_container_width=True,
                type="primary",
            ):
                st.session_state.current_roadmap_id = roadmap_id

                st.session_state.pop("current_roadmap", None)
                st.session_state.current_page = "roadmap"
                st.rerun()

        with btn_col2:

            confirm_key = f"confirm_delete_{roadmap_id}"
            if st.session_state.get(confirm_key):

                if st.button(
                    "✅",
                    key=f"confirm_{roadmap_id}",
                    use_container_width=True,
                    help="Click to confirm deletion",
                ):
                    with st.spinner("Deleting..."):
                        delete_roadmap(roadmap_id, user_id)
                    st.session_state.pop(confirm_key, None)
                    st.success("Roadmap deleted.")
                    st.rerun()
            else:
                if st.button(
                    "🗑️",
                    key=f"delete_{roadmap_id}",
                    use_container_width=True,
                    help="Delete this roadmap",
                ):
                    st.session_state[confirm_key] = True
                    st.rerun()


def _render_empty_state() -> None:

    st.markdown("")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
            <div style="text-align: center; padding: 40px 0;">
                <div style="font-size: 64px;">🗺️</div>
                <h3>No roadmaps yet</h3>
                <p style="color: gray;">
                    Generate your first personalised learning roadmap.<br>
                    Type a skill and get a complete study plan in minutes.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(
            "✨ Generate Your First Roadmap",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.current_page = "generate"
            st.rerun()
