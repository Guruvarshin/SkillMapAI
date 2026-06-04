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
\
\
\
\
\
\

import streamlit as st
from db.roadmaps import get_roadmap
from db.progress import get_progress, mark_subtopic_done, mark_subtopic_undone
from utils.helpers import (
    format_level, format_weeks, format_hours,
    pct_to_display, get_all_subtopic_ids, truncate_text
)

def render_roadmap() -> None:
\
\
\
\
\

    user_id = st.session_state.get("user_id")
    roadmap_id = st.session_state.get("current_roadmap_id")

    if not roadmap_id:
        st.error("No roadmap selected. Please go to your dashboard.")
        if st.button("← Dashboard"):
            st.session_state.current_page = "dashboard"
            st.rerun()
        return

    roadmap = _get_cached_roadmap(roadmap_id)
    if not roadmap:
        st.error("Roadmap not found. It may have been deleted.")
        if st.button("← Dashboard"):
            st.session_state.current_page = "dashboard"
            st.rerun()
        return

    progress = get_progress(user_id, roadmap_id)
    completed = set(progress.get("completed_subtopics", []))
    total_subtopics = len(get_all_subtopic_ids(roadmap))
    overall_pct = progress.get("overall_pct", 0.0)

    _render_header(roadmap, overall_pct, total_subtopics, len(completed))

    _render_summary_strip(roadmap)

    st.divider()

    topics = roadmap.get("topics", [])
    if not topics:
        st.warning("This roadmap has no content yet. Please try regenerating.")
        return

    for topic in topics:
        _render_topic(topic, completed, progress, user_id, roadmap_id, total_subtopics)

    st.divider()
    _render_final_quiz_cta(progress)

def _render_header(roadmap: dict, overall_pct: float, total: int, done: int) -> None:

    col_back, col_title, col_actions = st.columns([1, 4, 2])

    with col_back:
        if st.button("← Dashboard", use_container_width=True):
            st.session_state.current_page = "dashboard"
            st.rerun()

    with col_title:
        st.title(f"📋 {roadmap.get('skill', 'Roadmap')}")
        st.caption(
            f"{format_level(roadmap.get('level', 'beginner'))}  •  "
            f"{done}/{total} subtopics complete"
        )

    with col_actions:
        st.write("")
        if st.button("🚀 Projects", use_container_width=True):
            st.session_state.current_page = "projects"
            st.rerun()

    st.progress(overall_pct, text=f"Overall Progress: {pct_to_display(overall_pct)}")

def _render_summary_strip(roadmap: dict) -> None:

    timeline = roadmap.get("timeline") or {}
    budget = roadmap.get("budget") or {}

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("⏱️ Total Duration", format_weeks(timeline.get("total_weeks", 0)))
    c2.metric("📅 Hours/Week", f"{timeline.get('hours_per_week', 10)}h")
    c3.metric("💰 Free Path", budget.get("free_path_total", "$0"))
    c4.metric("💳 Paid Path", budget.get("paid_path_total", "~$30-60"))

def _render_topic(
    topic: dict,
    completed: set,
    progress: dict,
    user_id: str,
    roadmap_id: str,
    total_subtopics: int,
) -> None:
\
\
\
\
\

    subtopics = topic.get("subtopics", [])
    topic_done = sum(1 for s in subtopics if s.get("id") in completed)
    topic_total = len(subtopics)

    label = (
        f"{'✅' if topic_done == topic_total and topic_total > 0 else '📖'} "
        f"**{topic.get('name', 'Topic')}** "
        f"— {topic_done}/{topic_total} complete"
    )

    with st.expander(label, expanded=False):
        for subtopic in subtopics:
            _render_subtopic(
                subtopic, completed, progress,
                user_id, roadmap_id, total_subtopics
            )
            st.divider()

def _render_subtopic(
    subtopic: dict,
    completed: set,
    progress: dict,
    user_id: str,
    roadmap_id: str,
    total_subtopics: int,
) -> None:
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

    sub_id = subtopic.get("id", "")
    sub_name = subtopic.get("name", "Subtopic")
    is_done = sub_id in completed
    quiz_scores = progress.get("quiz_scores", {})
    quiz_score = quiz_scores.get(sub_id)

    check_col, name_col, quiz_col = st.columns([1, 7, 2])

    with check_col:

        checked = st.checkbox(
            f"Mark '{sub_name}' as complete",
            value=is_done,
            key=f"check_{sub_id}",
            label_visibility="collapsed",                                                          
        )

        if checked != is_done:
            if checked:
                mark_subtopic_done(user_id, roadmap_id, sub_id, total_subtopics)
            else:
                mark_subtopic_undone(user_id, roadmap_id, sub_id, total_subtopics)
            st.rerun()

    with name_col:
        st.markdown(
            f"{'~~' if is_done else ''}**{sub_name}**{'~~' if is_done else ''}  "
            f"⏱️ *{format_hours(subtopic.get('hours_estimate', 4))}*"
        )
        st.caption(truncate_text(subtopic.get("description", ""), 150))

    with quiz_col:

        if quiz_score:
            score = quiz_score.get("score", 0)
            total = quiz_score.get("total", 5)
            passed = quiz_score.get("passed", False)
            badge = "✅" if passed else "❌"
            st.markdown(f"{badge} Quiz: {score}/{total}")
        if st.button("❓ Quiz", key=f"quiz_{sub_id}", use_container_width=True):
            st.session_state.current_subtopic_id = sub_id
            st.session_state.current_subtopic_name = sub_name
            st.session_state.current_page = "quiz"
            st.rerun()

    tab_videos, tab_text, tab_courses, tab_projects = st.tabs(
        ["📹 Videos", "📚 Text Resource", "🎓 Courses", "🔨 Projects"]
    )

    with tab_videos:
        _render_videos(subtopic.get("videos", []))

    with tab_text:
        _render_text_resource(subtopic.get("text_resource", {}))

    with tab_courses:
        _render_courses(
            subtopic.get("free_course", {}),
            subtopic.get("paid_course", {}),
        )

    with tab_projects:
        _render_projects(
            subtopic.get("mini_project", {}),
            subtopic.get("capstone_project", {}),
        )

