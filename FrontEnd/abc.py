import streamlit as st
import sqlite3
import base64
import os
import requests  
import markdown 
import json
import re
import streamlit.components.v1 as components

# Backend URL pointing to your running FastAPI server
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Readora AI", page_icon="📚", layout="wide", initial_sidebar_state="expanded")

def get_image_base64(img_path):
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "logo readora ai.jpeg")
logo_b64 = get_image_base64(logo_path)

logo_src = f"data:image/jpeg;base64,{logo_b64}" if logo_b64 else "https://via.placeholder.com/45"

conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS documents (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, doc_name TEXT, original_text TEXT, simplified_text TEXT)')
conn.commit()

# Session state initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = ""
if 'simplified_text' not in st.session_state:
    st.session_state.simplified_text = ""
if 'vocabulary' not in st.session_state:            
    st.session_state.vocabulary = ""
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'current_doc_id' not in st.session_state:
    st.session_state.current_doc_id = None
if 'profile_photo' not in st.session_state:
    st.session_state.profile_photo = None
if 'font_size' not in st.session_state:
    st.session_state.font_size = 22
if 'line_spacing' not in st.session_state:
    st.session_state.line_spacing = 1.8

# --- DESIGN TOKENS ---------------------------------------------------------
# Original dark UI palette: near-black background with cyan/mint accents.
bg_color = "#0E1117"        # app background
text_color = "#E0E0E0"      # UI text
card_color = "#1A1C23"      # panel surface
cyan_color = "#00E5FF"      # primary accent
accent_color = "#69F0AE"    # secondary accent
border_color = "#2D303E"

# Paper tokens — used anywhere the user is actually *reading*, so the
# product's core transformation (dense text -> calm text) is visible in
# the UI itself, not just described by it.
paper_bg = "#B3E4CC"      # warm cream page
paper_ink = "#2A241C"       # ink on paper
paper_border = "#E4D8B8"    # page edge
paper_accent = "#00E5FF"    # terracotta — emphasis on paper (contrast-safe)

dynamic_css = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Figtree:wght@400;500;600;700&display=swap');

/* Clean minimal hiding, leaves the sidebar toggle completely untouched */
#MainMenu {{visibility: hidden !important;}}
footer {{visibility: hidden !important;}}

/* --- ENABLE SMOOTH SCROLLING FOR STREAMLIT CONTAINERS --- */
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMainContainer"], [data-testid="stMain"] {{
    scroll-behavior: smooth !important;
}}

@font-face {{
    font-family: 'OpenDyslexic';
    src: url('https://cdn.jsdelivr.net/gh/antijingoist/opendyslexic@master/compiled/OpenDyslexic-Regular.otf') format('opentype');
    font-weight: normal;
    font-style: normal;
}}

.stApp {{ background-color: {bg_color}; }}

/* --- TYPOGRAPHY: serif display paired with a humanist sans body --- */
html, body, [class*="css"], p, li, label, .stMarkdown {{
    font-family: 'Figtree', 'Segoe UI', sans-serif !important;
    color: {text_color} !important;
}}
h1, h2, h3, h4, h5, h6, .nav-title, .hero-text-light, .hero-text-cyan {{
    font-family: 'Fraunces', Georgia, serif !important;
    font-weight: 700 !important;
    color: {text_color} !important;
}}

