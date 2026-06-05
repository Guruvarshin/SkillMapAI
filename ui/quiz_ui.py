import streamlit as st
from db.quizzes import get_quiz, get_final_quiz
from db.progress import save_quiz_score, save_final_quiz_score, get_progress


def render_quiz() -> None:

    roadmap_id = st.session_state.get("current_roadmap_id")
    subtopic_id = st.session_state.get("current_subtopic_id", "")
    subtopic_name = st.session_state.get("current_subtopic_name", "Quiz")
    user_id = st.session_state.get("user_id")

    if not roadmap_id:
        st.error("No roadmap selected.")
        _back_button()
        return

    col_back, col_title = st.columns([1, 5])
    with col_back:
        _back_button()
    with col_title:
        if subtopic_id == "final":
            st.title("🎓 Final Quiz")
            st.caption("Comprehensive quiz covering the entire roadmap,10 questions")
        else:
            st.title(f"❓ {subtopic_name}")
            st.caption("5 questions,3 MCQ (auto-scored) + 2 open-ended (self-assessed)")

    st.divider()

    if subtopic_id == "final":
        questions = get_final_quiz(roadmap_id)
    else:
        questions = get_quiz(roadmap_id, subtopic_id)

    if not questions:
        st.warning(
            "No quiz questions found for this subtopic. "
            "This can happen if the quiz generator failed during roadmap generation."
        )
        return

    progress = get_progress(user_id, roadmap_id)
    if subtopic_id == "final":
        prior_score = progress.get("final_quiz_score")
    else:
        prior_score = progress.get("quiz_scores", {}).get(subtopic_id)

    if prior_score is not None:
        _render_prior_result(prior_score, subtopic_id, questions)
        st.divider()
        if not st.session_state.get(f"retake_{subtopic_id}", False):
            if st.button("🔄 Retake Quiz", type="secondary"):
                st.session_state[f"retake_{subtopic_id}"] = True
                st.rerun()
            return

    _render_quiz_form(questions, subtopic_id, roadmap_id, user_id)


def _render_quiz_form(
    questions: list,
    subtopic_id: str,
    roadmap_id: str,
    user_id: str,
) -> None:

    mcq_questions = [q for q in questions if q.get("type") == "mcq"]
    open_questions = [q for q in questions if q.get("type") != "mcq"]

    user_answers = {}

    with st.form(f"quiz_form_{subtopic_id}"):

        if mcq_questions:
            st.subheader(f"Multiple Choice ({len(mcq_questions)} questions)")
            for i, q in enumerate(mcq_questions):
                st.markdown(f"**Q{i + 1}. {q.get('question', '')}**")
                options = q.get("options", [])
                letters = ["a", "b", "c", "d"]

                display_options = [
                    f"{letters[j].upper()}. {opt}"
                    for j, opt in enumerate(options)
                    if j < len(letters)
                ]

                chosen = st.radio(
                    f"q_{i}",
                    options=display_options,
                    index=None,
                    key=f"{subtopic_id}_mcq_{i}",
                    label_visibility="collapsed",
                )
                user_answers[i] = chosen
                st.markdown("")

        if open_questions:
            st.subheader(f"Open-Ended ({len(open_questions)} questions)")
            st.caption("Write your answer, then reveal the model answer to self-assess.")
            for i, q in enumerate(open_questions):
                st.markdown(f"**Q{len(mcq_questions) + i + 1}. {q.get('question', '')}**")
                st.text_area(
                    "Your answer",
                    key=f"{subtopic_id}_open_{i}",
                    placeholder="Type your answer here...",
                    height=100,
                    label_visibility="collapsed",
                )
                st.markdown("")

        submitted = st.form_submit_button(
            "✅ Submit Quiz",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        _score_and_save(
            mcq_questions=mcq_questions,
            open_questions=open_questions,
            user_answers=user_answers,
            subtopic_id=subtopic_id,
            roadmap_id=roadmap_id,
            user_id=user_id,
        )


def _score_and_save(
    mcq_questions: list,
    open_questions: list,
    user_answers: dict,
    subtopic_id: str,
    roadmap_id: str,
    user_id: str,
) -> None:

    score = 0
    total_mcq = len(mcq_questions)
    letters = ["a", "b", "c", "d"]

    st.subheader("📊 Results")

    if mcq_questions:
        st.markdown("**Multiple Choice:**")
        for i, q in enumerate(mcq_questions):
            correct_letter = q.get("answer", "").lower().strip()
            chosen = user_answers.get(i)

            if chosen:

                chosen_letter = chosen[0].lower()
                is_correct = chosen_letter == correct_letter
            else:
                chosen_letter = None
                is_correct = False

            if is_correct:
                score += 1
                st.markdown(f"✅ **Q{i + 1}:** {q.get('question', '')}")
            else:
                correct_idx = letters.index(correct_letter) if correct_letter in letters else 0
                correct_text = q.get("options", [""])[correct_idx] if q.get("options") else ""
                chosen_text = chosen or "Not answered"
                st.markdown(f"❌ **Q{i + 1}:** {q.get('question', '')}")
                col1, col2 = st.columns(2)
                col1.caption(f"Your answer: {chosen_text}")
                col2.caption(f"✅ Correct: {correct_letter.upper()}. {correct_text}")

        pct = (score / total_mcq * 100) if total_mcq > 0 else 0
        passed = pct >= 70
        badge = "🎉 Passed!" if passed else "📚 Keep studying"
        st.metric(
            "Score",
            f"{score}/{total_mcq}",
            delta=f"{pct:.0f}%,{badge}",
            delta_color="normal" if passed else "inverse",
        )

    if open_questions:
        st.markdown("---")
        st.markdown("**Open-Ended,Model Answers:**")
        for i, q in enumerate(open_questions):
            st.markdown(f"**Q{total_mcq + i + 1}:** {q.get('question', '')}")
            with st.expander("💡 Show model answer"):
                st.info(q.get("answer", "No model answer available."))

    try:
        if subtopic_id == "final":
            save_final_quiz_score(user_id, roadmap_id, score, total_mcq)
        else:
            save_quiz_score(user_id, roadmap_id, subtopic_id, score, total_mcq)
        st.success("Quiz score saved! ✅")
    except Exception as e:
        st.warning(f"Could not save score: {e}")

    st.session_state.pop(f"retake_{subtopic_id}", None)


def _render_prior_result(prior_score, subtopic_id: str, questions: list) -> None:

    if isinstance(prior_score, dict):
        score = prior_score.get("score", 0)
        total = prior_score.get("total", len(questions))
        passed = prior_score.get("passed", False)
    else:
        score = prior_score
        total = len(questions)
        passed = (score / total >= 0.7) if total > 0 else False

    badge = "🎉 Passed" if passed else "📚 Not passed"
    st.info(f"**Previous score:** {score}/{total},{badge}")


def _back_button() -> None:

    if st.button("← Back to Roadmap", use_container_width=True):
        st.session_state.current_page = "roadmap"
        st.rerun()
