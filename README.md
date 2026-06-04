# 🗺️ SkillMap AI

> Generate a complete, personalised learning roadmap for any skill in minutes.

SkillMap AI takes a skill or job role (e.g. *"React Developer"*, *"Machine Learning Engineer"*) and uses a multi-agent AI system to produce a fully structured learning plan — complete with curated resources, projects, and quizzes for every subtopic.

**[Live Demo →](https://your-app.streamlit.app)**

---

## What it generates

For every subtopic in your roadmap:

| Resource | Details |
|---|---|
| 📹 YouTube Videos | Best tutorial video + full course playlist |
| 📚 Text Resource | Official docs, guides, authoritative tutorials |
| 🎓 Free Course | Certificate courses on Coursera, edX, freeCodeCamp |
| 💳 Paid Course | Top-rated Udemy course with real price |
| 🔨 Mini Project | 1–3 hour hands-on project with real-world use case |
| 🏗️ Capstone Project | Half-day project linking subtopic skills |
| ❓ Quiz | 5 interview-ready questions (MCQ + open-ended) |

For the full roadmap:

- 🚀 **Major portfolio project** — resume-worthy, with tech stack and GitHub structure
- 🗓️ **Realistic timeline** — weekly schedule based on your level
- 💰 **Budget breakdown** — free path ($0) and paid path with itemised costs
- 🎓 **Final quiz** — 10 comprehensive questions across the whole roadmap

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| AI Orchestration | CrewAI Flows |
| LLM (reasoning) | Claude Sonnet 4.5 — roadmap structure, projects |
| LLM (mechanical) | Claude Haiku 4.5 — quizzes, timeline, assembly |
| Video Search | YouTube Data API v3 |
| Web Search | Tavily Search API |
| Database | MongoDB Atlas |
| Auth | bcrypt (custom) |
| Deployment | Streamlit Cloud |

---

## Architecture

```
Stage 1 — Architect Agent (Claude Sonnet)
    └── Builds topic tree: 5-8 topics × 2-5 subtopics

Stage 2 — Parallel Workers
    ├── Video Hunter     → YouTube API per subtopic
    ├── Course Curator   → Tavily search per subtopic
    ├── Project Designer → LLM per topic batch
    ├── Quiz Generator   → LLM per topic batch
    └── Timeline/Budget  → LLM single call

Stage 3 — Python Assembler
    └── Merges all data → Pydantic validation → MongoDB
```

---

## Getting Started

### Prerequisites

- Python 3.12
- API keys for: Anthropic, YouTube Data API v3, Tavily, MongoDB Atlas

### Local Setup

```bash
git clone https://github.com/YOUR_USERNAME/skillmap-ai.git
cd skillmap-ai

py -3.12 -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

pip install -r requirements.txt

cp .env.example .env
# Fill in your API keys in .env

streamlit run app.py
```

### Environment Variables

```env
ANTHROPIC_API_KEY=sk-ant-...
YOUTUBE_API_KEY=AIza...
TAVILY_API_KEY=tvly-...
MONGODB_URI=mongodb+srv://...
CREWAI_TRACING_ENABLED=false
```

> Get keys: [Anthropic](https://console.anthropic.com) · [Google Cloud](https://console.cloud.google.com) · [Tavily](https://tavily.com) · [MongoDB Atlas](https://cloud.mongodb.com)

---

## Deploy to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Select this repo, branch `main`, file `app.py`
4. Add your API keys under **Advanced settings → Secrets**
5. Click **Deploy**

---

## Features

- 🔐 **Auth** — Register / login with bcrypt-hashed passwords
- 📋 **Dashboard** — All your roadmaps with progress bars
- ✅ **Progress tracking** — Check off subtopics, scores saved per quiz
- 💾 **Persistent** — All data stored in MongoDB, survives page refreshes
- 📱 **Responsive** — Works on desktop and tablet

---

## License

MIT
