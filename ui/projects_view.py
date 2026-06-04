import streamlit as st
from db.roadmaps import get_roadmap
from utils.helpers import truncate_text
def render_projects() -> None:
    roadmap_id = st.session_state.get("current_roadmap_id")
    if not roadmap_id:
        st.error("No roadmap selected.")
        if st.button("← Dashboard"):
            st.session_state.current_page = "dashboard"
            st.rerun()
        return
    roadmap = st.session_state.get("current_roadmap")
    if not roadmap or roadmap.get("_id") != roadmap_id:
        roadmap = get_roadmap(roadmap_id)
        if roadmap:
            st.session_state.current_roadmap = roadmap
    if not roadmap:
        st.error("Roadmap not found.")
        return
    col_back, col_title = st.columns([1, 5])
    with col_back:
        if st.button("← Roadmap", use_container_width=True):
            st.session_state.current_page = "roadmap"
            st.rerun()
    with col_title:
        st.title(f"🚀 Projects — {roadmap.get('skill', '')}")
        st.caption("Portfolio projects designed to reinforce and showcase your skills")
    st.divider()
    topics = roadmap.get("topics", [])
    major = roadmap.get("major_project", {})
    if major and major.get("title"):
        _render_major_project(major)
        st.divider()
    if not topics:
        st.warning("No project data found in this roadmap.")
        return
    tab_mini, tab_capstone = st.tabs(["🔨 Mini Projects", "🏗️ Capstone Projects"])
    with tab_mini:
        _render_mini_projects(topics)
    with tab_capstone:
        _render_capstone_projects(topics)
def _render_major_project(major: dict) -> None:
    tech_chips = "".join(f'<span class="tech-chip">{t}</span>' for t in major.get("tech_stack", []))
    features_html = "".join(
        f'<div class="feature-item"><div class="feature-dot"></div>{f}</div>'
        for f in major.get("features", [])
    )
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#111827,#1F2937);border:1px solid #374151;border-radius:20px;padding:2rem;position:relative;overflow:hidden;margin-bottom:1rem">
        <div style="position:absolute;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg,#7C3AED,#8B5CF6,#06B6D4)"></div>
        <div style="position:absolute;top:-30%;right:-5%;width:250px;height:250px;background:radial-gradient(circle,rgba(139,92,246,0.06) 0%,transparent 70%);pointer-events:none"></div>
        <div style="margin-bottom:6px"><span class="badge-major">⭐ Major Portfolio Project</span></div>
        <div style="font-size:1.6rem;font-weight:800;color:#F9FAFB;margin:10px 0 8px">{major.get('title','Portfolio Project')}</div>
        <div style="color:#9CA3AF;font-size:0.9rem;line-height:1.6;margin-bottom:1.5rem">{major.get('description','')}</div>
        <div style="display:flex;gap:2rem;flex-wrap:wrap">
            <div style="flex:1;min-width:200px">
                <div style="font-size:0.75rem;color:#6B7280;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;font-weight:600">Tech Stack</div>
                <div>{tech_chips}</div>
            </div>
            <div style="flex:1;min-width:200px">
                <div style="font-size:0.75rem;color:#6B7280;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;font-weight:600">Key Features</div>
                {features_html}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if major.get("github_structure"):
        with st.expander("📁 Suggested GitHub Structure"):
            st.code(major["github_structure"], language=None)
def _render_mini_projects(topics: list) -> None:
    st.markdown(
        "Small, focused projects (1–3 hours each) that reinforce "
        "each subtopic's concepts with a real-world use case."
    )
    st.markdown("")
    for topic in topics:
        subtopics = topic.get("subtopics", [])
        topic_projects = [
            (s.get("name", ""), s.get("mini_project", {}))
            for s in subtopics
            if s.get("mini_project", {}).get("title")
        ]
        if not topic_projects:
            continue
        st.markdown(f"### {topic.get('name', 'Topic')}")
        cols = st.columns(2, gap="medium")
        for idx, (sub_name, proj) in enumerate(topic_projects):
            col = cols[idx % 2]
            with col:
                _render_mini_card(sub_name, proj)
        st.markdown("")
def _render_mini_card(sub_name: str, proj: dict) -> None:
    vid_url = proj.get("tutorial_video_url", "")
    vid_html = f'<a href="{vid_url}" target="_blank" style="display:inline-flex;align-items:center;gap:5px;font-size:0.75rem;color:#06B6D4;margin-top:8px;text-decoration:none">▶ Watch Tutorial</a>' if vid_url else ""
    st.markdown(f"""
    <div style="background:#111827;border:1px solid #1F2937;border-radius:12px;padding:1rem;margin-bottom:8px;transition:border-color 0.2s" onmouseover="this.style.borderColor='#374151'" onmouseout="this.style.borderColor='#1F2937'">
        <div style="margin-bottom:6px"><span class="badge-mini">Mini Project</span></div>
        <div style="font-weight:700;color:#F9FAFB;font-size:0.9rem;margin-bottom:4px">{proj.get('title','Project')}</div>
        <div style="font-size:0.75rem;color:#6B7280;margin-bottom:6px">📌 {sub_name}</div>
        <div style="font-size:0.8rem;color:#9CA3AF;line-height:1.5">{truncate_text(proj.get('use_case',''),110)}</div>
        {vid_html}
    </div>
    """, unsafe_allow_html=True)
def _render_capstone_projects(topics: list) -> None:
    st.markdown(
        "Half-day projects that combine multiple subtopics within "
        "a topic into one cohesive application."
    )
    st.markdown("")
    for topic in topics:
        subtopics = topic.get("subtopics", [])
        capstones = [
            (s.get("name", ""), s.get("capstone_project", {}))
            for s in subtopics
            if s.get("capstone_project", {}).get("title")
        ]
        if not capstones:
            continue
        st.markdown(f"### {topic.get('name', 'Topic')}")
        for sub_name, cap in capstones:
            _render_capstone_card(sub_name, cap)
        st.markdown("")
def _render_capstone_card(sub_name: str, cap: dict) -> None:
    st.markdown(f"""
    <div style="background:#111827;border:1px solid #1F2937;border-radius:12px;padding:1.1rem;margin-bottom:8px">
        <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:1rem;margin-bottom:8px">
            <div>
                <div style="margin-bottom:4px"><span class="badge-capstone">Capstone</span></div>
                <div style="font-weight:700;color:#F9FAFB;font-size:0.95rem;margin-top:6px">{cap.get('title','Capstone')}</div>
            </div>
            <div style="font-size:0.72rem;color:#6B7280;text-align:right;white-space:nowrap;margin-top:4px">{sub_name}</div>
        </div>
        <div style="font-size:0.82rem;color:#9CA3AF;line-height:1.5;margin-bottom:6px">{cap.get('description','')}</div>
        <div style="font-size:0.75rem;color:#6B7280">📌 {cap.get('use_case','')}</div>
    </div>
    """, unsafe_allow_html=True)
