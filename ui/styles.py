import streamlit as st

def inject_css():
    st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.main .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1200px; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0D1117 0%, #111827 100%) !important; border-right: 1px solid #1F2937 !important; }
[data-testid="stSidebar"] .stButton button { background: transparent !important; border: 1px solid #1F2937 !important; color: #9CA3AF !important; border-radius: 8px !important; text-align: left !important; transition: all 0.2s ease !important; font-size: 0.875rem !important; }
[data-testid="stSidebar"] .stButton button:hover { background: #1F2937 !important; border-color: #8B5CF6 !important; color: #F9FAFB !important; transform: translateX(4px) !important; }
[data-testid="stSidebar"] .stButton button[kind="primary"] { background: linear-gradient(135deg, #7C3AED, #8B5CF6) !important; border-color: #8B5CF6 !important; color: #fff !important; }
.stButton button[kind="primary"] { background: linear-gradient(135deg, #7C3AED 0%, #8B5CF6 50%, #06B6D4 100%) !important; border: none !important; border-radius: 10px !important; color: white !important; font-weight: 600 !important; transition: all 0.3s ease !important; box-shadow: 0 4px 15px rgba(139,92,246,0.35) !important; }
.stButton button[kind="primary"]:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 25px rgba(139,92,246,0.5) !important; }
.stButton button[kind="secondary"] { background: #1F2937 !important; border: 1px solid #374151 !important; border-radius: 10px !important; color: #D1D5DB !important; font-weight: 500 !important; transition: all 0.2s ease !important; }
.stButton button[kind="secondary"]:hover { background: #374151 !important; border-color: #8B5CF6 !important; color: #F9FAFB !important; }
div[data-testid="stVerticalBlockBorderWrapper"] { background: #111827 !important; border: 1px solid #1F2937 !important; border-radius: 16px !important; transition: all 0.3s ease !important; box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important; }
div[data-testid="stVerticalBlockBorderWrapper"]:hover { border-color: #374151 !important; box-shadow: 0 8px 30px rgba(0,0,0,0.5), 0 0 0 1px rgba(139,92,246,0.2) !important; transform: translateY(-2px) !important; }
.stTextInput input, .stTextArea textarea { background: #1F2937 !important; border: 1px solid #374151 !important; border-radius: 10px !important; color: #F9FAFB !important; }
.stTextInput input:focus, .stTextArea textarea:focus { border-color: #8B5CF6 !important; box-shadow: 0 0 0 3px rgba(139,92,246,0.15) !important; }
.stProgress > div > div > div > div { background: linear-gradient(90deg, #7C3AED, #8B5CF6, #06B6D4) !important; border-radius: 99px !important; }
.stProgress > div > div > div { background: #1F2937 !important; border-radius: 99px !important; }
[data-testid="stExpander"] { background: #111827 !important; border: 1px solid #1F2937 !important; border-radius: 12px !important; margin-bottom: 8px !important; }
[data-testid="stExpander"]:hover { border-color: #374151 !important; }
[data-testid="stExpander"] summary { background: #111827 !important; border-radius: 12px !important; padding: 1rem !important; font-weight: 600 !important; }
.stTabs [data-baseweb="tab-list"] { background: #111827 !important; border-radius: 10px !important; padding: 4px !important; gap: 4px !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; border-radius: 8px !important; color: #9CA3AF !important; font-weight: 500 !important; transition: all 0.2s !important; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, #7C3AED, #8B5CF6) !important; color: white !important; }
[data-testid="stMetric"] { background: #111827 !important; border: 1px solid #1F2937 !important; border-radius: 12px !important; padding: 1rem !important; }
[data-testid="stMetricValue"] { color: #F9FAFB !important; font-weight: 700 !important; }
hr { border-color: #1F2937 !important; margin: 1.5rem 0 !important; }
[data-testid="stStatus"] { background: #111827 !important; border: 1px solid #1F2937 !important; border-radius: 12px !important; }
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #111827; }
::-webkit-scrollbar-thumb { background: #374151; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #8B5CF6; }

.gradient-text { background: linear-gradient(135deg, #8B5CF6, #06B6D4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-weight: 800; }
.hero-badge { display: inline-block; background: linear-gradient(135deg, rgba(124,58,237,0.2), rgba(6,182,212,0.2)); border: 1px solid rgba(139,92,246,0.3); border-radius: 99px; padding: 6px 16px; font-size: 0.8rem; font-weight: 600; color: #A78BFA; letter-spacing: 0.5px; text-transform: uppercase; }
.sidebar-logo { font-size: 1.4rem; font-weight: 800; background: linear-gradient(135deg, #8B5CF6, #06B6D4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.stat-card { background: #111827; border: 1px solid #1F2937; border-radius: 16px; padding: 1.5rem; text-align: center; transition: all 0.3s ease; }
.stat-card:hover { border-color: #8B5CF6; transform: translateY(-3px); box-shadow: 0 10px 30px rgba(139,92,246,0.2); }
.stat-number { font-size: 2.5rem; font-weight: 800; background: linear-gradient(135deg, #8B5CF6, #06B6D4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.stat-label { color: #6B7280; font-size: 0.875rem; font-weight: 500; margin-top: 4px; }
.roadmap-card { background: #111827; border: 1px solid #1F2937; border-radius: 20px; padding: 1.5rem; transition: all 0.3s ease; position: relative; overflow: hidden; }
.roadmap-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, #7C3AED, #8B5CF6, #06B6D4); }
.roadmap-card:hover { border-color: #374151; transform: translateY(-4px); box-shadow: 0 20px 40px rgba(0,0,0,0.4), 0 0 0 1px rgba(139,92,246,0.2); }
.roadmap-title { font-size: 1.2rem; font-weight: 700; color: #F9FAFB; margin-bottom: 6px; }
.level-badge { display: inline-flex; align-items: center; gap: 5px; padding: 3px 10px; border-radius: 99px; font-size: 0.72rem; font-weight: 600; }
.level-beginner { background: rgba(16,185,129,0.15); color: #10B981; border: 1px solid rgba(16,185,129,0.3); }
.level-intermediate { background: rgba(245,158,11,0.15); color: #F59E0B; border: 1px solid rgba(245,158,11,0.3); }
.level-advanced { background: rgba(239,68,68,0.15); color: #EF4444; border: 1px solid rgba(239,68,68,0.3); }
.generating-pill { display: inline-flex; align-items: center; gap: 6px; background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.3); border-radius: 99px; padding: 4px 12px; font-size: 0.75rem; font-weight: 600; color: #F59E0B; animation: pulse 2s infinite; }
.done-pill { display: inline-flex; align-items: center; gap: 6px; background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3); border-radius: 99px; padding: 4px 12px; font-size: 0.75rem; font-weight: 600; color: #10B981; }
.failed-pill { display: inline-flex; align-items: center; gap: 6px; background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); border-radius: 99px; padding: 4px 12px; font-size: 0.75rem; font-weight: 600; color: #EF4444; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.6; } }
.tech-chip { display: inline-block; background: #1F2937; border: 1px solid #374151; border-radius: 6px; padding: 3px 10px; font-size: 0.75rem; font-weight: 500; color: #A78BFA; margin: 2px; }
.feature-item { display: flex; align-items: flex-start; gap: 8px; padding: 5px 0; color: #D1D5DB; font-size: 0.875rem; }
.feature-dot { width: 6px; height: 6px; border-radius: 50%; background: linear-gradient(135deg, #8B5CF6, #06B6D4); margin-top: 7px; flex-shrink: 0; }
.empty-state { text-align: center; padding: 60px 20px; }
.empty-icon { font-size: 4rem; margin-bottom: 1rem; }
.empty-title { font-size: 1.4rem; font-weight: 700; color: #9CA3AF; margin-bottom: 8px; }
.empty-desc { font-size: 0.9rem; color: #6B7280; max-width: 400px; margin: 0 auto 1.5rem; }
.score-card { background: #111827; border-radius: 16px; padding: 2rem; text-align: center; border: 1px solid #1F2937; }
.score-number { font-size: 3.5rem; font-weight: 800; }
.score-pass { color: #10B981; }
.score-fail { color: #EF4444; }
.timeline-row { display: flex; align-items: center; padding: 10px 14px; background: #1F2937; border-radius: 10px; margin-bottom: 6px; font-size: 0.875rem; }
.timeline-topic { flex: 1; color: #D1D5DB; font-weight: 500; }
.timeline-hours { color: #8B5CF6; font-weight: 700; }
.roadmap-header { background: linear-gradient(135deg, #111827 0%, #1F2937 100%); border: 1px solid #1F2937; border-radius: 20px; padding: 2rem; margin-bottom: 1.5rem; position: relative; overflow: hidden; }
.roadmap-header::after { content: ''; position: absolute; top: -50%; right: -10%; width: 300px; height: 300px; background: radial-gradient(circle, rgba(139,92,246,0.08) 0%, transparent 70%); pointer-events: none; }
.resource-row { display: flex; align-items: center; gap: 10px; padding: 10px 14px; background: #1F2937; border: 1px solid #374151; border-radius: 10px; margin-bottom: 6px; font-size: 0.875rem; color: #D1D5DB; }
.badge-mini { background: rgba(6,182,212,0.15); color: #06B6D4; border: 1px solid rgba(6,182,212,0.3); border-radius: 99px; padding: 2px 8px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
.badge-capstone { background: rgba(139,92,246,0.15); color: #A78BFA; border: 1px solid rgba(139,92,246,0.3); border-radius: 99px; padding: 2px 8px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
.badge-major { background: rgba(245,158,11,0.15); color: #FCD34D; border: 1px solid rgba(245,158,11,0.3); border-radius: 99px; padding: 2px 8px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
</style>
""", unsafe_allow_html=True)
