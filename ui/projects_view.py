\
\
\
\
\
\
\
\
\
\
\
\

import streamlit as st
from db.roadmaps import get_roadmap
from utils.helpers import truncate_text

def render_projects() -> None:
\
\
\
\
\

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
\
\
\
\
\

    st.subheader("🏆 Major Portfolio Project")
    st.caption("Your capstone project — build this to showcase full roadmap mastery")

    with st.container(border=True):
        st.markdown(f"## {major.get('title', 'Portfolio Project')}")
        st.markdown(major.get("description", ""))

        col1, col2 = st.columns(2)

        with col1:
            tech_stack = major.get("tech_stack", [])
            if tech_stack:
                st.markdown("**🛠️ Tech Stack**")

                chips = "  ".join(f"`{t}`" for t in tech_stack)
                st.markdown(chips)

        with col2:
            github_structure = major.get("github_structure", "")
            if github_structure:
                st.markdown("**📁 GitHub Structure**")
                st.code(github_structure, language=None)

        features = major.get("features", [])
        if features:
            st.markdown("**✨ Key Features**")
            for f in features:
                st.markdown(f"- {f}")

def _render_mini_projects(topics: list) -> None:
\
\
\
\
\
\
\
\

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

    with st.container(border=True):
        st.markdown(f"**{proj.get('title', 'Project')}**")
        st.caption(f"*Subtopic: {sub_name}*")
        use_case = proj.get("use_case", "")
        if use_case:
            st.markdown(truncate_text(use_case, 120))
        vid_url = proj.get("tutorial_video_url", "")
        if vid_url:
            st.markdown(f"[▶️ Tutorial Video]({vid_url})")

def _render_capstone_projects(topics: list) -> None:
\
\
\
\
\
\
\
\

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

    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{cap.get('title', 'Capstone')}**")
        with col2:
            st.caption(f"*{sub_name}*")

        desc = cap.get("description", "")
        if desc:
            st.markdown(desc)

        use_case = cap.get("use_case", "")
        if use_case:
            st.caption(f"📌 Use case: {use_case}")
