import streamlit as st
from db.roadmaps import list_user_roadmaps, delete_roadmap
from db.progress import get_progress
from utils.helpers import time_ago, pct_to_display
def render_dashboard() -> None:
    user_id = st.session_state.get("user_id")
    user_name = st.session_state.get("user_name", "there")
    col_title, col_btn = st.columns([3, 1])
    with col_title:
        st.markdown(f"""
        <div style="padding: 0.5rem 0 1rem">
            <div style="font-size: 0.8rem; color: #6B7280; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px">Welcome back</div>
            <div style="font-size: 2rem; font-weight: 800; color: #F9FAFB">{user_name} 👋</div>
        </div>
        """, unsafe_allow_html=True)
    with col_btn:
        st.write(""); st.write("")
        if st.button("✨ New Roadmap", type="primary", use_container_width=True):
            st.session_state.current_page = "generate"
            st.rerun()
    with st.spinner(""):
        roadmaps = list_user_roadmaps(user_id)
    if not roadmaps:
        _render_empty_state()
        return
    done_count = sum(1 for r in roadmaps if r.get("status") == "done")
    in_progress = sum(1 for r in roadmaps if r.get("status") == "generating")
    total_pct = sum(get_progress(user_id, r["_id"]).get("overall_pct", 0) for r in roadmaps if r.get("status") == "done")
    avg_pct = (total_pct / done_count * 100) if done_count else 0
    c1, c2, c3, c4 = st.columns(4)
    for col, num, label in [
        (c1, len(roadmaps), "Total Roadmaps"),
        (c2, done_count, "Ready to Learn"),
        (c3, in_progress, "Generating"),
        (c4, f"{avg_pct:.0f}%", "Avg Progress"),
    ]:
        col.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{num}</div>
            <div class="stat-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<div style='margin: 1.5rem 0 1rem'><span style='font-size:1.1rem;font-weight:700;color:#F9FAFB'>Your Roadmaps</span> <span style='color:#6B7280;font-size:0.875rem'>({} total)</span></div>".format(len(roadmaps)), unsafe_allow_html=True)
    progress_map = {r["_id"]: get_progress(user_id, r["_id"]) for r in roadmaps}
    cols = st.columns(2, gap="medium")
    for idx, roadmap in enumerate(roadmaps):
        with cols[idx % 2]:
            _render_roadmap_card(roadmap, progress_map.get(roadmap["_id"], {}), user_id)
def _render_roadmap_card(roadmap: dict, progress: dict, user_id: str) -> None:
    status = roadmap.get("status", "done")
    roadmap_id = roadmap["_id"]
    overall_pct = progress.get("overall_pct", 0.0)
    level = roadmap.get("level", "beginner")
    level_class = f"level-{level}"
    level_icons = {"beginner": "🟢", "intermediate": "🟡", "advanced": "🔴"}
    icon = level_icons.get(level, "⚪")
    status_html = {
        "done": '<span class="done-pill">✓ Ready</span>',
        "generating": '<span class="generating-pill">⏳ Generating</span>',
        "failed": '<span class="failed-pill">✕ Failed</span>',
    }.get(status, "")
    pct_int = int(overall_pct * 100)
    time_str = time_ago(roadmap.get("created_at"))
    st.markdown(f"""
    <div class="roadmap-card">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px">
            <div class="roadmap-title">{roadmap.get('skill', 'Untitled')}</div>
            <span class="level-badge {level_class}">{icon} {level.capitalize()}</span>
        </div>
        {status_html}
        <div style="margin: 12px 0 6px">
            <div style="display:flex;justify-content:space-between;font-size:0.78rem;color:#6B7280;margin-bottom:5px">
                <span>Progress</span>
                <span style="color:#8B5CF6;font-weight:700">{pct_int}%</span>
            </div>
            <div style="background:#1F2937;border-radius:99px;height:6px;overflow:hidden">
                <div style="width:{pct_int}%;height:100%;background:linear-gradient(90deg,#7C3AED,#8B5CF6,#06B6D4);border-radius:99px;transition:width 0.5s ease"></div>
            </div>
        </div>
        <div style="font-size:0.75rem;color:#4B5563;margin-top:8px">{time_str}</div>
    </div>
    """, unsafe_allow_html=True)
    if status == "failed" and roadmap.get("error_message"):
        with st.expander("⚠️ See error"):
            st.code(roadmap["error_message"], language=None)
    btn_col1, btn_col2 = st.columns([3, 1])
    with btn_col1:
        if st.button("📋 View Roadmap" if status == "done" else "⏳ Generating...",
                     key=f"view_{roadmap_id}", disabled=(status != "done"),
                     use_container_width=True, type="primary"):
            st.session_state.current_roadmap_id = roadmap_id
            st.session_state.pop("current_roadmap", None)
            st.session_state.current_page = "roadmap"
            st.rerun()
    with btn_col2:
        confirm_key = f"confirm_delete_{roadmap_id}"
        if st.session_state.get(confirm_key):
            if st.button("✅", key=f"confirm_{roadmap_id}", use_container_width=True, help="Confirm delete"):
                with st.spinner(""):
                    delete_roadmap(roadmap_id, user_id)
                st.session_state.pop(confirm_key, None)
                st.rerun()
        else:
            if st.button("🗑️", key=f"delete_{roadmap_id}", use_container_width=True, help="Delete"):
                st.session_state[confirm_key] = True
                st.rerun()
    st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)
def _render_empty_state() -> None:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">🗺️</div>
        <div class="empty-title">No roadmaps yet</div>
        <div class="empty-desc">Generate your first personalised learning roadmap. Type any skill and get a complete study plan with videos, courses, and projects.</div>
    </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("✨ Generate Your First Roadmap", type="primary", use_container_width=True):
            st.session_state.current_page = "generate"
            st.rerun()