/* --- UPGRADED ACCESSIBILITY TWEAKS --- */
[data-testid="stUploadedFile"] {{ border: 1px solid #5A5E73 !important; border-radius: 8px !important; background-color: #222530 !important; }}
[data-testid="stAlert"] {{ background-color: rgba(105, 240, 174, 0.15) !important; border: 1px solid {accent_color} !important; color: #FFFFFF !important; }}

/* --- DASHBOARD CARD CONTAINERS --- */
.dashboard-card {{
    background: rgba(30, 28, 41, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.08);
    padding: 24px;
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    margin-bottom: 25px;
}}

/* --- FILE UPLOADER REFINEMENT --- */
[data-testid="stFileUploader"] {{
    background: rgba(14, 17, 23, 0.9);
    border: 1px dashed rgba(0, 229, 255, 0.4) !important;
    border-radius: 12px;
    padding: 10px;
}}

/* --- TABS POLISH --- */
.stTabs [data-baseweb="tab-list"] {{ gap: 8px; background-color: transparent; }}
.stTabs [data-baseweb="tab"] {{ background-color: rgba(30, 28, 41, 0.7); border-radius: 8px 8px 0 0; color: #8b949e; padding: 10px 20px; border: 1px solid {border_color}; }}
.stTabs [aria-selected="true"] {{ background-color: rgba(0, 229, 255, 0.12) !important; color: {cyan_color} !important; border-color: rgba(0, 229, 255, 0.4) !important; }}

/* --- READING PANE: a warm page, not another dark card --- */
.reading-pane {{
    position: relative;
    background-color: {paper_bg};
    padding: 40px 60px;
    border-radius: 6px 12px 12px 6px;
    box-shadow: 0 14px 34px rgba(0,0,0,0.35), inset 0 0 0 1px {paper_border};
    border: 1px solid {paper_border};
    transition: all 0.3s ease;
}}
/* folded page corner — the recurring visual signature of "this is a page you can actually read" */
.reading-pane::after {{
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 0; height: 0;
    border-style: solid;
    border-width: 0 26px 26px 0;
    border-color: transparent #DCCEA4 transparent transparent;
    filter: drop-shadow(-2px 2px 3px rgba(0,0,0,0.18));
    border-top-right-radius: 6px;
}}
.reading-pane, .reading-pane p, .reading-pane li, .reading-pane div, .reading-pane span, .reading-pane h1, .reading-pane h2, .reading-pane h3 {{
    font-family: 'OpenDyslexic', sans-serif !important;
    letter-spacing: normal !important; 
    color: {paper_ink} !important;
}}
.reading-pane strong, .reading-pane b {{ font-family: 'OpenDyslexic', sans-serif !important; font-weight: 700 !important; color: {paper_accent} !important; }}
.reading-pane h1, .reading-pane h2, .reading-pane h3 {{ margin-bottom: 20px !important; border-bottom: 1px solid {paper_border}; padding-bottom: 10px; }}
.reading-container {{ max-width: 900px; margin: 0 auto; }}
.badge {{ background-color: {border_color}; color: {cyan_color}; padding: 4px 12px; border-radius: 15px; font-size: 0.8rem; font-weight: 600; letter-spacing: 0.03em; margin-bottom: 15px; display: inline-block; font-family: 'Figtree', sans-serif !important; }}

/* --- CUSTOM TOP NAVBAR (legacy / unused variant, kept in sync) --- */
.custom-navbar {{
    position: fixed; top: 0; left: 0; width: 100%; background-color: rgba(19, 18, 26, 0.85); backdrop-filter: blur(10px);
    display: flex; justify-content: space-between; align-items: center; padding: 10px 50px; z-index: 99999; border-bottom: 1px solid {border_color};
}}
.nav-left {{ display: flex; align-items: center; gap: 12px; }}
.nav-logo {{ width: 36px; height: 36px; border-radius: 50%; object-fit: cover; border: 2px solid {cyan_color}; }}
.nav-title {{ font-size: 1.2rem; font-weight: bold; color: {text_color}; letter-spacing: 1px; }}
.nav-login-btn {{
    background-color: transparent; color: {text_color}; border: 1px solid {cyan_color};
    padding: 6px 20px; border-radius: 25px; text-decoration: none !important; font-weight: bold; transition: all 0.3s ease;
}}
.nav-login-btn:hover {{ background-color: {cyan_color}; color: #0E1117; box-shadow: 0 0 15px rgba(0, 229, 255, 0.4); }}

/* --- PRIMARY BUTTON STYLING --- */
button[kind="primary"] {{
    background-color: {cyan_color} !important;
    border: none !important;
    font-weight: 600 !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}}
button[kind="primary"] * {{ color: #0E1117 !important; }}
button[kind="primary"]:hover {{
    background-color: {accent_color} !important; transform: translateY(-3px); box-shadow: 0 6px 15px rgba(0, 229, 255, 0.25);
}}

/* --- GEMINI STYLE SIDEBAR UI --- */
[data-testid="collapsedControl"] svg {{
    display: none !important;
}}
[data-testid="collapsedControl"] {{
    background-image: url('{logo_src}');
    background-size: cover;
    background-position: center;
    border-radius: 50%;
    width: 36px !important;
    height: 36px !important;
    border: 2px solid {cyan_color};
    margin-top: 10px;
    margin-left: 15px;
    transition: transform 0.2s ease;
    z-index: 999999 !important;
}}
[data-testid="collapsedControl"]:hover {{
    transform: scale(1.1);
}}
[data-testid="stSidebar"] {{ background-color: #13151C !important; border-right: 1px solid {border_color}; }}
[data-testid="stSidebar"] button[kind="secondary"] {{
    background-color: transparent !important; border: none !important; justify-content: flex-start !important; 
    padding: 8px 10px !important; box-shadow: none !important;
}}
[data-testid="stSidebar"] button[kind="secondary"]:hover {{ background-color: #1E212B !important; }}
[data-testid="stSidebar"] button[kind="secondary"] p {{ color: {text_color} !important; font-size: 14.5px !important; }}

/* --- LANDING PAGE ANIMATIONS --- */
@keyframes fadeUp {{ 0% {{ opacity: 0; transform: translateY(20px); }} 100% {{ opacity: 1; transform: translateY(0); }} }}
.hero-wrapper {{ padding: 3rem 0 2rem 0; margin-top: 60px; text-align: center; animation: fadeUp 1s ease-out; position: relative; overflow: hidden; }}
.hero-wrapper::before, .hero-wrapper::after {{
    content: ''; position: absolute; width: 250px; height: 250px;
    background: radial-gradient(circle, rgba(0,229,255,0.07) 0%, transparent 60%); border-radius: 50%;
    animation: floatShape 12s infinite alternate ease-in-out; z-index: 0;
}}
.hero-wrapper::before {{ top: -10%; left: 15%; }}
.hero-wrapper::after {{ bottom: -10%; right: 15%; background: radial-gradient(circle, rgba(105,240,174,0.06) 0%, transparent 60%); animation-duration: 15s; animation-direction: alternate-reverse; }}
@keyframes floatShape {{ 0% {{ transform: translate(0, 0) scale(1); }} 100% {{ transform: translate(40px, -60px) scale(1.3); }} }}
.hero-text-light {{ position: relative; z-index: 1; font-size: 3.4rem; font-weight: 600; color: {text_color} !important; line-height: 1.25; }}
.hero-text-cyan {{ position: relative; z-index: 1; font-size: 4rem; font-weight: 700; color: {cyan_color} !important; line-height: 1.15; font-style: italic; }}
.text-accent {{ color: {accent_color} !important; font-style: italic; }}
.standard-pane {{ background-color: {card_color}; padding: 30px; border-radius: 12px; border: 1px solid {border_color}; }}
.standard-pane, .standard-pane p, .standard-pane strong, .standard-pane div {{ font-family: 'Arial', sans-serif !important; font-size: 1rem !important; color: #8b949e !important; }}
.mega-footer {{
    display: flex; justify-content: space-around; background-color: {card_color}; padding: 40px 20px; border-top: 1px solid {border_color};
    margin-top: 60px; border-radius: 12px;
}}
.footer-col {{ display: flex; flex-direction: column; text-align: left; }}
.footer-col h4 {{ color: #FFFFFF !important; font-size: 1.05rem; margin-bottom: 15px; font-weight: 600; font-family: 'Figtree', sans-serif !important;}}
.footer-col a {{ color: #9AA0A6 !important; text-decoration: none; font-size: 0.9rem; margin-bottom: 10px; transition: color 0.2s, transform 0.2s; }}
.footer-col a:hover {{ color: {cyan_color} !important; transform: translateX(5px); }}

/* --- HERO: asymmetric split, not a centered stack --- */
.hero-eyebrow {{
    font-family: 'Figtree', sans-serif; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.14em;
    text-transform: uppercase; color: {accent_color}; margin-bottom: 14px;
}}
.hero-copy h1 {{
    font-family: 'Fraunces', Georgia, serif !important; font-size: 3.1rem; line-height: 1.12;
    font-weight: 600 !important; margin: 0 0 18px 0 !important; color: {text_color} !important; text-align: left;
}}
.hero-copy h1 em {{ font-style: italic; color: {cyan_color}; font-weight: 700; }}
.hero-copy p {{ font-size: 1.08rem; color: #9AA0A6 !important; max-width: 460px; margin-bottom: 28px !important; text-align: left; }}
.cta-btn {{
    display: inline-block; background-color: {cyan_color}; color: #0E1117 !important; text-decoration: none !important;
    font-family: 'Figtree', sans-serif; font-weight: 700; font-size: 1rem; padding: 13px 28px; border-radius: 8px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}}
.cta-btn:hover {{ transform: translateY(-3px); box-shadow: 0 8px 20px rgba(0,229,255,0.3); }}
.cta-sub {{ font-size: 0.82rem; color: #6D6558; margin-top: 10px; }}

/* --- SIGNATURE: overlapping page-stack showing the actual transformation --- */
.stack-wrap {{ position: relative; height: 400px; }}
.stack-back {{
    position: absolute; top: 10px; left: 30px; width: 78%; padding: 26px 30px; border-radius: 10px;
    background-color: {card_color}; border: 1px solid {border_color}; transform: rotate(-7deg);
    box-shadow: 0 12px 24px rgba(0,0,0,0.35); opacity: 0.7;
}}
.stack-back p {{ font-family: 'Arial', sans-serif !important; font-size: 0.82rem !important; line-height: 1.6 !important; color: #857D6E !important; margin: 0 !important; }}
.stack-back .stack-label {{ font-family: 'Figtree', sans-serif; font-size: 0.7rem; font-weight: 700; color: #6D6558; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 10px; display: block; }}
.stack-front {{
    position: absolute; top: 55px; left: 0; width: 82%; padding: 30px 34px; border-radius: 6px 16px 16px 6px;
    background-color: {paper_bg}; border: 1px solid {paper_border}; transform: rotate(3deg);
    box-shadow: 0 20px 40px rgba(0,0,0,0.45);
}}
.stack-front::after {{
    content: ''; position: absolute; top: 0; right: 0; width: 0; height: 0;
    border-style: solid; border-width: 0 22px 22px 0; border-color: transparent #DCCEA4 transparent transparent;
}}
.stack-front .stack-label {{ font-family: 'Figtree', sans-serif; font-size: 0.7rem; font-weight: 700; color: {paper_accent}; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 10px; display: block; }}
.stack-front p {{ font-family: 'OpenDyslexic', sans-serif !important; font-size: 1rem !important; line-height: 1.75 !important; color: {paper_ink} !important; margin: 0 !important; }}
.stack-pill {{
    position: absolute; bottom: 18px; right: 6%; background-color: {accent_color}; color: #0E1117;
    font-family: 'Figtree', sans-serif; font-weight: 700; font-size: 0.78rem; padding: 7px 16px 7px 12px;
    border-radius: 20px; box-shadow: 0 8px 18px rgba(0,0,0,0.35); z-index: 5;
}}

/* --- FEATURE CARDS: color-coded by function, not a bullet dump --- */
.feature-grid {{ display: flex; gap: 20px; margin-top: 10px; }}
.feature-card {{
    flex: 1; background-color: {card_color}; border: 1px solid {border_color}; border-left: 3px solid var(--accent, {cyan_color});
    border-radius: 10px; padding: 24px 22px; transition: transform 0.2s ease, border-color 0.2s ease;
}}
.feature-card:hover {{ transform: translateY(-4px); }}
.feature-icon {{
    width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem; background-color: rgba(255,255,255,0.06); margin-bottom: 14px;
}}
.feature-card h4 {{ font-family: 'Fraunces', Georgia, serif !important; font-size: 1.08rem; margin: 0 0 8px 0 !important; color: {text_color} !important; }}
.feature-card p {{ font-size: 0.88rem; color: #9AA0A6 !important; margin: 0 !important; line-height: 1.55; }}

/* --- MISSION: editorial block with a spine, not two plain paragraphs --- */
.mission-block {{ border-left: 3px solid {cyan_color}; padding-left: 26px; }}
.mission-block .kicker {{ font-family: 'Figtree', sans-serif; font-size: 0.78rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: {accent_color}; margin-bottom: 10px; }}
.mission-block p {{ font-size: 1rem; color: #C9C0AE !important; line-height: 1.7; margin-bottom: 14px !important; }}
.mission-block p:first-of-type {{ font-family: 'Fraunces', Georgia, serif; font-size: 1.25rem; color: {text_color} !important; font-style: italic; }}

/* --- AUTH CARD: a real panel instead of bare inputs on the page --- */
.auth-card-header {{ text-align: center; margin-bottom: 22px; }}
.auth-card-header .icon-badge {{
    width: 52px; height: 52px; border-radius: 50%; background-color: rgba(0,229,255,0.12); border: 1px solid {cyan_color};
    display: flex; align-items: center; justify-content: center; font-size: 1.4rem; margin: 0 auto 14px auto;
}}
.auth-card-header h3 {{ margin: 0 0 4px 0 !important; }}
.auth-card-header p {{ color: #9AA0A6 !important; font-size: 0.9rem; margin: 0 !important; }}
.auth-card {{
    background-color: {card_color}; border: 1px solid {border_color}; border-radius: 16px; padding: 34px 38px 24px 38px;
    box-shadow: 0 14px 30px rgba(0,0,0,0.4);
}}

/* ======================================================================
   WORKSPACE (post-login) — everything below is scoped to the dashboard,
   the landing page above is untouched.
   ====================================================================== */

/* --- App shell background: subtle depth instead of flat black --- */
[data-testid="stMain"] {{
    background:
        radial-gradient(circle at 15% 0%, rgba(0,229,255,0.05) 0%, transparent 45%),
        radial-gradient(circle at 85% 10%, rgba(105,240,174,0.04) 0%, transparent 45%),
        {bg_color};
}}

/* --- Workspace top bar: greeting + live doc status, replaces the bare avatar row --- */
.ws-topbar {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 4px 4px 20px 4px; margin-bottom: 6px; border-bottom: 1px solid {border_color};
}}
.ws-greeting-eyebrow {{
    font-family: 'Figtree', sans-serif; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.12em;
    text-transform: uppercase; color: {accent_color}; margin-bottom: 4px;
}}
.ws-greeting-title {{
    font-family: 'Fraunces', Georgia, serif !important; font-size: 1.7rem; font-weight: 700 !important;
    color: {text_color} !important; margin: 0 !important; line-height: 1.2;
}}
.ws-doc-chip {{
    display: flex; align-items: center; gap: 10px; background: rgba(255,255,255,0.04);
    border: 1px solid {border_color}; border-radius: 30px; padding: 8px 18px 8px 8px;
}}
.ws-doc-chip .dot {{
    width: 30px; height: 30px; border-radius: 50%; display:flex; align-items:center; justify-content:center;
    background: rgba(0,229,255,0.14); font-size: 0.95rem; flex-shrink: 0;
}}
.ws-doc-chip .doc-meta {{ line-height: 1.15; }}
.ws-doc-chip .doc-meta .lbl {{ font-size: 0.68rem; color: #6D7280; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 700; }}
.ws-doc-chip .doc-meta .val {{ font-size: 0.86rem; color: {text_color}; font-weight: 600; max-width: 220px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}

/* --- Upload / action card: clear zones instead of default-uploader-in-a-box --- */
.upload-card {{
    background: linear-gradient(160deg, rgba(0,229,255,0.05), rgba(30,28,41,0.55) 55%);
    border: 1px solid rgba(255,255,255,0.08);
    padding: 26px 28px;
    border-radius: 18px;
    box-shadow: 0 12px 28px rgba(0,0,0,0.45);
    margin-bottom: 18px;
}}
.upload-card-head {{ display:flex; align-items:flex-start; gap:14px; margin-bottom: 4px; }}
.upload-card-head .feature-icon {{ background-color: rgba(0,229,255,0.12); }}
.upload-card-head .title {{ font-weight:600; color:#E0E0E0; margin:0 0 4px 0; font-family:'Fraunces', serif; font-size:1.08rem; }}
.upload-card-head .sub {{ color:#9AA0A6; margin:0; font-size:0.85rem; line-height:1.5; }}

/* --- Action toolbar: a real pill-shaped toolbar instead of scattered columns --- */
.toolbar-wrap {{
    background: rgba(255,255,255,0.03);
    border: 1px solid {border_color};
    border-radius: 14px;
    padding: 10px 14px;
    margin: 4px 0 22px 0;
    display: flex;
    align-items: center;
}}
.toolbar-label {{
    font-family: 'Figtree', sans-serif; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.08em;
    text-transform: uppercase; color: #6D7280; padding-left: 6px; white-space: nowrap;
}}

/* --- Content stats strip above the reading tabs --- */
.content-stats {{
    display: flex; gap: 10px; margin: 2px 0 16px 0; flex-wrap: wrap;
}}
.stat-chip {{
    background: rgba(255,255,255,0.04); border: 1px solid {border_color}; border-radius: 20px;
    padding: 6px 14px; font-size: 0.78rem; color: #9AA0A6; font-family: 'Figtree', sans-serif; font-weight: 500;
}}
.stat-chip b {{ color: {cyan_color}; font-weight: 700; }}

/* --- Sidebar: section cards instead of a flat stack of widgets --- */
[data-testid="stSidebar"] .block-container {{ padding-top: 1.2rem; }}
.sb-brand {{ display:flex; align-items:center; gap:10px; margin-bottom: 18px; }}
.sb-brand .logo-dot {{ width:30px; height:30px; border-radius:50%; background: linear-gradient(135deg, {cyan_color}, {accent_color}); flex-shrink:0; }}
.sb-brand .name {{ font-family:'Fraunces', Georgia, serif; font-style: italic; font-weight:700; font-size:1.08rem; color:#FFFFFF; }}
.sb-section-label {{
    color: #6D7280 !important; font-size: 0.72rem !important; font-weight: 700 !important; text-transform: uppercase;
    letter-spacing: 0.08em; margin: 18px 0 8px 2px; display:block; font-family: 'Figtree', sans-serif !important;
}}
[data-testid="stSidebar"] [data-testid="stFileUploader"] {{ padding: 6px; }}

/* Recent-document buttons: give the active/hover state some presence */
[data-testid="stSidebar"] button[kind="secondary"] {{
    border-radius: 8px !important; margin-bottom: 2px !important;
}}
[data-testid="stSidebar"] button[kind="secondary"]:hover {{ background-color: rgba(0,229,255,0.08) !important; }}

/* Sidebar profile footer card */
.sb-profile-card {{
    background: rgba(255,255,255,0.03); border: 1px solid {border_color}; border-radius: 12px;
    padding: 10px 12px; margin-top: 10px; display:flex; align-items:center; gap: 10px;
}}
</style>
"""
st.markdown(dynamic_css, unsafe_allow_html=True)


if not st.session_state.logged_in:
    st.markdown(f"""
        <style>
            #smooth-logo-bg {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background: linear-gradient(rgba(14, 17, 23, 0.74), rgba(14, 17, 23, 0.85)), url('{logo_src}');
                background-size: cover;
                background-position: center;
                pointer-events: none;
                z-index: 0;
                opacity: 0.85;
                transition: opacity 0.8s ease-in-out;
            }}
            #smooth-logo-bg.hidden-bg {{
                opacity: 0 !important;
            }}
        </style>
        
        <div id="smooth-logo-bg"></div>
        
        <script>
            (function() {{
                const bgDiv = document.getElementById("smooth-logo-bg");
                const targetWin = window.parent !== window ? window.parent : window;
                
                function handleScroll() {{
                    const scrollPos = targetWin.scrollY || window.scrollY || document.documentElement.scrollTop || 0;
                    if (bgDiv) {{
                        if (scrollPos > 40) {{
                            bgDiv.classList.add("hidden-bg");
                        }} else {{
                            bgDiv.classList.remove("hidden-bg");
                        }}
                    }}
                }}
                
                targetWin.addEventListener('scroll', handleScroll, {{ passive: true }});
                window.addEventListener('scroll', handleScroll, {{ passive: true }});
                handleScroll();
            }})();
        </script>
    """, unsafe_allow_html=True)

    top_bar_container = st.container()
    with top_bar_container:
        st.markdown(f"""
            <style>
                .custom-top-bar {{
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 80px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 0 50px;
                    background-color: rgba(14, 17, 23, 0.45);
                    backdrop-filter: blur(16px);
                    -webkit-backdrop-filter: blur(16px);
                    border-bottom: 1px solid rgba(51, 47, 63, 0.4);
                    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.15);
                    z-index: 999999;
                }}
                .nav-left-side {{
                    display: flex;
                    align-items: center;
                }}
                .nav-brand-title {{
                    font-family: 'Fraunces', Georgia, serif;
                    font-size: 2.1rem;
                    font-weight: 700;
                    font-style: italic;
                    letter-spacing: 0.5px;
                    background: linear-gradient(135deg, #FFFFFF 30%, #00E5FF 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }}
                .nav-login-link {{
                    background-color: transparent;
                    color: #00E5FF !important;
                    border: 1.5px solid #00E5FF;
                    padding: 8px 24px;
                    border-radius: 25px;
                    text-decoration: none !important;
                    font-family: 'Figtree', sans-serif;
                    font-size: 1rem;
                    font-weight: 600;
                    transition: all 0.25s ease;
                }}
                .nav-login-link:hover {{
                    background-color: #00E5FF;
                    color: #0E1117 !important;
                    box-shadow: 0 0 18px rgba(0, 229, 255, 0.5);
                    transform: translateY(-2px);
                }}
            </style>
            <div class="custom-top-bar">
                <div class="nav-left-side">
                    <span class="nav-brand-title">Readora AI</span>
                </div>
                <div>
                    <a href="#login-section" class="nav-login-link">Log In</a>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<div style='height: 90px;'></div>", unsafe_allow_html=True)

    hero_col1, hero_col2 = st.columns([1.05, 1], gap="large")
    with hero_col1:
        st.markdown("""
        <div class="hero-copy">
            <div class="hero-eyebrow">For dyslexic, ADHD &amp; neurodivergent readers</div>
            <h1>Your brain isn't behind the AI curve.<br>It's been <em>ahead</em> of it for years.</h1>
            <p>Readora rewrites dense, academic text into short, plain-language sentences — set in a dyslexia-friendly typeface, at your pace, with your spacing.</p>
            <a href="#login-section" class="cta-btn">Try the live demo →</a>
            <div class="cta-sub">No credit card. Two minutes to your first simplified page.</div>
        </div>
        """, unsafe_allow_html=True)

    with hero_col2:
        st.markdown("""
        <div class="stack-wrap">
            <div class="stack-back">
                <span class="stack-label">Original textbook</span>
                <p>Photosynthesis is a process used by plants and other organisms to convert light energy into chemical energy that, through cellular respiration, can later be released to fuel the organism's activities.</p>
            </div>
            <div class="stack-front">
                <span class="stack-label">Readora</span>
                <p>Plants use sunlight to make their own food.<br><br>They store it as sugar, then use it later to grow.</p>
            </div>
            <div class="stack-pill">✨ Simplified in 4s</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    st.markdown("<h2 style='margin-bottom: 6px;'>Built for neurodivergent minds</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #9AA0A6; margin-bottom: 26px;'>Three things happen to your document the moment it lands in Readora.</p>", unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card" style="--accent: #00E5FF; border-left-color: #00E5FF;">
            <div class="feature-icon" style="color:#00E5FF;">📄</div>
            <h4>Reads how you read</h4>
            <p>OpenDyslexic type, wide letter spacing, and adjustable line height replace the dense default layout of the source PDF.</p>
        </div>
        <div class="feature-card" style="--accent: #B5651D; border-left-color: #B5651D;">
            <div class="feature-icon" style="color:#B5651D;">✨</div>
            <h4>Rewrites the concepts</h4>
            <p>Abstract, jargon-heavy paragraphs are broken into short, literal sentences — with a plain-language vocabulary list alongside.</p>
        </div>
        <div class="feature-card" style="--accent: #69F0AE; border-left-color: #69F0AE;">
            <div class="feature-icon" style="color:#69F0AE;">🔊</div>
            <h4>Reads it out loud</h4>
            <p>Word-by-word highlighted narration for anyone who processes audio and text together better than text alone.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

    mission_col, spacer_col = st.columns([1.4, 1])
    with mission_col:
        st.markdown("""
        <div class="mission-block">
            <div class="kicker">Who's building this</div>
            <p>Most reading tools force the student to adapt to the technology.</p>
            <p>We're the UI engineering team from NSUT CSAI, building this <em>with</em> neurodivergent users, not just for them — so the AI adapts to the student instead, giving them a low-sensory space to process complex material at their own speed.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown('<div id="login-section" style="padding-top: 60px; margin-top: -60px;"></div>', unsafe_allow_html=True)
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    _, auth_col, _ = st.columns([1, 1.1, 1])
    with auth_col:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.markdown("""
        <div class="auth-card-header">
            <div class="icon-badge">🔑</div>
            <h3>Access the app</h3>
            <p>Log in to pick up where you left off, or create an account.</p>
        </div>
        """, unsafe_allow_html=True)

        log_user = st.text_input("Username")
        log_pass = st.text_input("Password", type="password")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Log In", type="primary", use_container_width=True):
                c.execute('SELECT * FROM users WHERE username=? AND password=?', (log_user, log_pass))
                if c.fetchone():
                    st.session_state.logged_in = True
                    st.session_state.username = log_user
                    st.rerun()
                else:
                    st.toast("Invalid credentials. Please try again.", icon="🚨")
        with c2:
            if st.button("Sign Up", use_container_width=True):
                if log_user and log_pass:
                    c.execute('INSERT INTO users VALUES (?, ?)', (log_user, log_pass))
                    conn.commit()
                    st.toast("Account created! You can now log in.", icon="✅")
        
        st.markdown("<div style='text-align: center; margin: 20px 0; color: #5A5E73; font-size: 0.9rem;'>OR</div>", unsafe_allow_html=True)
        
        if st.button("🌐 Continue with Google", use_container_width=True):
            st.toast("Google OAuth integration coming soon!", icon="ℹ️")
        st.markdown('</div>', unsafe_allow_html=True)

    footer_html = """
    <div class="mega-footer">
        <div class="footer-col">
            <h4>Get to Know Us</h4>
            <a href="#">About Readora AI</a>
            <a href="#">Our Team at NSUT</a>
            <a href="#">Hackathon Mission</a>
            <a href="#">Press Releases</a>
        </div>
        <div class="footer-col">
            <h4>Connect with Us</h4>
            <a href="#">GitHub Repository</a>
            <a href="#">Twitter / X</a>
            <a href="#">Instagram</a>
            <a href="#">LinkedIn</a>
        </div>
        <div class="footer-col">
            <h4>Resources</h4>
            <a href="#">Dyslexia Support</a>
            <a href="#">ADHD Tools</a>
            <a href="#">Accessibility Guide</a>
            <a href="#">API Documentation</a>
        </div>
        <div class="footer-col">
            <h4>Legal & Help</h4>
            <a href="#">Your Account</a>
            <a href="#">Privacy Policy</a>
            <a href="#">Terms of Service</a>
            <a href="#">Help Center</a>
        </div>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)

else:
    # ---------------------------------------------------------------
    # WORKSPACE TOP BAR — greeting + live status of the current doc.
    # (Account settings now live only in the sidebar popover below —
    # having the same "Account Settings" popover in two places was
    # redundant and is why this used to feel cluttered.)
    # ---------------------------------------------------------------
    active_doc_name = st.session_state.get('last_uploaded_file')
    if active_doc_name:
        doc_status_label, doc_status_val = "Current document", (active_doc_name[:28] + '…') if len(active_doc_name) > 28 else active_doc_name
        doc_icon = "📄"
    else:
        doc_status_label, doc_status_val = "Current document", "None loaded yet"
        doc_icon = "📥"

    st.markdown(f"""
    <div class="ws-topbar">
        <div>
            <div class="ws-greeting-eyebrow">Workspace</div>
            <h2 class="ws-greeting-title">Welcome back, {st.session_state.username.lower()}</h2>
        </div>
        <div class="ws-doc-chip">
            <div class="dot">{doc_icon}</div>
            <div class="doc-meta">
                <div class="lbl">{doc_status_label}</div>
                <div class="val">{doc_status_val}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("""
        <div class="sb-brand">
            <div class="logo-dot"></div>
            <span class="name">Readora AI</span>
        </div>
        """, unsafe_allow_html=True)

        st.text_input("Search", placeholder="🔍 Search documents...", label_visibility="collapsed")

        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
        if st.button("✨ New Chat Session", use_container_width=True, type="primary"):
            st.session_state.extracted_text = ""
            st.session_state.simplified_text = ""
            st.session_state.last_uploaded_file = None
            st.session_state.current_doc_id = None
            st.rerun()

        st.markdown("<span class='sb-section-label'>Recent Documents</span>", unsafe_allow_html=True)

        c.execute("SELECT id, doc_name, original_text, simplified_text FROM documents WHERE username=? ORDER BY id DESC", (st.session_state.username,))
        user_history = c.fetchall()

        with st.container(height=260):
            if not user_history:
                st.markdown("<span style='color: #5A5E73; font-size: 0.85rem;'>No documents yet — upload a PDF to get started.</span>", unsafe_allow_html=True)
            else:
                for doc in user_history:
                    doc_id, doc_name, orig_text, simp_text = doc
                    display_name = (doc_name[:22] + '…') if len(doc_name) > 22 else doc_name
                    is_active = st.session_state.get('current_doc_id') == doc_id
                    icon = "🟢" if is_active else "📄"
                    if st.button(f"{icon} {display_name}", key=f"hist_{doc_id}", use_container_width=True):
                        st.session_state.current_doc_id = doc_id
                        st.session_state.last_uploaded_file = doc_name
                        st.session_state.extracted_text = orig_text
                        st.session_state.simplified_text = simp_text
                        st.rerun()

        st.markdown("<span class='sb-section-label'>Visual Settings</span>", unsafe_allow_html=True)
        st.session_state.font_size = st.slider("🔤 Font Size", 14, 48, st.session_state.get('font_size', 22))
        st.session_state.line_spacing = st.slider("↕️ Line Spacing", 1.0, 4.0, st.session_state.get('line_spacing', 1.8), step=0.1)

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

        initial = st.session_state.username[0].upper() if st.session_state.username else "U"
        if st.session_state.get('profile_photo'):
            b64_img = base64.b64encode(st.session_state.profile_photo).decode()
            avatar_html = f'<img src="data:image/jpeg;base64,{b64_img}" style="width: 34px; height: 34px; border-radius: 50%; object-fit: cover;">'
        else:
            avatar_html = f'<div style="width: 34px; height: 34px; border-radius: 50%; background-color: #00E5FF; color: #0E1117; display: flex; justify-content: center; align-items: center; font-weight: 700; font-family: \'Figtree\', sans-serif; font-size: 14px; flex-shrink:0;">{initial}</div>'

        display_name = st.session_state.username.lower() if st.session_state.username else "user"

        st.markdown(f"""
        <div class="sb-profile-card">
            {avatar_html}
            <div style="line-height: 1.15; flex:1;">
                <div style="font-weight: 600; color: #E0E0E0; font-size: 13.5px;">{display_name}</div>
                <div style="font-size: 11px; color: #00E5FF;">Free Plan</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        pop_col, log_col = st.columns([7, 3])
        with pop_col:
            with st.popover("⚙️ Settings & Profile", use_container_width=True):
                st.markdown("##### Account Settings")
                m_tab1, m_tab2 = st.tabs(["👤 Profile", "❓ Help"])

                with m_tab1:
                    if st.session_state.get('profile_photo'):
                        b64_img = base64.b64encode(st.session_state.profile_photo).decode()
                        st.markdown(f'<img src="data:image/jpeg;base64,{b64_img}" style="width: 80px; height: 80px; border-radius: 50%; object-fit: cover; margin-bottom: 10px;">', unsafe_allow_html=True)
                        if st.button("🗑️ Delete Photo", use_container_width=True):
                            st.session_state.profile_photo = None
                            st.rerun()
                    else:
                        uploaded_img = st.file_uploader("Upload Profile Photo", type=["jpg", "png", "jpeg"])
                        if uploaded_img:
                            st.session_state.profile_photo = uploaded_img.getvalue()
                            st.rerun()

                    st.text_input("Name")
                    st.text_input("Surname")
                    st.text_area("Preferences for AI", placeholder="E.g., Keep sentences short, I prefer bullets...")

                with m_tab2:
                    st.info("Support: help@readora.ai")
        with log_col:
            st.button("🚪 Out", use_container_width=True, help="Log Out",
                       on_click=lambda: st.session_state.update(logged_in=False))

    # Wrapped inside upload card container
    st.markdown('<div class="upload-card">', unsafe_allow_html=True)

    upload_intro_col, upload_drop_col = st.columns([1, 1.3], gap="large")
    with upload_intro_col:
        st.markdown("""
        <div class="upload-card-head">
            <div class="feature-icon" style="color:#00E5FF; flex-shrink:0;">📥</div>
            <div>
                <p class="title">Bring in a document</p>
                <p class="sub">PDF only, for now. It's extracted, simplified, and saved to your workspace history automatically.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with upload_drop_col:
        uploaded_file = st.file_uploader("Drop your reading material here (PDF)", type=['pdf'], label_visibility="collapsed")

    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_file is not None:
        if st.session_state.get('last_uploaded_file') != uploaded_file.name:
            status_placeholder = st.empty()
            status_placeholder.info("⏳ Extracting text from PDF via FastAPI...")
            
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                status_placeholder.warning("⏳ Processing document... This is taking slightly longer than usual due to file size or complexity.")
                
                response = requests.post(f"{BACKEND_URL}/upload", files=files)
                status_placeholder.empty()
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.extracted_text = data.get("text", "")
                    st.session_state.last_uploaded_file = uploaded_file.name
                    st.session_state.simplified_text = ""
                    st.session_state.vocabulary = "" 
                    
                    c.execute("INSERT INTO documents (username, doc_name, original_text, simplified_text) VALUES (?, ?, ?, ?)", 
                            (st.session_state.username, uploaded_file.name, st.session_state.extracted_text, ""))
                    conn.commit()
                    st.session_state.current_doc_id = c.lastrowid 
                    st.success("PDF processed and saved to history!")
                else:
                    st.error(f"Upload Error: {response.json().get('detail')}")
            except Exception as e:
                status_placeholder.empty()
                st.error(f"Connection Error: Could not connect to FastAPI backend on {BACKEND_URL}")
                
    st.markdown('<div class="toolbar-wrap">', unsafe_allow_html=True)
    tb_label_col, tb_btn1_col, tb_btn2_col, tb_spacer_col = st.columns([1.4, 1.6, 1.6, 3.4])
    with tb_label_col:
        st.markdown('<div class="toolbar-label">Actions</div>', unsafe_allow_html=True)
    with tb_btn1_col:
        btn_simplify = st.button("✨ Simplify Text", type="primary", use_container_width=True)
    with tb_btn2_col:
        btn_read = st.button("🔊 Read Aloud", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if btn_read:
        text_to_read = st.session_state.simplified_text if st.session_state.simplified_text else st.session_state.extracted_text
        if text_to_read:
            clean_text = text_to_read.replace('*', '').replace('#', '')
            clean_text = re.sub(r'\b\d+\.\s+', '', clean_text)
            clean_text = clean_text.replace('- ', '')
            safe_text = json.dumps(clean_text)

            player_html = f"""
            <style>
                @font-face {{ font-family: 'OpenDyslexic'; src: url('https://cdn.jsdelivr.net/gh/antijingoist/opendyslexic@master/compiled/OpenDyslexic-Regular.otf') format('opentype'); }}
                body {{ font-family: 'OpenDyslexic', sans-serif; background-color: {paper_bg}; color: {paper_ink}; padding: 24px 28px; border-radius: 12px; margin: 0; border: 1px solid {paper_border}; }}
                .highlight {{ background-color: {cyan_color}; color: #0E1117; font-weight: bold; border-radius: 4px; padding: 2px 4px; box-shadow: 0 0 8px rgba(0,229,255,0.5); transition: background-color 0.1s ease; }}
                #progress-container {{ width: 100%; background-color: {paper_border}; border-radius: 8px; margin-bottom: 20px; height: 10px; overflow: hidden; }}
                #progress-bar {{ width: 0%; height: 100%; background-color: {accent_color}; transition: width 0.1s linear; }}
                .controls {{ margin-bottom: 20px; display: flex; gap: 15px; align-items: center; font-family: 'Segoe UI', sans-serif; }}
                button {{ background-color: {cyan_color}; color: #0E1117; border: none; padding: 8px 16px; border-radius: 20px; font-family: 'Segoe UI', sans-serif; font-weight: bold; cursor: pointer; transition: 0.2s; }}
                button:hover {{ background-color: {accent_color}; }}
                #status {{ font-family: 'Segoe UI', sans-serif; }}
            </style>
            
            <div id="progress-container"><div id="progress-bar"></div></div>
            <div class="controls">
                <button id="play-pause-btn" onclick="togglePlayPause()">⏸️ Pause Reading</button>
                <span id="status" style="color: #4E7A67; font-weight: bold;">🔊 Speaking...</span>
            </div>
            <div id="text-display" style="font-size: 22px; line-height: 1.8;"></div>

            <script>
                const rawText = {safe_text};
                const display = document.getElementById("text-display");
                const progressBar = document.getElementById("progress-bar");
                const status = document.getElementById("status");
                const playPauseBtn = document.getElementById("play-pause-btn");

                const words = rawText.split(/(\\s+)/); 
                display.innerHTML = words.map((w, i) => `<span id="word-${{i}}">${{w}}</span>`).join('');

                const synth = window.parent.speechSynthesis || window.speechSynthesis;
                synth.cancel();

                let msg = new SpeechSynthesisUtterance(rawText);
                msg.lang = 'en-US';
                msg.rate = 0.9; 

                msg.onboundary = (event) => {{
                    if(event.name === 'word') {{
                        const pct = (event.charIndex / rawText.length) * 100;
                        progressBar.style.width = pct + "%";

                        let charCount = 0;
                        for (let i = 0; i < words.length; i++) {{
                            charCount += words[i].length;
                            if (charCount > event.charIndex) {{
                                document.querySelectorAll('.highlight').forEach(el => el.classList.remove('highlight'));
                                const activeWord = document.getElementById(`word-${{i}}`);
                                if(activeWord && activeWord.innerText.trim().length > 0) {{
                                    activeWord.classList.add('highlight');
                                }}
                                break;
                            }}
                        }}
                    }}
                }};

                msg.onend = () => {{
                    progressBar.style.width = "100%";
                    status.innerText = "✅ Finished";
                    playPauseBtn.style.display = "none"; 
                    document.querySelectorAll('.highlight').forEach(el => el.classList.remove('highlight'));
                }};

                synth.speak(msg);

                function togglePlayPause() {{
                    if (synth.paused) {{
                        synth.resume();
                        playPauseBtn.innerText = "⏸️ Pause Reading";
                        status.innerText = "🔊 Speaking...";
                    }} else if (synth.speaking) {{
                        synth.pause();
                        playPauseBtn.innerText = "▶️ Resume Reading";
                        status.innerText = "⏸️ Paused";
                    }}
                }}
            </script>
            """
            st.markdown("### 🎧 Interactive Reader")
            components.html(player_html, height=400, scrolling=True)
            st.markdown("---")
        else:
            st.warning("Please upload a PDF or generate simplified text first!")

    if btn_simplify:
        if st.session_state.extracted_text and st.session_state.extracted_text.strip():
            with st.spinner("Readora AI is breaking down complex concepts..."):
                try:
                    payload = {"text": st.session_state.extracted_text}
                    response = requests.post(f"{BACKEND_URL}/simplify", json=payload)
                
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.simplified_text = data.get("simplified_text", "")
                        st.session_state.vocabulary = data.get("vocabulary", "") 
                    
                        if st.session_state.current_doc_id:
                            c.execute("UPDATE documents SET simplified_text = ? WHERE id = ?", 
                                    (st.session_state.simplified_text, st.session_state.current_doc_id))
                            conn.commit()
                        
                        st.toast("Text simplified and saved to history!", icon="✨")
                        st.rerun() 
                    else:
                        st.error(f"Simplification Error: {response.json().get('detail')}")
                except Exception as e:
                    st.error(f"Connection Error: Could not connect to FastAPI backend on {BACKEND_URL}")
        elif uploaded_file is not None:
            st.warning("⚠️ The PDF uploaded, but the backend couldn't extract any words. Check the 'Original PDF Text' tab below to verify it's blank.")
        else:
            st.warning("Please upload a PDF document first!")

    st.markdown(f"""
    <style>
        .reading-pane, .reading-pane p, .reading-pane li, .reading-pane span {{
            font-size: {st.session_state.get('font_size', 22)}px !important;
            line-height: {st.session_state.get('line_spacing', 1.8)} !important;
        }}
    </style>
    """, unsafe_allow_html=True)

    word_count = len(st.session_state.extracted_text.split()) if st.session_state.extracted_text else 0
    simplified_ready = bool(st.session_state.simplified_text)
    st.markdown(f"""
    <div class="content-stats">
        <div class="stat-chip">📄 <b>{word_count:,}</b> words extracted</div>
        <div class="stat-chip">✨ Simplified: <b>{"Ready" if simplified_ready else "Not yet"}</b></div>
        <div class="stat-chip">🔤 Font <b>{st.session_state.get('font_size', 22)}px</b></div>
        <div class="stat-chip">↕️ Spacing <b>{st.session_state.get('line_spacing', 1.8)}</b></div>
    </div>
    """, unsafe_allow_html=True)

    custom_text_style = ""

    tab1, tab2, tab3 = st.tabs(["✨ AI Simplified", "📚 Key Vocabulary", "📄 Original PDF Text"])
    
    with tab1:
        st.markdown('<div class="reading-container">', unsafe_allow_html=True)
        if st.session_state.simplified_text:
            st.markdown('<div class="badge">AI Output</div>', unsafe_allow_html=True)
            parsed_html = markdown.markdown(st.session_state.simplified_text)
            st.markdown(f'<div class="reading-pane" style="{custom_text_style}">{parsed_html}</div>', unsafe_allow_html=True)
        else:
            st.info("Upload a PDF and click '✨ Simplify Text' to generate a neurodivergent-friendly version.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="reading-container">', unsafe_allow_html=True)
        if st.session_state.get('vocabulary'):
            st.markdown('<div class="badge">Vocabulary List</div>', unsafe_allow_html=True)
            parsed_vocab_html = markdown.markdown(st.session_state.vocabulary)
            st.markdown(f'<div class="reading-pane" style="{custom_text_style}">{parsed_vocab_html}</div>', unsafe_allow_html=True)
        else:
            st.info("Click '✨ Simplify Text' to generate a vocabulary breakdown.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="reading-container">', unsafe_allow_html=True)
        if st.session_state.extracted_text:
            st.markdown('<div class="badge">Raw Extraction</div>', unsafe_allow_html=True)
            parsed_raw_html = markdown.markdown(st.session_state.extracted_text)
            st.markdown(f'<div class="reading-pane" style="{custom_text_style}">{parsed_raw_html}</div>', unsafe_allow_html=True)
        else:
            st.info("Your original document text will appear here.")
        st.markdown('</div>', unsafe_allow_html=True)