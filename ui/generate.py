import time
import streamlit as st
from db.roadmaps import save_roadmap, update_status
from agents.flow import run_skillmap_flow, get_progress_updates
def render_generate() -> None:
    if st.session_state.get("generation_running"):
        _render_generation_waiting()
        return
    _render_input_form()
def _render_input_form() -> None:
    col_main, col_side = st.columns([3, 2], gap="large")
    with col_main:
        st.markdown("""
        <div style="padding: 0.5rem 0 1.5rem">
            <div style="font-size: 0.8rem; color: #6B7280; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px">New Roadmap</div>
            <div style="font-size: 2rem; font-weight: 800; color: #F9FAFB; margin-bottom: 8px">What do you want to <span class="gradient-text">master?</span></div>
            <div style="color: #9CA3AF; font-size: 0.9rem">Type any skill or job role to get a complete learning plan.</div>
        </div>
        """, unsafe_allow_html=True)
        with st.form("generate_form"):
            skill = st.text_input(
                "Skill or job role",
                placeholder="e.g. React Developer, Machine Learning, Data Analyst, DevOps...",
                help="Be specific. 'React Developer' gives better results than just 'JavaScript'.",
            )
            level = st.selectbox(
                "Your current level",
                options=["beginner", "intermediate", "advanced"],
                format_func=lambda x: {
                    "beginner": "🟢 Beginner — little or no prior experience",
                    "intermediate": "🟡 Intermediate — some experience, going deeper",
                    "advanced": "🔴 Advanced — experienced, mastering edge cases",
                }[x],
            )
            st.markdown("""
            <div style="background:rgba(139,92,246,0.08);border:1px solid rgba(139,92,246,0.2);border-radius:10px;padding:12px 16px;font-size:0.85rem;color:#A78BFA;margin:0.5rem 0">
                ⏱️ Generation takes <strong>2–5 minutes</strong>. The AI searches videos, courses, and designs custom projects for every subtopic. Keep this tab open.
            </div>
            """, unsafe_allow_html=True)
            submitted = st.form_submit_button(
                "🚀 Generate My Roadmap",
                type="primary",
                use_container_width=True,
            )
        if submitted:
            skill = skill.strip()
            if not skill:
                st.error("Please enter a skill or job role.")
                return
            if len(skill) < 3:
                st.error("Please be more specific — at least 3 characters.")
                return
            if len(skill) > 100:
                st.error("Skill name too long. Please keep it under 100 characters.")
                return
            _run_generation(skill, level)
    with col_side:
        st.markdown("""
        <div style="padding: 1.5rem 0 0">
            <div style="font-size: 0.8rem; color: #6B7280; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 1rem">What you'll get</div>
        </div>
        """, unsafe_allow_html=True)
        features = [
            ("📹", "YouTube Videos", "Best tutorial videos and full course playlists for every subtopic"),
            ("📚", "Text Resources", "Official docs, guides, and authoritative tutorials"),
            ("🎓", "Free Courses", "Courses with free certificates on Coursera, edX, freeCodeCamp"),
            ("💳", "Paid Courses", "Best-rated Udemy courses with real prices"),
            ("🔨", "Mini Projects", "Hands-on projects for each subtopic (1-3 hours each)"),
            ("🏗️", "Capstone Projects", "Larger projects linking skills across topics"),
            ("🚀", "Portfolio Project", "One major resume-worthy project for the full roadmap"),
            ("❓", "Quiz Questions", "Interview-ready questions for every subtopic"),
            ("🗓️", "Timeline", "Realistic week-by-week learning schedule"),
            ("💰", "Budget Guide", "Free path and paid path with exact costs"),
        ]
        for icon, title, desc in features:
            st.markdown(f"""
            <div style="display:flex;gap:12px;padding:10px 0;border-bottom:1px solid #1F2937">
                <div style="font-size:1.2rem;flex-shrink:0;margin-top:1px">{icon}</div>
                <div>
                    <div style="font-weight:600;color:#F9FAFB;font-size:0.875rem">{title}</div>
                    <div style="font-size:0.78rem;color:#6B7280;margin-top:1px">{desc}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
def _run_generation(skill: str, level: str) -> None:
    user_id = st.session_state.get("user_id")
    with st.spinner("Creating your roadmap..."):
        roadmap_id = save_roadmap(user_id, skill, level)
    st.session_state.generation_running = True
    st.session_state.current_roadmap_id = roadmap_id
    success = _run_with_status(skill, level, roadmap_id, user_id)
    st.session_state.generation_running = False
    if success:
        st.session_state.current_page = "roadmap"
        st.session_state.pop("current_roadmap", None)                    
        st.rerun()
def _run_with_status(
    skill: str,
    level: str,
    roadmap_id: str,
    user_id: str,
) -> bool:
    with st.status(
        f"🚀 Generating roadmap for: **{skill}**",
        expanded=True,
    ) as status:
        st.markdown("**Stages:**")
        stage1 = st.empty()
        stage2 = st.empty()
        stage3 = st.empty()
        log_container = st.empty()
        stage1.markdown("⏳ Stage 1: Building topic structure...")
        stage2.markdown("⏳ Stage 2: Searching videos, courses, projects, quizzes...")
        stage3.markdown("⏳ Stage 3: Assembling final roadmap...")
        st.caption("Keep this tab open. Progress updates appear below.")
        st.divider()
        try:
            run_skillmap_flow(
                skill=skill,
                level=level,
                roadmap_id=roadmap_id,
                user_id=user_id,
            )
            updates = get_progress_updates()
            _render_progress_log(log_container, updates)
            stage1.markdown("✅ Stage 1: Topic structure built")
            stage2.markdown("✅ Stage 2: Resources found")
            stage3.markdown("✅ Stage 3: Roadmap assembled and saved")
            status.update(
                label=f"✅ Roadmap ready: **{skill}**",
                state="complete",
                expanded=False,
            )
            st.success(
                f"🎉 Your **{skill}** roadmap is ready! "
                "Redirecting you to your roadmap..."
            )
            time.sleep(1.5)
            return True
        except Exception as e:
            updates = get_progress_updates()
            _render_progress_log(log_container, updates)
            error_str = str(e)
            if "Architect" in error_str or "Stage 1" in error_str:
                stage1.markdown("❌ Stage 1: Failed to build topic structure")
            elif "Assembler" in error_str or "Stage 3" in error_str:
                stage1.markdown("✅ Stage 1: Topic structure built")
                stage2.markdown("✅ Stage 2: Resources gathered")
                stage3.markdown("❌ Stage 3: Failed to assemble roadmap")
            else:
                stage2.markdown("❌ Stage 2: Resource search failed")
            status.update(
                label="❌ Generation failed",
                state="error",
                expanded=True,
            )
            st.error(
                f"**Generation failed:** {e}\n\n"
                "Your skeleton roadmap has been saved with status 'failed'. "
                "Please try again. If the issue persists, check your API keys."
            )
            try:
                update_status(roadmap_id, "failed", str(e))
            except Exception:
                pass
            return False
def _render_progress_log(container, updates: list[str]) -> None:
    if not updates:
        return
    with container.container():
        st.markdown("**Generation log:**")
        for msg in updates:
            st.markdown(f"- {msg}")
def _render_generation_waiting() -> None:
    st.info(
        "⏳ **Generation in progress...**\n\n"
        "Your roadmap is being generated. "
        "If you refreshed this page accidentally, "
        "go to your Dashboard to check its status."
    )
    if st.button("← Back to Dashboard"):
        st.session_state.generation_running = False
        st.session_state.current_page = "dashboard"
        st.rerun()