def _render_videos(videos: list) -> None:

    if not videos:
        st.caption("No videos found. Search YouTube directly.")
        return

    for v in videos:
        url = v.get("url", "")
        title = v.get("title", "Watch")
        channel = v.get("channel", "")
        vtype = v.get("type", "video")
        icon = "▶️" if vtype == "video" else "📋"

        st.markdown(
            f"{icon} **[{title}]({url})**"
            + (f"  •  *{channel}*" if channel else "")
        )

def _render_text_resource(resource: dict) -> None:

    if not resource or not resource.get("url"):
        st.caption("No text resource found.")
        return

    title = resource.get("title", "Read")
    url = resource.get("url", "")
    rtype = resource.get("type", "article").capitalize()

    st.markdown(f"📄 **{rtype}:** [{title}]({url})")

def _render_courses(free: dict, paid: dict) -> None:

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**🎓 Free Course**")
        if free and free.get("url"):
            cert = "✅ Free certificate" if free.get("certificate") else "No certificate"
            st.markdown(
                f"[{free.get('name', 'Free Course')}]({free.get('url')})"
                f"  •  *{free.get('platform', '')}*"
            )
            st.caption(cert)
        else:
            st.caption("No free course found.")

    with c2:
        st.markdown("**💳 Paid Course**")
        if paid and paid.get("url"):
            price = paid.get("price", "")
            rating = paid.get("rating", "")
            meta = "  •  ".join(filter(None, [price, f"⭐ {rating}" if rating else ""]))
            st.markdown(
                f"[{paid.get('name', 'Paid Course')}]({paid.get('url')})"
                f"  •  *{paid.get('platform', '')}*"
            )
            if meta:
                st.caption(meta)
        else:
            st.caption("No paid course found.")

def _render_projects(mini: dict, capstone: dict) -> None:

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**🔨 Mini Project**")
        if mini and mini.get("title"):
            st.markdown(f"**{mini.get('title')}**")
            st.caption(mini.get("use_case", ""))
            vid_url = mini.get("tutorial_video_url", "")
            if vid_url:
                st.markdown(f"[▶️ Tutorial]({vid_url})")
        else:
            st.caption("No mini project designed.")

    with c2:
        st.markdown("**🏗️ Capstone Project**")
        if capstone and capstone.get("title"):
            st.markdown(f"**{capstone.get('title')}**")
            st.caption(truncate_text(capstone.get("description", ""), 120))
        else:
            st.caption("No capstone project designed.")

def _render_final_quiz_cta(progress: dict) -> None:

    final_score = progress.get("final_quiz_score")
    final_total = progress.get("final_quiz_total")
    final_passed = progress.get("final_quiz_passed")

    st.subheader("🎓 Final Quiz")

    if final_score is not None:
        badge = "✅ Passed" if final_passed else "❌ Failed"
        st.markdown(
            f"{badge} — Score: **{final_score}/{final_total}**"
        )
        if st.button("🔄 Retake Final Quiz", use_container_width=False):
            st.session_state.current_subtopic_id = "final"
            st.session_state.current_subtopic_name = "Final Quiz"
            st.session_state.current_page = "quiz"
            st.rerun()
    else:
        st.markdown(
            "Test your knowledge of the entire roadmap with a "
            "comprehensive 10-question final quiz."
        )
        if st.button(
            "🎓 Take Final Quiz",
            type="primary",
            use_container_width=False,
        ):
            st.session_state.current_subtopic_id = "final"
            st.session_state.current_subtopic_name = "Final Quiz"
            st.session_state.current_page = "quiz"
            st.rerun()

def _get_cached_roadmap(roadmap_id: str) -> dict | None:
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
\
\
\

    cached = st.session_state.get("current_roadmap")

    if cached and cached.get("_id") == roadmap_id:
        return cached

    st.session_state.pop("current_roadmap", None)

    roadmap = get_roadmap(roadmap_id)
    if roadmap:
        st.session_state.current_roadmap = roadmap

    return roadmap
