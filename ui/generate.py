import time
import threading
import streamlit as st

from db.roadmaps import save_roadmap, update_status
from agents.flow import run_skillmap_flow, get_progress_updates


def render_generate() -> None:
    st.title("✨ Generate Your Roadmap")
    st.markdown(
        "Enter a skill or job role and get a complete, personalised "
        "learning roadmap with videos, courses, projects, and quizzes."
    )
    st.divider()

    if st.session_state.get("generation_running"):
        _render_generation_waiting()
        return

    _render_input_form()


def _render_input_form() -> None:
    with st.form("generate_form"):
        st.subheader("What do you want to learn?")

        skill = st.text_input(
            "Skill or job role",
            placeholder="e.g. React Developer, Machine Learning Engineer, Data Analyst...",
            help="Be specific for the best results. 'React Developer' is better than 'JavaScript'.",
        )

        level = st.selectbox(
            "Your current level",
            options=["beginner", "intermediate", "advanced"],
            format_func=lambda x: {
                "beginner": "🟢 Beginner,little or no experience",
                "intermediate": "🟡 Intermediate,some experience, want to go deeper",
                "advanced": "🔴 Advanced,experienced, want to master edge cases",
            }[x],
        )

        st.info(
            "⏱️ Generation takes **2–5 minutes**. "
            "The AI will search for videos, courses, and design projects for every subtopic. "
            "Please keep this tab open."
        )

        submitted = st.form_submit_button(
            "🚀 Generate Roadmap",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        skill = skill.strip()
        if not skill:
            st.error("Please enter a skill or job role.")
            return
        if len(skill) < 3:
            st.error("Please be more specific,at least 3 characters.")
            return
        if len(skill) > 100:
            st.error("Skill name too long. Please keep it under 100 characters.")
            return

        _run_generation(skill, level)


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


def _run_with_status(skill: str, level: str, roadmap_id: str, user_id: str) -> bool:
    result = {"success": False, "error": None}

    def _worker():
        try:
            run_skillmap_flow(
                skill=skill,
                level=level,
                roadmap_id=roadmap_id,
                user_id=user_id,
            )
            result["success"] = True
        except Exception as e:
            result["error"] = e

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()

    with st.status(f"🚀 Generating roadmap for: **{skill}**", expanded=True) as status:
        st.markdown("**Stages:**")
        stage1 = st.empty()
        stage2 = st.empty()
        stage3 = st.empty()
        st.caption("Keep this tab open. Progress updates appear below.")
        st.divider()
        log_area = st.empty()

        stage1.markdown("⏳ Stage 1: Building topic structure...")
        stage2.markdown("⏳ Stage 2: Searching videos, courses, projects, quizzes...")
        stage3.markdown("⏳ Stage 3: Assembling final roadmap...")

        seen = 0

        while thread.is_alive():
            updates = get_progress_updates()

            all_text = " ".join(updates)
            if "Stage 1 complete" in all_text:
                stage1.markdown("✅ Stage 1: Topic structure built")
            if "Stage 2 complete" in all_text:
                stage2.markdown("✅ Stage 2: Resources found")
            if "Stage 3" in all_text and "complete" in all_text.lower():
                stage3.markdown("✅ Stage 3: Roadmap assembled and saved")

            new = updates[seen:]
            if new:
                seen = len(updates)
                with log_area.container():
                    for msg in updates:
                        st.markdown(f"- {msg}")

            time.sleep(2)

        thread.join()
        updates = get_progress_updates()
        if updates:
            with log_area.container():
                for msg in updates:
                    st.markdown(f"- {msg}")

        if result["success"]:
            stage1.markdown("✅ Stage 1: Topic structure built")
            stage2.markdown("✅ Stage 2: Resources found")
            stage3.markdown("✅ Stage 3: Roadmap assembled and saved")
            status.update(
                label=f"✅ Roadmap ready: **{skill}**",
                state="complete",
                expanded=False,
            )
            st.success(f"🎉 Your **{skill}** roadmap is ready! Redirecting...")
            time.sleep(1.5)
            return True

        else:
            e = result["error"]
            error_str = str(e) if e else "Unknown error"

            if "Architect" in error_str or "Stage 1" in error_str:
                stage1.markdown("❌ Stage 1: Failed to build topic structure")
            elif "Assembler" in error_str or "Stage 3" in error_str:
                stage1.markdown("✅ Stage 1: Topic structure built")
                stage2.markdown("✅ Stage 2: Resources gathered")
                stage3.markdown("❌ Stage 3: Failed to assemble roadmap")
            else:
                stage2.markdown("❌ Stage 2: Resource search failed")

            status.update(label="❌ Generation failed", state="error", expanded=True)
            st.error(
                f"**Generation failed:** {error_str}\n\n"
                "Please try again. If the issue persists, check your API keys."
            )

            try:
                update_status(roadmap_id, "failed", error_str)
            except Exception:
                pass

            return False


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
